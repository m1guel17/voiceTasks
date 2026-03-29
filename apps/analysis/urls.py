"""URL configuration for the analysis app."""
from django.urls import path

from . import views

app_name = 'analysis'

urlpatterns = [
    path('extract-tasks/', views.extract_tasks, name='extract_tasks'),
]
