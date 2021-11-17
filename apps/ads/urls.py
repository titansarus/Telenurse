# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from .views import ads_view

urlpatterns = [
    path('submit_ad/', ads_view, name='submit_ad'),
]
