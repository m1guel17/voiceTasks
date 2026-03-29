"""AppConfig for the analysis app."""
from django.apps import AppConfig


class AnalysisConfig(AppConfig):
    """Analysis app: LLM-powered task extraction from transcriptions."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.analysis'
    label = 'analysis'
