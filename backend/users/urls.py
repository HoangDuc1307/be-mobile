from django.urls import path
from .views import RegisterView, LoginView, TenantListView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('tenants/', TenantListView.as_view(), name='tenant-list'),
]