from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .validators import validate_file_size


from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    document = models.FileField(upload_to="documents/%Y/%m/%d", validators=[validate_file_size])
    phone_number = models.CharField(max_length=11)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name", "password", "phone_number"]

    objects = CustomUserManager()

    def __str__(self):
        return self.username + " / " + self.password

class Nurse(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    document = models.FileField(upload_to="documents/%Y/%m/%d")
    phone_number = models.CharField(max_length=11)

    def __str__(self):
        return (
            f"Nurse with username {self.username} info: {self.first_name} {self.last_name}, {self.email}, "
            f"{self.phone_number}"
        )
