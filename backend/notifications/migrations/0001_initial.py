from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id',         models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title',      models.CharField(max_length=200)),
                ('body',       models.TextField()),
                ('notif_type', models.CharField(choices=[('payment_due','Nhắc thanh toán'),('payment_success','Thanh toán thành công'),('new_invoice','Hóa đơn mới'),('contract','Hợp đồng'),('system','Thông báo hệ thống')], default='system', max_length=20)),
                ('is_read',    models.BooleanField(default=False)),
                ('invoice_id', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tenant',     models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
