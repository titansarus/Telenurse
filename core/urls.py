# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this


urlpatterns = [
    path("admin/", admin.site.urls),  # Django admin route
    path("", include("apps.users.urls")),  # Auth routes - login / register
    path("", include("apps.ads.urls")),  # UI Kits Html files
    path("", include("apps.geolocation.urls")),  # UI Kits Html files
]
