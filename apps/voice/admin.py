"""Admin configuration for the voice app."""
from django.contrib import admin

from .models import VoiceNote


@admin.register(VoiceNote)
class VoiceNoteAdmin(admin.ModelAdmin):
    """Admin interface for VoiceNote model."""

    list_display = ('pk', 'language', 'transcription_snippet', 'created_at')
    list_filter = ('language',)
    search_fields = ('transcription',)
    readonly_fields = ('created_at',)

    def transcription_snippet(self, obj):
        """Return first 80 chars of transcription for list display."""
        return obj.transcription[:80] if obj.transcription else '—'

    transcription_snippet.short_description = 'Transcription'
