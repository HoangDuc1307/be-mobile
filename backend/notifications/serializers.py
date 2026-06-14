from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    time_display = serializers.SerializerMethodField()

    class Meta:
        model  = Notification
        fields = ['id', 'title', 'body', 'notif_type', 'is_read',
                  'invoice_id', 'created_at', 'time_display']

    def get_time_display(self, obj):
        from django.utils import timezone
        import math
        now   = timezone.now()
        delta = now - obj.created_at
        minutes = int(delta.total_seconds() // 60)
        if minutes < 1:
            return "Vừa xong"
        if minutes < 60:
            return f"{minutes} phút trước"
        hours = minutes // 60
        if hours < 24:
            return f"{hours} giờ trước"
        days = hours // 24
        if days == 1:
            return "Hôm qua"
        return f"{days} ngày trước"
