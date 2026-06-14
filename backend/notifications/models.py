from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = [
        ('payment_due',      'Nhắc thanh toán'),
        ('payment_success',  'Thanh toán thành công'),
        ('payment_rejected', 'Thanh toán bị từ chối'),
        ('new_invoice',      'Hóa đơn mới'),
        ('contract',         'Hợp đồng'),
        ('system',           'Thông báo hệ thống'),
    ]

    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='notifications',
    )
    title      = models.CharField(max_length=200)
    body       = models.TextField()
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    is_read    = models.BooleanField(default=False)
    invoice_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        tenant_str = self.tenant.username if self.tenant else 'all'
        return f"[{self.notif_type}] {self.title} → {tenant_str}"
