from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Room, RoomTenant
from .serializers import RoomSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class RoomListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_owner():
            #chủ trọ có thể xem tất cả phòng của mình
            rooms = Room.objects.filter(owner=request.user)
        else:
            rooms = Room.objects.filter(
                current_tenant__tenant=request.user,
                current_tenant__is_active=True
            )
        return Response(RoomSerializer(rooms, many=True).data)
    
    def post(self, request):
        if not request.user.is_owner:
            return Response({'error': 'Không có quyền'}, status=403)
        
        serializer = RoomSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save(owner=request.user)
        return Response(serializer.data, status=201)
    
class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=404)
        return Response(RoomSerializer(room).data)
    
    def put(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=404)
        if room.owner != request.user:
            return Response({'error': 'Không có quyền'}, status=403)
        serializer = RoomSerializer(room, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, room_id):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=404)
        
        if room.owner != request.user:
            return Response({'error': 'Không có quyền'}, status=403)
        if RoomTenant.objects.filter(room=room, is_active=True).exists():
            return Response({'error': 'Không thể xóa phòng đang có người thuê'}, status=400)
        room.delete()
        return Response({'message': 'Xóa phòng thành công'}, status=204)

class AssignTenantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=403)

        try:
            room = Room.objects.get(id=room_id, owner=request.user)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=404)

        if room.status == 'occupied':
            return Response({'error': 'Phòng đã có người thuê'}, status=400)

        username = request.data.get('username')
        password = request.data.get('password', '123456')
        phone    = request.data.get('phone', '')
        move_in  = request.data.get('move_in')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username đã tồn tại'}, status=400)

        tenant = User.objects.create_user(
            username = username,
            password = password,
            phone    = phone,
            role     = 'tenant'
        )

        RoomTenant.objects.create(
            room      = room,
            tenant    = tenant,
            move_in   = move_in,
            is_active = True
        )

        room.status = 'occupied'
        room.save()

        return Response({
            'message':  'Gán người thuê thành công',
            'username': username,
            'password': password,
            'room':     room.name
        }, status=201)
    

class RemoveTenantView(APIView):
    """Chủ trọ cho người thuê trả phòng"""
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=403)

        try:
            room = Room.objects.get(id=room_id, owner=request.user)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng'}, status=404)

        try:
            room_tenant = RoomTenant.objects.get(room=room, is_active=True)
        except RoomTenant.DoesNotExist:
            return Response({'error': 'Phòng không có người thuê'}, status=400)

        # Lưu ngày trả phòng + đánh dấu không còn active
        room_tenant.is_active = False
        room_tenant.move_out  = request.data.get('move_out')
        room_tenant.save()

        # Đổi trạng thái phòng về trống
        room.status = 'available'
        room.save()

        return Response({'message': 'Trả phòng thành công'}, status=200)


class TransferTenantView(APIView):
    """Chủ trọ chuyển người thuê sang phòng khác"""
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        if not request.user.is_owner():
            return Response({'error': 'Không có quyền'}, status=403)

        # Phòng hiện tại
        try:
            current_room = Room.objects.get(id=room_id, owner=request.user)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng hiện tại'}, status=404)

        # Phòng mới muốn chuyển sang
        new_room_id = request.data.get('new_room_id')
        try:
            new_room = Room.objects.get(id=new_room_id, owner=request.user)
        except Room.DoesNotExist:
            return Response({'error': 'Không tìm thấy phòng mới'}, status=404)

        if new_room.status == 'occupied':
            return Response({'error': 'Phòng mới đã có người thuê'}, status=400)

        # Lấy người thuê hiện tại
        try:
            room_tenant = RoomTenant.objects.get(room=current_room, is_active=True)
        except RoomTenant.DoesNotExist:
            return Response({'error': 'Phòng hiện tại không có người thuê'}, status=400)

        # Đóng hợp đồng phòng cũ
        room_tenant.is_active = False
        room_tenant.move_out  = request.data.get('move_out')
        room_tenant.save()
        current_room.status = 'available'
        current_room.save()

        # Tạo hợp đồng phòng mới
        RoomTenant.objects.create(
            room      = new_room,
            tenant    = room_tenant.tenant,
            move_in   = request.data.get('move_in'),
            is_active = True
        )
        new_room.status = 'occupied'
        new_room.save()

        return Response({
            'message':  'Chuyển phòng thành công',
            'tenant':   room_tenant.tenant.username,
            'old_room': current_room.name,
            'new_room': new_room.name
        }, status=200)