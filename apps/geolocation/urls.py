from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.geolocation.views import TrackingPointAPIView, RoutesListView, get_active_tasks, start_tracking, stop_tracking, get_nurse_location

urlpatterns = [
    path('tasks-route-location/', login_required(RoutesListView.as_view()),
         name='tasks-route-location'),
    path('track-point/', login_required(TrackingPointAPIView.as_view()),
         name='track-point'),
    path('stop-tracking/', stop_tracking, name='stop-tracking'),
    path('start-tracking/<int:ad_id>/', start_tracking, name='start-tracking'),
    path('get-nurse-location/<int:nurse_id>/', get_nurse_location, name='get-nurse-location'),
    path('active-tasks/', get_active_tasks, name='active-tasks'),
]
