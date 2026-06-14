from django.db import models
from django.conf import settings

class Room(models.Model):
    STATUS_CHOICES = [
        ('available', 'Còn trống'),
        ('occupied',  'Đã thuê'),
    ]

    name        = models.CharField(max_length=100)
    price       = models.DecimalField(max_digits=10, decimal_places=0)
    area        = models.FloatField()
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    floor       = models.CharField(max_length=20, blank=True, null=True)
    capacity    = models.IntegerField(default=2, blank=True, null=True)
    amenities   = models.TextField(blank=True, default='')
    description = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RoomTenant(models.Model):
    room            = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='current_tenant')
    tenant          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    move_in         = models.DateField()
    move_out        = models.DateField(null=True, blank=True)
    deposit         = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    duration_months = models.IntegerField(default=12)
    is_active       = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tenant.username} - {self.room.name}"