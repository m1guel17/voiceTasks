"""URL configuration for the providers app."""
from django.urls import path

from . import views

app_name = 'providers'

urlpatterns = [
    path('test/', views.test_connection, name='test_connection'),
]
