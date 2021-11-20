# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from apps.geolocation.views import TrackingPointAPIView, RoutesListView, RouteCreateView
from django.contrib.auth.decorators import login_required


# from apps.ads import views


urlpatterns = [
    # The home page
    path("", views.index, name="home"),
    path("<int:ad_id>/accept/", views.accept_ad, name="accept"),
    path("<int:ad_id>/start/", views.start_task, name="start"),
    path("<int:ad_id>/end/", views.end_task, name="end"),
    path("tasks-list.html", login_required(TrackingPointAPIView.as_view()), name="tasks"),
    path("nurse-location.html", login_required(RoutesListView.as_view()), name="locations"),
    path("endtask.html", login_required(RouteCreateView.as_view()), name="end_tasks"),
    # Matches any html file
    re_path(r"^.*\.*\.html", views.pages, name="pages"),
]
