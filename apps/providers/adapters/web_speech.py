"""Web Speech API passthrough adapter for VoiceTasks."""
import logging

from .base import BaseASRAdapter

logger = logging.getLogger(__name__)


class WebSpeechASRAdapter(BaseASRAdapter):
    """
    Passthrough adapter for the browser-native Web Speech API.

    Transcription happens entirely in the browser via the SpeechRecognition API.
    The pre-transcribed text is sent by the frontend as a POST field; the backend
    view uses it directly without invoking this adapter's transcribe() method.

    No API key, model, or endpoint is required.
    """

    def __init__(self, **kwargs):
        pass

    def transcribe(self, audio_file, language: str = 'en') -> str:
        """Not used — transcription happens in the browser."""
        logger.debug(
            'WebSpeechASRAdapter.transcribe() called; '
            'transcription should have been provided by the browser.'
        )
        return ''

    def test_connection(self) -> tuple[bool, str]:
        return True, 'Web Speech API runs in the browser — no server-side connection needed.'
