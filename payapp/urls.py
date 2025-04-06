from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('points_transfer', views.points_transfer, name='points_transfer'),
    path('points', views.points, name='points'),
    path('request_points', views.request_points, name='request_points'),
    path('accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request')
]
