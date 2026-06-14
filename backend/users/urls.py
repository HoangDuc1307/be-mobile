from django.urls import path
from .views import RegisterView, LoginView, TenantListView, TenantProfileView, LogoutView, UploadAvatarView

urlpatterns = [
    path('register/',       RegisterView.as_view(),      name='register'),
    path('login/',          LoginView.as_view(),         name='login'),
    path('logout/',         LogoutView.as_view(),        name='logout'),
    path('profile/',        TenantProfileView.as_view(), name='tenant-profile'),
    path('profile/avatar/', UploadAvatarView.as_view(),  name='upload-avatar'),
    path('tenants/',        TenantListView.as_view(),    name='tenant-list'),
]
