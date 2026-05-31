from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = [
        ('owner', 'Chủ trọ'),
        ('tenant', 'Người thuê'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def is_owner(self):
        return self.role == 'owner'
    def is_tenant(self):
        return self.role == 'tenant'