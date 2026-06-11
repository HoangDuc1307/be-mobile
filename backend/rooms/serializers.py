from rest_framework import serializers
from .models import Room, RoomTenant

class RoomSerializer(serializers.ModelSerializer):
    tenant_name = serializers.SerializerMethodField()
    tenant_phone = serializers.SerializerMethodField()
    move_in = serializers.SerializerMethodField()
    deposit = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['id', 'name', 'price', 'area', 'status',
                  'description', 'created_at', 'tenant_name',
                  'tenant_phone', 'move_in', 'deposit']
        read_only_fields = ['created_at']

    def get_tenant_name(self, obj):
        try:
            room_tenant = RoomTenant.objects.get(room=obj, is_active=True)
            user = room_tenant.tenant
            full_name = f"{user.last_name} {user.first_name}".strip()
            return full_name if full_name else user.username
        except RoomTenant.DoesNotExist:
            return None

    def get_tenant_phone(self, obj):
        try:
            room_tenant = RoomTenant.objects.get(room=obj, is_active=True)
            return room_tenant.tenant.phone
        except RoomTenant.DoesNotExist:
            return None

    def get_move_in(self, obj):
        try:
            room_tenant = RoomTenant.objects.get(room=obj, is_active=True)
            return room_tenant.move_in.strftime('%d/%m/%Y')
        except RoomTenant.DoesNotExist:
            return None

    def get_deposit(self, obj):
        try:
            room_tenant = RoomTenant.objects.get(room=obj, is_active=True)
            return str(room_tenant.deposit)
        except RoomTenant.DoesNotExist:
            return None