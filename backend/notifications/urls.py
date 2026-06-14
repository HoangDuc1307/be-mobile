from django.urls import path
from .views import NotificationListView, MarkAllReadView

urlpatterns = [
    path('',              NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationListView.as_view(), name='notification-read'),
    path('read-all/',     MarkAllReadView.as_view(),      name='notification-read-all'),
]
