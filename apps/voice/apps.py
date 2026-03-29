"""AppConfig for the voice app."""
from django.apps import AppConfig


class VoiceConfig(AppConfig):
    """Voice app: audio recording, upload, and transcription."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.voice'
    label = 'voice'
