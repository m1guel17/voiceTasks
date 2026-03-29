"""
OpenAI Chat Completion LLM adapter for VoiceTasks.

Supports OpenAI models (GPT-4o, GPT-4, GPT-3.5-turbo) and any
provider with an OpenAI-compatible chat completions API (Groq, Mistral,
DeepSeek, Qwen, Ollama, Azure OpenAI, etc.).
"""
from __future__ import annotations

import logging

from .base import BaseLLMAdapter

logger = logging.getLogger(__name__)


class OpenAILLMAdapter(BaseLLMAdapter):
    """
    LLM adapter using the OpenAI chat completions API.

    Compatible with any OpenAI-compatible endpoint by setting a
    custom base_url (endpoint).

    Args:
        api_key: Provider API key.
        model: Model identifier (default 'gpt-4o-mini').
        endpoint: Optional base URL for custom/compatible providers.
        parameters: Additional parameters forwarded to the API call
                    (e.g. temperature, max_tokens).
    """

    DEFAULT_MODEL = 'gpt-4o-mini'

    def __init__(
        self,
        api_key: str,
        model: str = '',
        endpoint: str = '',
        parameters: dict | None = None,
        **kwargs,
    ):
        self.api_key = api_key
        self.model = model or self.DEFAULT_MODEL
        self.endpoint = endpoint or None
        self.parameters = parameters or {}

    def _get_client(self):
        """Instantiate and return the openai client."""
        try:
            import openai
        except ImportError as exc:
            raise ImportError(
                'openai package is required for OpenAILLMAdapter. '
                'Install it with: pip install openai'
            ) from exc

        kwargs = {'api_key': self.api_key}
        if self.endpoint:
            kwargs['base_url'] = self.endpoint
        return openai.OpenAI(**kwargs)

    def complete(self, prompt: str, **kwargs) -> str:
        """
        Send a prompt via chat completions and return the response text.

        Args:
            prompt: The full prompt to send as a user message.
            **kwargs: Additional completion parameters (override self.parameters).

        Returns:
            The model's response content string.
        """
        client = self._get_client()

        call_params = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': """
                        Eres un asistente experto en gestión de proyectos y productividad. Tu tarea es analizar el texto del usuario y extraer tareas accionables y claras.

                        REGLAS IMPORTANTES:
                        1. Incluso si el usuario no menciona tareas explícitamente, debes inferir qué acciones podrían derivarse del texto.
                        2. Divide el contenido en múltiples tareas si hay diferentes acciones o temas.
                        3. Cada tarea debe tener un título claro y conciso (máximo 80 caracteres).
                        4. La descripción debe explicar brevemente qué hacer (máximo 200 caracteres).
                        5. Asigna prioridad: "low", "medium" o "high" basándote en la urgencia implícita.
                        6. Responde ÚNICAMENTE con un JSON válido con esta estructura:
                        {
                            "tasks": [
                                {
                                "title": "Título de la tarea",
                                "description": "Descripción breve de qué hacer",
                                "priority": "medium"
                                }
                            ]
                        }
                    """,
                },
                {'role': 'user', 'content': prompt},
            ],
            'temperature': self.parameters.get('temperature', 0.3),
            'max_tokens': self.parameters.get('max_tokens', 1000),
            'response_format': {'type': 'json_object'},
        }
        # Allow caller kwargs to override
        call_params.update(kwargs)

        response = client.chat.completions.create(**call_params)
        return response.choices[0].message.content or ''

    def test_connection(self) -> tuple[bool, str]:
        """Test by sending a minimal completion request."""
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': 'Say "ok" in JSON: {"status": "ok"}'}],
                max_tokens=20,
            )
            if response.choices:
                return True, f'Connection successful. Model: {self.model}'
            return False, 'Empty response from provider.'
        except Exception as exc:
            return False, f'Connection failed: {exc}'
