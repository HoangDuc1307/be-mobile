from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .models import UnitPrice, Invoice, BankInfo
from .serializers import (
    UnitPriceSerializer, InvoiceSerializer,
    BankInfoSerializer, InvoiceHistorySerializer,
    PendingPaymentSerializer,
)
from rooms.models import Room, RoomTenant
from notifications.models import Notification


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
            invoices = Invoice.objects.all()
        else:
            invoices = Invoice.objects.filter(
                room__current_tenant__tenant=request.user,
                room__current_tenant__is_active=True
            )

        month   = request.query_params.get('month')
        year    = request.query_params.get('year')
        is_paid = request.query_params.get('is_paid')

        if month:
            invoices = invoices.filter(month=int(month))
        if year:
            invoices = invoices.filter(year=int(year))
        if is_paid is not None and is_paid != '':
            invoices = invoices.filter(is_paid=(is_paid.lower() == 'true'))

        return Response(InvoiceSerializer(invoices.order_by('-created_at'), many=True).data)

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

        # Create notification for tenant
        room_tenant = RoomTenant.objects.filter(room=room, is_active=True).order_by('-id').first()
        if room_tenant:
            Notification.objects.create(
                tenant=room_tenant.tenant,
                title=f'Hóa đơn mới - {room.name}',
                body=f'Hóa đơn tháng {month}/{year} cho phòng {room.name} đã được tạo. Số tiền thanh toán: {int(grand_total):,} VNĐ',
                notif_type='new_invoice',
                invoice_id=invoice.id,
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
        room_tenant = RoomTenant.objects.filter(
            tenant=request.user, is_active=True
        ).order_by('-id').first()
        if not room_tenant:
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


class SubmitPaymentView(APIView):
    """
    POST /api/invoices/{invoice_id}/submit-payment/
    Tenant upload ảnh minh chứng thanh toán.
    """
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request, invoice_id):
        if request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=status.HTTP_403_FORBIDDEN)

        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            return Response({'error': 'Không tìm thấy hóa đơn'}, status=status.HTTP_404_NOT_FOUND)

        room_tenant = RoomTenant.objects.filter(
            tenant=request.user, is_active=True
        ).order_by('-id').first()
        if not room_tenant:
            return Response({'error': 'Bạn chưa thuê phòng nào'}, status=status.HTTP_403_FORBIDDEN)

        if invoice.room != room_tenant.room:
            return Response({'error': 'Hóa đơn không thuộc phòng của bạn'}, status=status.HTTP_403_FORBIDDEN)

        if invoice.payment_status == 'pending':
            return Response({'error': 'Đang chờ xác nhận, vui lòng đợi'}, status=status.HTTP_400_BAD_REQUEST)
        if invoice.is_paid or invoice.payment_status == 'approved':
            return Response({'error': 'Hóa đơn đã được thanh toán'}, status=status.HTTP_400_BAD_REQUEST)

        proof = request.FILES.get('payment_proof')
        if not proof:
            return Response({'error': 'Vui lòng upload ảnh minh chứng'}, status=status.HTTP_400_BAD_REQUEST)

        invoice.payment_proof  = proof
        invoice.payment_status = 'pending'
        invoice.save()

        return Response({'message': 'Đã gửi xác nhận thanh toán, vui lòng chờ duyệt'})


class PendingPaymentsView(APIView):
    """
    GET /api/invoices/pending-payments/
    Owner xem danh sách hóa đơn đang chờ duyệt kèm ảnh minh chứng.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=status.HTTP_403_FORBIDDEN)

        invoices = Invoice.objects.filter(payment_status='pending').order_by('-updated_at')
        return Response(PendingPaymentSerializer(invoices, many=True, context={'request': request}).data)


class ApprovePaymentView(APIView):
    """
    POST /api/invoices/{invoice_id}/approve/
    Owner duyệt thanh toán → is_paid=True, gửi notification cho tenant.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, invoice_id):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=status.HTTP_403_FORBIDDEN)

        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            return Response({'error': 'Không tìm thấy hóa đơn'}, status=status.HTTP_404_NOT_FOUND)

        if invoice.payment_status != 'pending':
            return Response({'error': 'Hóa đơn không ở trạng thái chờ duyệt'}, status=status.HTTP_400_BAD_REQUEST)

        invoice.payment_status = 'approved'
        invoice.is_paid        = True
        invoice.save()

        room_tenant = RoomTenant.objects.filter(
            room=invoice.room, is_active=True
        ).order_by('-id').first()
        if room_tenant:
            Notification.objects.create(
                tenant=room_tenant.tenant,
                title='Thanh toán thành công',
                body=f'Hóa đơn tháng {invoice.month}/{invoice.year} phòng {invoice.room.name} đã được xác nhận.',
                notif_type='payment_success',
                invoice_id=invoice.id,
            )

        return Response({'message': 'Đã duyệt thanh toán'})


class RejectPaymentView(APIView):
    """
    POST /api/invoices/{invoice_id}/reject/
    Owner từ chối → gửi notification cho tenant để nộp lại.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, invoice_id):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=status.HTTP_403_FORBIDDEN)

        try:
            invoice = Invoice.objects.get(id=invoice_id)
        except Invoice.DoesNotExist:
            return Response({'error': 'Không tìm thấy hóa đơn'}, status=status.HTTP_404_NOT_FOUND)

        if invoice.payment_status != 'pending':
            return Response({'error': 'Hóa đơn không ở trạng thái chờ duyệt'}, status=status.HTTP_400_BAD_REQUEST)

        invoice.payment_status = 'rejected'
        invoice.save()

        room_tenant = RoomTenant.objects.filter(
            room=invoice.room, is_active=True
        ).order_by('-id').first()
        if room_tenant:
            Notification.objects.create(
                tenant=room_tenant.tenant,
                title='Thanh toán không thành công',
                body=f'Hóa đơn tháng {invoice.month}/{invoice.year} phòng {invoice.room.name} bị từ chối. Vui lòng kiểm tra lại và gửi lại minh chứng.',
                notif_type='payment_rejected',
                invoice_id=invoice.id,
            )

        return Response({'message': 'Đã từ chối thanh toán'})
