from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/reservations/', views.get_reservations, name='api_reservations'),
    path('api/dashboard/', views.get_dashboard_data, name='api_dashboard'),
]