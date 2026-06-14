from django.db import models
from django.conf import settings
from rooms.models import Room


class BankInfo(models.Model):
    bank_name      = models.CharField(max_length=100, default='Vietcombank')
    account_number = models.CharField(max_length=50)
    account_name   = models.CharField(max_length=100)
    is_active      = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class UnitPrice(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='unit_price')
    electricity_price = models.DecimalField(max_digits=10, decimal_places=0, default=3500)
    water_price = models.DecimalField(max_digits=10, decimal_places=0, default=15000)
    common_service_fee = models.DecimalField(max_digits=10, decimal_places=0, default=100000)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Đơn giá của {self.owner.username}"


class Invoice(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='invoices')
    month = models.IntegerField()
    year = models.IntegerField()
    room_price = models.DecimalField(max_digits=10, decimal_places=0)
    electricity_usage = models.IntegerField(default=0)
    water_usage = models.IntegerField(default=0)
    service_price = models.DecimalField(max_digits=10, decimal_places=0)

    # Đơn giá áp dụng tại thời điểm tạo hóa đơn
    electricity_price = models.DecimalField(max_digits=10, decimal_places=0)
    water_price = models.DecimalField(max_digits=10, decimal_places=0)

    # Thành tiền tự động tính
    total_electric = models.DecimalField(max_digits=10, decimal_places=0)
    total_water = models.DecimalField(max_digits=10, decimal_places=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=0)

    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Hóa đơn {self.room.name} - Tháng {self.month}/{self.year}"
