"""
LLM analysis service for VoiceTasks.

Extracts structured task data from free-form transcription text
using the active LLM provider. Falls back gracefully on any error.
"""
from __future__ import annotations

import json
import logging
import re

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are a task extraction assistant for a personal productivity app.

Analyze the following voice transcription and extract all actionable tasks mentioned.

Rules:
- Infer implicit tasks even when not explicitly stated as commands
- Split multiple separate actions into individual tasks
- Each task must have:
  * title: concise action-oriented string, maximum 80 characters
  * description: brief context or detail, maximum 200 characters
  * priority: one of exactly "low", "medium", or "high"
- Assign priority based on urgency cues (words like "urgent", "asap", "critical" → high; "when you can", "sometime" → low; default → medium)
- Return ONLY valid JSON — no markdown, no extra text, no code fences
- Required JSON format: {{"tasks": [{{"title": "...", "description": "...", "priority": "low|medium|high"}}]}}

Transcription:
{text}"""

VALID_PRIORITIES = {'low', 'medium', 'high'}


class LLMAnalysisService:
    """
    Service for extracting actionable tasks from transcribed text.

    Uses the active LLM provider via ProviderFactory. Falls back to a
    single raw task if the LLM response cannot be parsed.
    """

    def extract_tasks(self, text: str) -> list[dict]:
        """
        Extract tasks from transcription text.

        Args:
            text: The transcription string to analyze.

        Returns:
            A list of task dicts each with keys: title, description, priority.
            Never raises — always returns at least a fallback task.
        """
        if not text or not text.strip():
            return []

        from apps.providers.factory import ProviderFactory

        try:
            adapter = ProviderFactory.get_active_llm()
            prompt = EXTRACTION_PROMPT.format(text=text.strip())
            response = adapter.complete(prompt)
            tasks = self._parse_response(response, fallback_text=text)
        except Exception:
            logger.exception('LLM extraction failed; using fallback task')
            tasks = self._fallback_task(text)

        return tasks

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_response(self, response: str, fallback_text: str) -> list[dict]:
        """
        Parse and validate the LLM JSON response.

        Tries several strategies:
        1. Direct JSON parse of the full response
        2. Extract first {...} block with regex
        3. Fall back to a single raw task

        Args:
            response: Raw string returned by the LLM adapter.
            fallback_text: Original transcription used as fallback title.

        Returns:
            List of validated task dicts.
        """
        if not response:
            return self._fallback_task(fallback_text)

        # Strategy 1: direct parse
        parsed = self._try_json_parse(response)

        # Strategy 2: extract JSON block
        if parsed is None:
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                parsed = self._try_json_parse(match.group())

        if parsed is None:
            logger.warning('Could not parse LLM response as JSON; using fallback')
            return self._fallback_task(fallback_text)

        raw_tasks = parsed.get('tasks')
        if not isinstance(raw_tasks, list) or not raw_tasks:
            logger.warning('LLM response missing tasks list; using fallback')
            return self._fallback_task(fallback_text)

        validated = []
        for item in raw_tasks:
            task = self._validate_task(item)
            if task:
                validated.append(task)

        return validated if validated else self._fallback_task(fallback_text)

    def _try_json_parse(self, text: str) -> dict | None:
        """Attempt to parse text as JSON. Returns None on failure."""
        try:
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return None

    def _validate_task(self, item: dict) -> dict | None:
        """
        Validate and normalise a single task dict from the LLM.

        Returns a clean dict or None if the item is unusable.
        """
        if not isinstance(item, dict):
            return None

        title = str(item.get('title', '')).strip()[:80]
        if not title:
            return None

        description = str(item.get('description', '')).strip()[:200]
        priority = str(item.get('priority', 'medium')).strip().lower()
        if priority not in VALID_PRIORITIES:
            priority = 'medium'

        return {'title': title, 'description': description, 'priority': priority}

    def _fallback_task(self, text: str) -> list[dict]:
        """
        Create a single fallback task from the raw transcription.

        Used when the LLM response cannot be parsed.
        """
        title = text.strip()[:80]
        description = text.strip()[:200] if len(text.strip()) > 80 else ''
        return [{'title': title, 'description': description, 'priority': 'medium'}]
