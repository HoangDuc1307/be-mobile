from rest_framework import serializers
from .models import UnitPrice, Invoice, BankInfo
from rooms.serializers import RoomSerializer
from rooms.models import RoomTenant


class BankInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = BankInfo
        fields = ['bank_name', 'account_number', 'account_name']


class UnitPriceSerializer(serializers.ModelSerializer):
    last_updated = serializers.DateTimeField(source='updated_at', format='%d/%m/%Y %H:%M:%S', read_only=True)

    class Meta:
        model  = UnitPrice
        fields = ['electricity_price', 'water_price', 'common_service_fee', 'last_updated']


class InvoiceSerializer(serializers.ModelSerializer):
    room_details = RoomSerializer(source='room', read_only=True)

    class Meta:
        model  = Invoice
        fields = [
            'id', 'room', 'room_details', 'month', 'year', 'room_price',
            'electricity_usage', 'water_usage',
            'service_price', 'electricity_price', 'water_price',
            'total_electric', 'total_water', 'grand_total', 'is_paid',
            'payment_status', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'electricity_price', 'water_price',
            'total_electric', 'total_water', 'grand_total',
            'payment_status', 'created_at', 'updated_at',
        ]


class PendingPaymentSerializer(serializers.ModelSerializer):
    room_name   = serializers.CharField(source='room.name', read_only=True)
    tenant_name = serializers.SerializerMethodField()
    proof_url   = serializers.SerializerMethodField()

    def get_tenant_name(self, obj):
        rt = RoomTenant.objects.filter(room=obj.room, is_active=True).order_by('-id').first()
        if not rt:
            return ''
        return rt.tenant.full_name or rt.tenant.username

    def get_proof_url(self, obj):
        if obj.payment_proof:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.payment_proof.url) if request else obj.payment_proof.url
        return None

    class Meta:
        model  = Invoice
        fields = ['id', 'room_name', 'tenant_name', 'month', 'year', 'grand_total', 'proof_url', 'payment_status', 'updated_at']


class InvoiceHistorySerializer(serializers.ModelSerializer):
    paid_at = serializers.DateTimeField(source='updated_at', format='%d/%m/%Y', read_only=True)

    class Meta:
        model  = Invoice
        fields = ['id', 'month', 'year', 'grand_total', 'is_paid', 'paid_at']
