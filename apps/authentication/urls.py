# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import login_view, register_user, init_view
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("init/", init_view, name="init"),
    path("login/", login_view, name="login"),
    path("register/", register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
