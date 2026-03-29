"""AppConfig for the providers app."""
from django.apps import AppConfig


class ProvidersConfig(AppConfig):
    """Providers app: adapter registry, factory, and provider configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.providers'
    label = 'providers'
