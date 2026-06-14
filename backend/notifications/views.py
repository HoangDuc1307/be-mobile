from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifs = Notification.objects.filter(tenant=request.user)
        serializer = NotificationSerializer(notifs, many=True)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Mark a single notification as read."""
        try:
            notif = Notification.objects.get(pk=pk, tenant=request.user)
        except Notification.DoesNotExist:
            return Response({'error': 'Không tìm thấy thông báo'}, status=404)
        notif.is_read = True
        notif.save()
        return Response(NotificationSerializer(notif).data)


class MarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(tenant=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'Đã đánh dấu tất cả là đã đọc'})
