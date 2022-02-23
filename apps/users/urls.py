# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.urls import path, re_path
from django.contrib.auth.views import LogoutView, PasswordResetConfirmView, PasswordResetCompleteView

from .views import *

password_urlpatterns = [
    path('password-reset/', ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
]

activate_urlpatterns = [
    re_path(r'activate/manual/',
            activate_manually_view, name='activate-manual'),
    re_path(r'activate/(?P<uidb64>[0-9A-Za-z_-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,128})/',
            activate, name='activate'),
]

urlpatterns = [
                  path('init/', init_view, name='init'),
                  path('login/', login_view, name='login'),
                  path('register/', register_view, name='register'),
                  path('logout/', LogoutView.as_view(), name='logout'),
                  path('nurse-list/', nurse_list_view, name='nurse-list'),
                  path('profile/', user_profile_view, name='user-profile'),
                  path('change-password/', change_password_view, name='change-password'),

              ] + password_urlpatterns + activate_urlpatterns
