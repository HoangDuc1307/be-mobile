from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0002_remove_invoice_new_electric_remove_invoice_new_water_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankInfo',
            fields=[
                ('id',             models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name',      models.CharField(default='Vietcombank', max_length=100)),
                ('account_number', models.CharField(max_length=50)),
                ('account_name',   models.CharField(max_length=100)),
                ('is_active',      models.BooleanField(default=True)),
            ],
        ),
    ]
