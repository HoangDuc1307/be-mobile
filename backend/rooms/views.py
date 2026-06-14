from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Room, RoomTenant
from .serializers import RoomSerializer, ContractSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class RoomListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_owner():
            rooms = Room.objects.all()
        else:
            rooms = Room.objects.filter(
                current_tenant__tenant=request.user,
                current_tenant__is_active=True
            )
        return Response(RoomSerializer(rooms, many=True).data)

    def post(self, request):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=403)
        serializer = RoomSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data, status=201)


class AvailableRoomListView(APIView):
    """List of rooms with status='available' — for browsing tenants."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.filter(status='available').order_by('name')
        return Response(RoomSerializer(rooms, many=True).data)


class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=404)
        return Response(RoomSerializer(room).data)

    def put(self, request, room_id):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=403)
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=404)
        serializer = RoomSerializer(room, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, room_id):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=403)
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=404)
        if RoomTenant.objects.filter(room=room, is_active=True).exists():
            return Response({'error': 'Không thể xóa phòng đang có người thuê'}, status=400)
        room.delete()
        return Response({'message': 'Xóa phòng thành công'}, status=204)


class TenantRoomView(APIView):
    """Dashboard data for TenantMainActivity."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            room_tenant = RoomTenant.objects.select_related('room', 'tenant').get(
                tenant=request.user, is_active=True
            )
        except RoomTenant.DoesNotExist:
            return Response({'error': 'Bạn chưa được gán vào phòng nào'}, status=404)

        room = room_tenant.room

        # Unpaid invoices total
        from invoices.models import Invoice, BankInfo
        unpaid_qs    = Invoice.objects.filter(room=room, is_paid=False)
        unpaid_total = sum(inv.grand_total for inv in unpaid_qs)
        unpaid_count = unpaid_qs.count()

        # Landlord info — newest superuser (the one created via test_data has full_name/phone)
        owner = User.objects.filter(is_superuser=True, full_name__isnull=False).exclude(full_name='').first() \
                or User.objects.filter(is_superuser=True).last()
        landlord = {
            'full_name': (owner.full_name or owner.username) if owner else 'Chủ nhà',
            'phone':     owner.phone if owner else '',
            'email':     owner.email if owner else '',
        }

        # Bank info
        bank = BankInfo.objects.filter(is_active=True).first()
        bank_info = {
            'bank_name':      bank.bank_name      if bank else '',
            'account_number': bank.account_number if bank else '',
            'account_name':   bank.account_name   if bank else '',
        }

        return Response({
            'room':          RoomSerializer(room).data,
            'unpaid_total':  str(unpaid_total),
            'unpaid_count':  unpaid_count,
            'landlord':      landlord,
            'bank_info':     bank_info,
        })


class TenantContractView(APIView):
    """Contract info for ContractActivity."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            room_tenant = RoomTenant.objects.get(tenant=request.user, is_active=True)
        except RoomTenant.DoesNotExist:
            return Response({'error': 'Bạn chưa có hợp đồng nào'}, status=404)
        return Response(ContractSerializer(room_tenant).data)


class AssignTenantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=403)

        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=404)

        if room.status == 'occupied':
            return Response({'error': 'Phòng đã có người thuê'}, status=400)

        name            = request.data.get('name', '').strip()
        phone           = request.data.get('phone', '').strip()
        id_card         = request.data.get('id_card', '').strip()
        move_in         = request.data.get('move_in')
        deposit         = request.data.get('deposit', 0)
        duration_months = request.data.get('duration_months', 12)

        if not phone:
            return Response({'error': 'Số điện thoại là bắt buộc'}, status=400)
        if not name:
            return Response({'error': 'Tên người thuê là bắt buộc'}, status=400)
        if not move_in:
            return Response({'error': 'Ngày bắt đầu thuê là bắt buộc'}, status=400)

        tenant = User.objects.filter(phone=phone).first()
        if not tenant:
            tenant = User.objects.filter(username=phone).first()

        if tenant:
            tenant.first_name = name
            if id_card:
                tenant.id_card = id_card
            tenant.save()
            password_info = "Sử dụng mật khẩu cũ"
        else:
            password_info = '123456'
            tenant = User.objects.create_user(
                username=phone, password=password_info,
                phone=phone, first_name=name, id_card=id_card
            )

        RoomTenant.objects.create(
            room=room, tenant=tenant,
            move_in=move_in, deposit=deposit,
            duration_months=duration_months, is_active=True
        )
        room.status = 'occupied'
        room.save()

        return Response({
            'message':  'Gán người thuê thành công',
            'username': tenant.username,
            'password': password_info,
            'room':     room.name,
        }, status=201)


class RemoveTenantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=403)
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=404)
        try:
            room_tenant = RoomTenant.objects.get(room=room, is_active=True)
        except RoomTenant.DoesNotExist:
            return Response({'error': 'Phòng không có người thuê'}, status=400)
        room_tenant.is_active = False
        room_tenant.move_out  = request.data.get('move_out')
        room_tenant.save()
        room.status = 'available'
        room.save()
        return Response({'message': 'Trả phòng thành công'}, status=200)


class TransferTenantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=403)
        try:
            current_room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng hiện tại'}, status=404)

        new_room_id = request.data.get('new_room_id')
        try:
            new_room = Room.objects.get(id=new_room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng mới'}, status=404)

        if new_room.status == 'occupied':
            return Response({'error': 'Phòng mới đã có người thuê'}, status=400)

        try:
            room_tenant = RoomTenant.objects.get(room=current_room, is_active=True)
        except RoomTenant.DoesNotExist:
            return Response({'error': 'Phòng hiện tại không có người thuê'}, status=400)

        room_tenant.is_active = False
        room_tenant.move_out  = request.data.get('move_out')
        room_tenant.save()
        current_room.status = 'available'
        current_room.save()

        RoomTenant.objects.create(
            room=new_room, tenant=room_tenant.tenant,
            move_in=request.data.get('move_in'), is_active=True
        )
        new_room.status = 'occupied'
        new_room.save()

        return Response({
            'message':  'Chuyển phòng thành công',
            'tenant':   room_tenant.tenant.username,
            'old_room': current_room.name,
            'new_room': new_room.name,
        }, status=200)
