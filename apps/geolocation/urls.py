from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.geolocation.views import TrackingPointAPIView, RoutesListView, start_tracking, stop_tracking

urlpatterns = [
    path('nurse-location/', login_required(RoutesListView.as_view()),
         name='nurse-location'),
    path('track-point/', login_required(TrackingPointAPIView.as_view()),
         name='track-point'),
    path('stop-tracking/', stop_tracking, name='stop-tracking'),
    path('start-tracking/<int:ad_id>/', start_tracking, name='start-tracking'),
]
