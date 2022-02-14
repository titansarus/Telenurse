import os

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

from .managers import CustomUserManager
from .validators import validate_file_size

from ..address.models import Address


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=11)
    avatar = models.ImageField(blank=True, null=True, upload_to='profile_pictures')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, blank=True, null=True)

    REQUIRED_FIELDS = ["email", "first_name", "last_name", "password", "phone_number"]

    objects = CustomUserManager()

    def __str__(self):
        return self.username

    def get_avatar_url(self):
        if not self.avatar:
            return os.path.join(settings.STATIC_URL, 'assets/img/default-avatar.png')
        return os.path.join(settings.MEDIA_URL, self.avatar.url)


class Nurse(CustomUser):
    document = models.FileField(
        upload_to="documents/%Y/%m/%d", validators=[validate_file_size])

    def __str__(self):
        return (
            f"Nurse with username {self.username} info: {self.first_name} {self.last_name}, {self.email}, "
            f"{self.phone_number}"
        )
