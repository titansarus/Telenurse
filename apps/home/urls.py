# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
# from apps.ads import views


urlpatterns = [
    # The home page
    path("", views.index, name="home"),
    path("<int:ad_id>/accept/", views.accept_ad, name="accept"),

    # Matches any html file
    re_path(r'^.*\.*\.html', views.pages, name='pages'),
]
