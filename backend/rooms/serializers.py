from rest_framework import serializers
from .models import Room, RoomTenant


class RoomSerializer(serializers.ModelSerializer):
    tenant_name  = serializers.SerializerMethodField()
    tenant_phone = serializers.SerializerMethodField()
    move_in      = serializers.SerializerMethodField()
    deposit      = serializers.SerializerMethodField()
    floor        = serializers.SerializerMethodField()

    class Meta:
        model  = Room
        fields = [
            'id', 'name', 'price', 'area', 'status', 'floor',
            'capacity', 'amenities', 'description', 'created_at',
            'tenant_name', 'tenant_phone', 'move_in', 'deposit',
        ]
        read_only_fields = ['created_at']

    def get_floor(self, obj):
        if obj.floor:
            return obj.floor
        import re
        match = re.search(r'(\d)', obj.name)
        if match:
            return f"Tầng {match.group(1)}"
        return ""

    def get_tenant_name(self, obj):
        try:
            rt = RoomTenant.objects.get(room=obj, is_active=True)
            full = f"{rt.tenant.last_name} {rt.tenant.first_name}".strip()
            return full or rt.tenant.username
        except RoomTenant.DoesNotExist:
            return None

    def get_tenant_phone(self, obj):
        try:
            return RoomTenant.objects.get(room=obj, is_active=True).tenant.phone
        except RoomTenant.DoesNotExist:
            return None

    def get_move_in(self, obj):
        try:
            return RoomTenant.objects.get(room=obj, is_active=True).move_in.strftime('%d/%m/%Y')
        except RoomTenant.DoesNotExist:
            return None

    def get_deposit(self, obj):
        try:
            return str(RoomTenant.objects.get(room=obj, is_active=True).deposit)
        except RoomTenant.DoesNotExist:
            return None


class ContractSerializer(serializers.ModelSerializer):
    room_name      = serializers.CharField(source='room.name', read_only=True)
    move_in        = serializers.DateField(format='%d/%m/%Y')
    move_out       = serializers.DateField(format='%d/%m/%Y', allow_null=True)
    landlord_name  = serializers.SerializerMethodField()
    tenant_name    = serializers.SerializerMethodField()

    class Meta:
        model  = RoomTenant
        fields = [
            'id', 'room_name', 'move_in', 'move_out',
            'deposit', 'duration_months', 'is_active',
            'landlord_name', 'tenant_name',
        ]

    def get_landlord_name(self, obj):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        owner = User.objects.filter(is_superuser=True, full_name__isnull=False).exclude(full_name='').first() \
                or User.objects.filter(is_superuser=True).last()
        if owner:
            return owner.full_name or owner.username
        return "Chủ nhà"

    def get_tenant_name(self, obj):
        u = obj.tenant
        full = f"{u.last_name} {u.first_name}".strip()
        return full or u.full_name or u.username
