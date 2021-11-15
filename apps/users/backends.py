from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class SettingsBackend(BaseBackend):
    """
    Authenticate against the settings ADMIN_LOGIN and ADMIN_PASSWORD.

    Use the login name and a hash of the password. For example:

    ADMIN_LOGIN = 'admin'
    ADMIN_PASSWORD = 'pbkdf2_sha256$30000$Vo0VlMnkR4Bk$qEvtdyZRWTcOsCnI/oQ7fVOu1XAURIZYoOZ3iq8Dr4M='
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        print("^^^^^^^^^^^^ hereeeeeeeeeeee", password)
        if password is None or password == '':
            print("######## password in None")
        user = User.objects.get(username=username)
        print("user fields:", user.username, user.first_name, user.password)
        print("in authentication function:", user, ", ", user.check_password(password))
        if user is not None and user.check_password(password):
            return user
            # if user.is_active == Constants.YES:
            #     return user
            # else:
            #     return "User is not activated"
        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None