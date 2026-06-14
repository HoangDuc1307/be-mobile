from rest_framework import serializers
from .models import Room, RoomTenant


class RoomSerializer(serializers.ModelSerializer):
    tenant_name     = serializers.SerializerMethodField()
    tenant_phone    = serializers.SerializerMethodField()
    move_in         = serializers.SerializerMethodField()
    deposit         = serializers.SerializerMethodField()
    duration_months = serializers.SerializerMethodField()
    floor           = serializers.SerializerMethodField()
    room_image_url  = serializers.SerializerMethodField()

    class Meta:
        model  = Room
        fields = [
            'id', 'name', 'price', 'area', 'status', 'floor',
            'capacity', 'amenities', 'description', 'created_at',
            'tenant_name', 'tenant_phone', 'move_in', 'deposit',
            'duration_months', 'room_image_url',
        ]
        read_only_fields = ['created_at']

    def get_room_image_url(self, obj):
        if not obj.room_image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.room_image.url)
        return obj.room_image.url

    def get_floor(self, obj):
        if obj.floor:
            return obj.floor
        import re
        match = re.search(r'(\d)', obj.name)
        if match:
            return f"Tầng {match.group(1)}"
        return ""

    def _active_rt(self, obj):
        return RoomTenant.objects.filter(room=obj, is_active=True).order_by('-id').first()

    def get_tenant_name(self, obj):
        rt = self._active_rt(obj)
        if not rt:
            return None
        full = f"{rt.tenant.last_name} {rt.tenant.first_name}".strip()
        return full or rt.tenant.username

    def get_tenant_phone(self, obj):
        rt = self._active_rt(obj)
        return rt.tenant.phone if rt else None

    def get_move_in(self, obj):
        rt = self._active_rt(obj)
        return rt.move_in.strftime('%d/%m/%Y') if rt else None

    def get_deposit(self, obj):
        rt = self._active_rt(obj)
        return str(rt.deposit) if rt else None

    def get_duration_months(self, obj):
        rt = self._active_rt(obj)
        return rt.duration_months if rt else None


class ContractSerializer(serializers.ModelSerializer):
    room_name          = serializers.CharField(source='room.name', read_only=True)
    move_in            = serializers.DateField(format='%d/%m/%Y')
    move_out           = serializers.DateField(format='%d/%m/%Y', allow_null=True)
    landlord_name      = serializers.SerializerMethodField()
    tenant_name        = serializers.SerializerMethodField()
    contract_image_url = serializers.SerializerMethodField()

    class Meta:
        model  = RoomTenant
        fields = [
            'id', 'room_name', 'move_in', 'move_out',
            'deposit', 'duration_months', 'is_active',
            'landlord_name', 'tenant_name', 'contract_image_url',
        ]

    def get_contract_image_url(self, obj):
        if not obj.contract_image:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.contract_image.url)
        return obj.contract_image.url

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
