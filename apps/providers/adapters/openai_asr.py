"""
OpenAI Whisper ASR adapter for VoiceTasks.

Uses the openai Python SDK to call the Whisper speech-to-text API.
Requires an API key stored in the ProviderConfiguration model.
"""
from __future__ import annotations

import logging

from .base import BaseASRAdapter

logger = logging.getLogger(__name__)


class OpenAIASRAdapter(BaseASRAdapter):
    """
    ASR adapter for OpenAI Whisper (whisper-1 model).

    Args:
        api_key: OpenAI API key.
        model: Whisper model name (default 'whisper-1').
        endpoint: Optional custom base URL for OpenAI-compatible endpoints.
    """

    DEFAULT_MODEL = 'whisper-1'

    def __init__(self, api_key: str, model: str = '', endpoint: str = '', **kwargs):
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL
        self.endpoint = endpoint or None

    def _get_client(self):
        """Instantiate and return the openai client."""
        try:
            import openai
        except ImportError as exc:
            raise ImportError(
                'openai package is required for OpenAIASRAdapter. '
                'Install it with: pip install openai'
            ) from exc

        kwargs = {'api_key': self.api_key}
        if self.endpoint:
            kwargs['base_url'] = self.endpoint
        return openai.OpenAI(**kwargs)

    def transcribe(self, audio_file, language: str = 'en') -> str:
        """
        Transcribe audio using OpenAI Whisper.

        Args:
            audio_file: A file-like object or Django UploadedFile.
            language: BCP-47 language code.

        Returns:
            Transcription text string.

        Raises:
            Exception: Re-raises API errors so the service layer can log them.
        """
        client = self._get_client()

        # OpenAI SDK expects a file tuple: (filename, file_object, content_type)
        # Handle both Django UploadedFile and plain file objects
        if hasattr(audio_file, 'name'):
            filename = audio_file.name
        else:
            filename = 'audio.webm'

        # Seek to start if possible
        if hasattr(audio_file, 'seek'):
            audio_file.seek(0)

        response = client.audio.transcriptions.create(
            model=self.model,
            file=(filename, audio_file, 'audio/webm'),
            language=language if language != 'auto' else None,
        )
        return response.text

    def test_connection(self) -> tuple[bool, str]:
        """Test by listing available models."""
        try:
            client = self._get_client()
            client.models.list()
            return True, 'OpenAI connection successful.'
        except Exception as exc:
            return False, f'OpenAI connection failed: {exc}'
