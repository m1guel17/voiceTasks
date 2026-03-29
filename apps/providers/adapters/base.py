"""
Abstract base adapters for ASR and LLM providers.

All concrete provider adapters must subclass the appropriate base class
and implement the required abstract methods.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class BaseASRAdapter(ABC):
    """
    Abstract base class for Speech-to-Text (ASR) providers.

    Subclasses implement transcribe() to call their respective APIs.
    """

    @abstractmethod
    def transcribe(self, audio_file, language: str = 'en') -> str:
        """
        Transcribe an audio file to text.

        Args:
            audio_file: A file-like object containing audio data.
            language: BCP-47 language code (e.g. 'en', 'es').

        Returns:
            Transcription string. Must not raise — return empty string on failure.
        """

    def test_connection(self) -> tuple[bool, str]:
        """
        Test the provider connection.

        Returns:
            (success: bool, message: str)
        """
        return True, 'Connection test not implemented for this provider.'


class BaseLLMAdapter(ABC):
    """
    Abstract base class for Large Language Model (LLM) providers.

    Subclasses implement complete() to call their respective APIs.
    """

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """
        Send a prompt and return the completion text.

        Args:
            prompt: The full prompt string to send to the LLM.
            **kwargs: Provider-specific optional parameters.

        Returns:
            Completion string. Must not raise — return empty string on failure.
        """

    def test_connection(self) -> tuple[bool, str]:
        """
        Test the provider connection.

        Returns:
            (success: bool, message: str)
        """
        return True, 'Connection test not implemented for this provider.'
