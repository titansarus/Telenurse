from django.contrib import admin
from apps.users.models import CustomUser

admin.site.register(CustomUser)
