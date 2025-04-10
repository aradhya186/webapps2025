from django.urls import path
from . import views

urlpatterns = [
    path('dashboard', views.dashboard, name='dashboard'),
    path('money_transfer', views.money_transfer, name='money_transfer'),
    path('money', views.money, name='money'),
    path('request_money', views.request_money, name='request_money'),
    path('accept/<int:request_id>/', views.accept_request, name='accept_request'),
    path('reject/<int:request_id>/', views.reject_request, name='reject_request')
]
