# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.ads import views


# from apps.ads import views


urlpatterns = [
    # The home page
    path("", views.index, name="home"),
    path('submit_ad/', views.submit_new_ad_view, name='submit_ad'),
    path('ads_list/', views.ads_list, name='ads-list'),
    path('tasks_list/', views.tasks_list, name='tasks-list'),
    path("<int:ad_id>/accept/", views.accept_ad, name="accept"),
    path("<int:ad_id>/start/", views.start_task, name="start"),
    path("<int:ad_id>/end/", views.end_task, name="end"),
    # Matches any html file
    re_path(r"^.*\.*\.html", views.pages, name="pages"),
]