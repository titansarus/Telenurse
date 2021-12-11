from django.urls import path
from apps.geolocation.views import TrackingPointAPIView, RoutesListView, RouteCreateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path("nurse-location/", login_required(RoutesListView.as_view()), name="nurse-location"),
    path("start-tracking/", login_required(TrackingPointAPIView.as_view()), name="start-tracking"),
    path("stop-tracking/", login_required(RouteCreateView.as_view()), name="stop-tracking"),
]
