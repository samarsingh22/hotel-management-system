from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('api/reservations/', views.get_reservations, name='api_reservations'),
]