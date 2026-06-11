from django.urls import path
from .views import RoomListCreateView, RoomDetailView, AssignTenantView, RemoveTenantView, TransferTenantView

urlpatterns = [
    path('',                      RoomListCreateView.as_view(), name='room-list'),
    path('<int:room_id>/',        RoomDetailView.as_view(),     name='room-detail'),
    path('<int:room_id>/assign/', AssignTenantView.as_view(),   name='assign-tenant'),
    path('<int:room_id>/remove/', RemoveTenantView.as_view(),   name='remove-tenant'),
    path('<int:room_id>/transfer/', TransferTenantView.as_view(), name='transfer-tenant'),
]