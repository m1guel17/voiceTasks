"""
VoiceNote model for VoiceTasks.

Stores an uploaded audio recording and its transcription result.
"""
from django.db import models


class VoiceNote(models.Model):
    """
    A recorded audio clip with its transcription.

    The audio_file is stored under MEDIA_ROOT/voice_notes/.
    The transcription may be empty until the ASR service processes it.
    """

    audio_file = models.FileField(upload_to='voice_notes/')
    language = models.CharField(max_length=10, default='en')
    transcription = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        snippet = self.transcription[:60] if self.transcription else '(no transcription)'
        return f'VoiceNote {self.pk}: {snippet}'
