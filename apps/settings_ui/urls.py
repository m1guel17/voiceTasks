"""URL configuration for the settings_ui app."""
from django.urls import path

from . import views

app_name = 'settings_ui'

urlpatterns = [
    path('', views.provider_settings, name='providers'),
    path('create/', views.provider_create, name='provider_create'),
    path('<int:provider_id>/update/', views.provider_update, name='provider_update'),
    path('<int:provider_id>/delete/', views.provider_delete, name='provider_delete'),
]
