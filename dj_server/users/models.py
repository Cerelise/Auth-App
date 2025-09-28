import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager


class CustomUser(AbstractUser):
    USERNAME_FIELD = "email"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50)
    profile_image = models.ImageField(upload_to="profile/", null=True, blank=True)
    bio = models.TextField(max_length=500, default="")
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = []

    objects = CustomUserManager()
