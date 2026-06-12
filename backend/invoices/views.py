from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UnitPrice, Invoice
from .serializers import UnitPriceSerializer, InvoiceSerializer
from rooms.models import Room

class UnitPriceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền truy cập đơn giá'}, status=status.HTTP_403_FORBIDDEN)
        
        # Lấy hoặc tạo đơn giá mặc định cho chủ trọ này
        unit_price, created = UnitPrice.objects.get_or_create(
            owner=request.user,
            defaults={
                'electricity_price': 3500,
                'water_price': 15000,
                'common_service_fee': 100000
            }
        )
        serializer = UnitPriceSerializer(unit_price)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền chỉnh sửa đơn giá'}, status=status.HTTP_403_FORBIDDEN)
        
        unit_price, created = UnitPrice.objects.get_or_create(owner=request.user)
        serializer = UnitPriceSerializer(unit_price, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Nếu là chủ trọ: xem tất cả hóa đơn của các phòng
        if request.user.is_owner():
            invoices = Invoice.objects.all().order_by('-created_at')
        # Nếu là khách thuê: xem hóa đơn của các phòng mình đang thuê
        else:
            invoices = Invoice.objects.filter(
                room__current_tenant__tenant=request.user,
                room__current_tenant__is_active=True
            ).order_by('-created_at')
        
        serializer = InvoiceSerializer(invoices, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền tạo hóa đơn'}, status=status.HTTP_403_FORBIDDEN)
        
        room_id = request.data.get('room')
        try:
            room = Room.objects.get(id=room_id)
        except (Room.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Phòng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

        # Lấy đơn giá của chủ trọ để tính toán
        unit_price, _ = UnitPrice.objects.get_or_create(
            owner=request.user,
            defaults={
                'electricity_price': 3500,
                'water_price': 15000,
                'common_service_fee': 100000
            }
        )

        try:
            month = int(request.data.get('month'))
            year = int(request.data.get('year'))
            room_price = float(request.data.get('room_price', room.price))
            electricity_usage = int(request.data.get('electricity_usage', 0))
            water_usage = int(request.data.get('water_usage', 0))
            service_price = float(request.data.get('service_price', unit_price.common_service_fee))
        except (ValueError, TypeError) as e:
            return Response({'error': 'Dữ liệu không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

        # Tính toán hóa đơn
        total_electric = electricity_usage * unit_price.electricity_price
        total_water = water_usage * unit_price.water_price

        grand_total = room_price + float(total_electric) + float(total_water) + service_price

        # Lưu hóa đơn
        invoice = Invoice.objects.create(
            room=room,
            month=month,
            year=year,
            room_price=room_price,
            electricity_usage=electricity_usage,
            water_usage=water_usage,
            service_price=service_price,
            electricity_price=unit_price.electricity_price,
            water_price=unit_price.water_price,
            total_electric=total_electric,
            total_water=total_water,
            grand_total=grand_total
        )

        serializer = InvoiceSerializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
