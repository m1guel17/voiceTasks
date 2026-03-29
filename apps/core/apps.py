"""AppConfig for the core app."""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core app: shared layout, dashboard, and utilities."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    label = 'core'
