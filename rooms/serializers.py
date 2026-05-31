from rest_framework import serializers
from .models import Room, RoomTenant

class RoomSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    tenant_name = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'price', 'area', 'status',
                  'description', 'created_at', 'owner_name', 'tenant_name']
        read_only_fields = ['owner', 'status', 'created_at']

    def get_tenant_name(self, obj):
        #lấy tên người đang thuê phòng nếu có
        try:
             room_tenant = RoomTenant.objects.get(room=obj, is_active=True)
             return room_tenant.tenant.username
        except RoomTenant.DoesNotExist:
            return None 