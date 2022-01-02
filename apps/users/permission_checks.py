from .models import Nurse, CustomUser

def is_user_admin(user):
    return user.is_superuser


def is_user_nurse(user):
    return Nurse.objects.filter(username=user.username).count() == 1


def is_user_custom_user(user):
    return CustomUser.objects.filter(username=user.username).count() == 1

