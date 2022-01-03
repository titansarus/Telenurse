from django.urls import path, re_path
from apps.ads import views

urlpatterns = [
    # The home page
    path('', views.index, name='home'),
    path('submit_ad/', views.create_update_ad_view, name='submit_ad'),
    path('<int:ad_id>/edit/', views.create_update_ad_view, name='edit'),
    path('<int:ad_id>/review/', views.submit_review, name='review'),
    path('tasks_list/', views.tasks_list, name='tasks-list'),
    path('requests_list/', views.requests_list, name='requests-list'),
    path('review_list/', views.review_list, name='review-list'),
    path('<int:ad_id>/accept/', views.accept_ad, name='accept'),
    path('<int:ad_id>/delete/', views.delete_ad, name='delete'),
    # Matches any html file
    re_path(r'^.*\.*\.html', views.pages, name='pages'),
]
