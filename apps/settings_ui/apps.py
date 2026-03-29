"""AppConfig for the settings_ui app."""
from django.apps import AppConfig


class SettingsUIConfig(AppConfig):
    """Settings UI app: provider configuration forms and management."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.settings_ui'
    label = 'settings_ui'
