from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_roomtenant_duration_months'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='floor',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='capacity',
            field=models.IntegerField(blank=True, default=2, null=True),
        ),
        migrations.AddField(
            model_name='room',
            name='amenities',
            field=models.TextField(blank=True, default=''),
        ),
    ]
