"""Vosk offline ASR adapter for VoiceTasks."""
import json
import logging
import os
import wave
from io import BytesIO

from .base import BaseASRAdapter

logger = logging.getLogger(__name__)

# Module-level model cache to avoid reloading from disk on every request
_vosk_model_cache: dict[str, object] = {}


class VoskASRAdapter(BaseASRAdapter):
    """
    Offline ASR adapter using the Vosk speech recognition library.

    Requires:
      - vosk package (pip install vosk)
      - pydub package (pip install pydub)
      - ffmpeg installed on the system (for audio format conversion)
      - A downloaded Vosk model directory set in the Model field
    """

    def __init__(self, api_key: str = '', model: str = '', endpoint: str = '', **kwargs):
        # model field holds the path to the downloaded Vosk model directory
        self.model_path = model.strip() or endpoint.strip() or ''

    def _get_vosk(self):
        try:
            import vosk
            return vosk
        except ImportError as exc:
            raise ImportError(
                'vosk package is required for VoskASRAdapter. '
                'Install it with: pip install vosk'
            ) from exc

    def _get_audio_segment(self):
        try:
            from pydub import AudioSegment
            return AudioSegment
        except ImportError as exc:
            raise ImportError(
                'pydub package is required for VoskASRAdapter. '
                'Install it with: pip install pydub'
            ) from exc

    def _load_model(self, vosk):
        if self.model_path not in _vosk_model_cache:
            _vosk_model_cache[self.model_path] = vosk.Model(self.model_path)
        return _vosk_model_cache[self.model_path]

    def transcribe(self, audio_file, language: str = 'en') -> str:
        """Transcribe audio using Vosk offline speech recognition."""
        if not self.model_path:
            logger.error('VoskASRAdapter: no model path configured')
            return ''

        try:
            vosk = self._get_vosk()
            AudioSegment = self._get_audio_segment()

            if hasattr(audio_file, 'seek'):
                audio_file.seek(0)
            audio_bytes = audio_file.read()

            # Convert to 16000 Hz, mono, 16-bit PCM WAV
            try:
                audio = AudioSegment.from_file(BytesIO(audio_bytes))
            except Exception as exc:
                if 'ffmpeg' in str(exc).lower() or 'avlib' in str(exc).lower():
                    logger.error(
                        'VoskASRAdapter: ffmpeg not found. '
                        'Install ffmpeg for audio format conversion.'
                    )
                else:
                    logger.exception('VoskASRAdapter: audio conversion failed')
                return ''

            audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
            wav_buffer = BytesIO()
            audio.export(wav_buffer, format='wav')
            wav_buffer.seek(0)

            model = self._load_model(vosk)
            results = []

            with wave.open(wav_buffer, 'rb') as wf:
                recognizer = vosk.KaldiRecognizer(model, wf.getframerate())
                while True:
                    data = wf.readframes(4000)
                    if not data:
                        break
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get('text', '').strip()
                        if text:
                            results.append(text)

                final = json.loads(recognizer.FinalResult())
                final_text = final.get('text', '').strip()
                if final_text:
                    results.append(final_text)

            return ' '.join(results).strip()

        except Exception:
            logger.exception('VoskASRAdapter.transcribe() failed')
            return ''

    def test_connection(self) -> tuple[bool, str]:
        """Verify the Vosk model directory exists and is loadable."""
        if not self.model_path:
            return (
                False,
                'No model path configured. '
                'Set the Model field to the path of your downloaded Vosk model directory.',
            )
        if not os.path.isdir(self.model_path):
            return False, f'Model directory not found: {self.model_path}'
        try:
            vosk = self._get_vosk()
            self._load_model(vosk)
            return True, f'Vosk model loaded successfully from: {self.model_path}'
        except Exception as exc:
            return False, f'Failed to load Vosk model: {exc}'
