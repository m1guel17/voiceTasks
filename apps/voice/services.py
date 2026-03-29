"""
ASR service for VoiceTasks.

Routes audio through the active ASR provider adapter.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class ASRService:
    """
    Speech-to-text transcription service.

    Delegates to the currently active ASR provider via ProviderFactory.
    Falls back to mock provider if none is configured.
    """

    def transcribe(self, audio_file, language: str = 'en') -> str:
        """
        Transcribe an audio file.

        Args:
            audio_file: A Django UploadedFile or file-like object.
            language: BCP-47 language code (e.g. 'en', 'es', 'fr').

        Returns:
            Transcription string. Returns empty string on failure.
        """
        # Import here to avoid circular imports at module load time
        from apps.providers.factory import ProviderFactory

        try:
            adapter = ProviderFactory.get_active_asr()
            transcription = adapter.transcribe(audio_file, language=language)
            logger.info('Transcription completed (%d chars)', len(transcription))
            return transcription
        except Exception:
            logger.exception('Transcription failed')
            return ''
