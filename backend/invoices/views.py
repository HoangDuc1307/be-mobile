from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UnitPrice, Invoice, BankInfo
from .serializers import (
    UnitPriceSerializer, InvoiceSerializer,
    BankInfoSerializer, InvoiceHistorySerializer,
)
from rooms.models import Room, RoomTenant


class UnitPriceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền truy cập đơn giá'}, status=status.HTTP_403_FORBIDDEN)
        unit_price, _ = UnitPrice.objects.get_or_create(
            owner=request.user,
            defaults={'electricity_price': 3500, 'water_price': 15000, 'common_service_fee': 100000}
        )
        return Response(UnitPriceSerializer(unit_price).data)

    def post(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền chỉnh sửa đơn giá'}, status=status.HTTP_403_FORBIDDEN)
        unit_price, _ = UnitPrice.objects.get_or_create(owner=request.user)
        serializer = UnitPriceSerializer(unit_price, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_owner():
            invoices = Invoice.objects.all().order_by('-created_at')
        else:
            invoices = Invoice.objects.filter(
                room__current_tenant__tenant=request.user,
                room__current_tenant__is_active=True
            ).order_by('-created_at')
        return Response(InvoiceSerializer(invoices, many=True).data)

    def post(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền tạo hóa đơn'}, status=status.HTTP_403_FORBIDDEN)

        room_id = request.data.get('room')
        try:
            room = Room.objects.get(id=room_id)
        except (Room.DoesNotExist, ValueError, TypeError):
            return Response({'error': 'Phòng không tồn tại'}, status=status.HTTP_404_NOT_FOUND)

        unit_price, _ = UnitPrice.objects.get_or_create(
            owner=request.user,
            defaults={'electricity_price': 3500, 'water_price': 15000, 'common_service_fee': 100000}
        )

        try:
            month              = int(request.data.get('month'))
            year               = int(request.data.get('year'))
            room_price         = float(request.data.get('room_price', room.price))
            electricity_usage  = int(request.data.get('electricity_usage', 0))
            water_usage        = int(request.data.get('water_usage', 0))
            service_price      = float(request.data.get('service_price', unit_price.common_service_fee))
        except (ValueError, TypeError):
            return Response({'error': 'Dữ liệu không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

        total_electric = electricity_usage * unit_price.electricity_price
        total_water    = water_usage       * unit_price.water_price
        grand_total    = room_price + float(total_electric) + float(total_water) + service_price

        invoice = Invoice.objects.create(
            room=room, month=month, year=year,
            room_price=room_price,
            electricity_usage=electricity_usage,
            water_usage=water_usage,
            service_price=service_price,
            electricity_price=unit_price.electricity_price,
            water_price=unit_price.water_price,
            total_electric=total_electric,
            total_water=total_water,
            grand_total=grand_total,
        )
        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)


class InvoiceCurrentUnpaidView(APIView):
    """
    GET /api/invoices/current-unpaid/
    Returns the latest unpaid invoice for the tenant, bank info, and payment history.
    Used by PaymentNotificationActivity.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            room_tenant = RoomTenant.objects.get(tenant=request.user, is_active=True)
        except RoomTenant.DoesNotExist:
            return Response({'error': 'Bạn chưa thuê phòng nào'}, status=404)

        room = room_tenant.room
        invoice = Invoice.objects.filter(room=room, is_paid=False).order_by('-year', '-month').first()
        if not invoice:
            return Response({'error': 'Không có hóa đơn chưa thanh toán'}, status=404)

        bank  = BankInfo.objects.filter(is_active=True).first()
        history = Invoice.objects.filter(room=room, is_paid=True).order_by('-year', '-month')[:5]

        return Response({
            'invoice':         InvoiceSerializer(invoice).data,
            'bank_info':       BankInfoSerializer(bank).data if bank else {},
            'payment_history': InvoiceHistorySerializer(history, many=True).data,
        })
