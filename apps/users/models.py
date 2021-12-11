from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import CustomUserManager
from .validators import validate_file_size


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=11)

    REQUIRED_FIELDS = ["email", "first_name",
                       "last_name", "password", "phone_number"]

    objects = CustomUserManager()

    def __str__(self):
        return self.username


class Nurse(CustomUser):
    document = models.FileField(
        upload_to="documents/%Y/%m/%d", validators=[validate_file_size])

    def __str__(self):
        return (
            f"Nurse with username {self.username} info: {self.first_name} {self.last_name}, {self.email}, "
            f"{self.phone_number}"
        )
