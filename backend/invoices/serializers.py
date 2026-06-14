from rest_framework import serializers
from .models import UnitPrice, Invoice, BankInfo
from rooms.serializers import RoomSerializer


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
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'electricity_price', 'water_price',
            'total_electric', 'total_water', 'grand_total',
            'created_at', 'updated_at',
        ]


class InvoiceHistorySerializer(serializers.ModelSerializer):
    paid_at = serializers.DateTimeField(source='updated_at', format='%d/%m/%Y', read_only=True)

    class Meta:
        model  = Invoice
        fields = ['id', 'month', 'year', 'grand_total', 'is_paid', 'paid_at']
