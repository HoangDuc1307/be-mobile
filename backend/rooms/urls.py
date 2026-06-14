from django.urls import path
from .views import (
    RoomListCreateView, RoomDetailView,
    AssignTenantView, RemoveTenantView, TransferTenantView,
    AvailableRoomListView, TenantRoomView, TenantContractView,
    UploadRoomImageView, RoomContractView, UploadContractImageView,
)

urlpatterns = [
    path('',                                        RoomListCreateView.as_view(),       name='room-list'),
    path('available/',                              AvailableRoomListView.as_view(),    name='room-available'),
    path('tenant-room/',                            TenantRoomView.as_view(),           name='tenant-room'),
    path('tenant-contract/',                        TenantContractView.as_view(),       name='tenant-contract'),
    path('<int:room_id>/',                          RoomDetailView.as_view(),           name='room-detail'),
    path('<int:room_id>/assign/',                   AssignTenantView.as_view(),         name='assign-tenant'),
    path('<int:room_id>/remove/',                   RemoveTenantView.as_view(),         name='remove-tenant'),
    path('<int:room_id>/transfer/',                 TransferTenantView.as_view(),       name='transfer-tenant'),
    path('<int:room_id>/upload-image/',             UploadRoomImageView.as_view(),      name='upload-room-image'),
    path('<int:room_id>/contract/',                 RoomContractView.as_view(),         name='room-contract'),
    path('<int:room_id>/contract/upload-image/',    UploadContractImageView.as_view(),  name='upload-contract-image'),
]
