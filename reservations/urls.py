from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('api/reservations/', views.get_reservations, name='api_reservations'),
    path('api/dashboard/', views.get_dashboard_data, name='api_dashboard'),
    path('api/listings/create/', views.create_listing, name='create_listing'),
    path('api/reservations/create/', views.create_reservation, name='create_reservation'),
]