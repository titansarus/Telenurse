from django.urls import path
from apps.geolocation import views
from apps.geolocation.views import TrackingPointAPIView, RoutesListView, RouteCreateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("tasks-list.html", login_required(TrackingPointAPIView.as_view()), name="tasks"),
    path("nurse-location/", login_required(RoutesListView.as_view()), name="nurse-location"),
    path("endtask.html", login_required(RouteCreateView.as_view()), name="end_tasks"),
]
