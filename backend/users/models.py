from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone     = models.CharField(max_length=20, blank=True, null=True)
    id_card   = models.CharField(max_length=20, blank=True, null=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    avatar    = models.ImageField(upload_to='avatars/', null=True, blank=True)
    
    def is_owner(self):
        # Superuser hoặc staff = chủ trọ
        return self.is_superuser or self.is_staff

    def is_tenant(self):
        return not self.is_staff and not self.is_superuser