from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class SettingsBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = User.objects.get(username=username)
        if user is not None and user.check_password(password):
            return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
