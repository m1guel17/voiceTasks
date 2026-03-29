"""
Mock provider adapters for VoiceTasks.

The mock adapters work with zero configuration and are the default
fallback when no real provider is configured. Useful for development
and testing without external API keys.
"""
from __future__ import annotations

import json
import logging

from .base import BaseASRAdapter, BaseLLMAdapter

logger = logging.getLogger(__name__)

_MOCK_TRANSCRIPTION = (
    "This is a mock transcription. "
    "I need to schedule a team meeting for tomorrow afternoon to discuss the project roadmap. "
    "Also, please review the quarterly report and send follow-up emails to the client. "
    "It's urgent that we fix the login bug on the production server as soon as possible."
)

_MOCK_TASKS_JSON = json.dumps({
    "tasks": [
        {
            "title": "Schedule team meeting for project roadmap discussion",
            "description": "Organize a team meeting for tomorrow afternoon to discuss project roadmap and upcoming milestones.",
            "priority": "medium"
        },
        {
            "title": "Review quarterly report",
            "description": "Review the quarterly report and prepare summary notes before sending to stakeholders.",
            "priority": "medium"
        },
        {
            "title": "Send follow-up emails to client",
            "description": "Draft and send follow-up emails to the client regarding recent project updates.",
            "priority": "medium"
        },
        {
            "title": "Fix login bug on production server",
            "description": "Investigate and resolve the login bug affecting production users. Mark as urgent.",
            "priority": "high"
        }
    ]
})


class MockASRAdapter(BaseASRAdapter):
    """
    Mock ASR adapter that returns a canned transcription.

    No network calls are made. Requires no API keys.
    """

    def transcribe(self, audio_file, language: str = 'en') -> str:
        """
        Return a pre-defined mock transcription.

        Args:
            audio_file: Ignored.
            language: Ignored.

        Returns:
            A realistic mock transcription string.
        """
        logger.debug('MockASRAdapter.transcribe() called (no real API call)')
        return _MOCK_TRANSCRIPTION

    def test_connection(self) -> tuple[bool, str]:
        return True, 'Mock ASR provider is always available.'


class MockLLMAdapter(BaseLLMAdapter):
    """
    Mock LLM adapter that returns a canned task extraction JSON response.

    No network calls are made. Requires no API keys.
    """

    def complete(self, prompt: str, **kwargs) -> str:
        """
        Return a pre-defined mock JSON task extraction response.

        Args:
            prompt: Ignored.
            **kwargs: Ignored.

        Returns:
            Valid JSON string with 4 extracted tasks.
        """
        logger.debug('MockLLMAdapter.complete() called (no real API call)')
        return _MOCK_TASKS_JSON

    def test_connection(self) -> tuple[bool, str]:
        return True, 'Mock LLM provider is always available.'
