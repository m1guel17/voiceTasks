"""
Provider factory for VoiceTasks.

Resolves ProviderConfiguration records to concrete adapter instances.
Falls back to mock adapters when no real provider is configured or
when the configured provider fails to instantiate.
"""
from __future__ import annotations

import logging

from .adapters.base import BaseASRAdapter, BaseLLMAdapter
from .adapters.mock import MockASRAdapter, MockLLMAdapter
from .adapters.openai_asr import OpenAIASRAdapter
from .adapters.openai_llm import OpenAILLMAdapter
from .adapters.vosk_asr import VoskASRAdapter
from .adapters.web_speech import WebSpeechASRAdapter

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    Factory for creating provider adapter instances.

    Maps provider_type slugs to adapter classes and handles
    instantiation with the correct configuration parameters.
    """

    # Mapping from provider_type slug to ASR adapter class
    ASR_ADAPTERS: dict[str, type[BaseASRAdapter]] = {
        'mock': MockASRAdapter,
        'openai_whisper': OpenAIASRAdapter,
        'custom_asr': OpenAIASRAdapter,  # Custom OpenAI-compatible endpoints
        'vosk': VoskASRAdapter,
        'web_speech_api': WebSpeechASRAdapter,
    }

    # Mapping from provider_type slug to LLM adapter class
    LLM_ADAPTERS: dict[str, type[BaseLLMAdapter]] = {
        'mock': MockLLMAdapter,
        'openai': OpenAILLMAdapter,
        'azure_openai': OpenAILLMAdapter,    # Azure OpenAI is API-compatible
        'deepseek': OpenAILLMAdapter,         # DeepSeek is OpenAI-compatible
        'qwen': OpenAILLMAdapter,             # Qwen is OpenAI-compatible
        'groq': OpenAILLMAdapter,             # Groq is OpenAI-compatible
        'mistral': OpenAILLMAdapter,          # Mistral is OpenAI-compatible
        'ollama': OpenAILLMAdapter,           # Ollama exposes OpenAI-compatible API
        'custom_llm': OpenAILLMAdapter,       # Custom OpenAI-compatible endpoint
    }

    @classmethod
    def get_asr_adapter(cls, config) -> BaseASRAdapter:
        """
        Create an ASR adapter from a ProviderConfiguration instance.

        Args:
            config: ProviderConfiguration model instance.

        Returns:
            Concrete BaseASRAdapter instance.

        Raises:
            ValueError: If the provider_type is not registered.
        """
        adapter_class = cls.ASR_ADAPTERS.get(config.provider_type)
        if adapter_class is None:
            raise ValueError(
                f'Unknown ASR provider type: {config.provider_type!r}. '
                f'Registered types: {list(cls.ASR_ADAPTERS.keys())}'
            )
        return adapter_class(
            api_key=config.api_key,
            model=config.model,
            endpoint=config.endpoint,
            parameters=config.parameters,
        )

    @classmethod
    def get_llm_adapter(cls, config) -> BaseLLMAdapter:
        """
        Create an LLM adapter from a ProviderConfiguration instance.

        Args:
            config: ProviderConfiguration model instance.

        Returns:
            Concrete BaseLLMAdapter instance.

        Raises:
            ValueError: If the provider_type is not registered.
        """
        adapter_class = cls.LLM_ADAPTERS.get(config.provider_type)
        if adapter_class is None:
            raise ValueError(
                f'Unknown LLM provider type: {config.provider_type!r}. '
                f'Registered types: {list(cls.LLM_ADAPTERS.keys())}'
            )
        return adapter_class(
            api_key=config.api_key,
            model=config.model,
            endpoint=config.endpoint,
            parameters=config.parameters,
        )

    @classmethod
    def get_active_asr(cls) -> BaseASRAdapter:
        """
        Return the active ASR adapter.

        Queries the database for the active ASR configuration.
        Falls back to MockASRAdapter if none is found or instantiation fails.

        Returns:
            Active BaseASRAdapter instance (never raises).
        """
        try:
            from .models import ProviderConfiguration

            config = ProviderConfiguration.objects.filter(
                category=ProviderConfiguration.CATEGORY_ASR,
                is_active=True,
            ).first()

            if config is None:
                logger.debug('No active ASR provider configured; using mock')
                return MockASRAdapter()

            adapter = cls.get_asr_adapter(config)
            logger.debug('Using ASR adapter: %s', config.provider_type)
            return adapter

        except Exception:
            logger.exception('Failed to load active ASR adapter; falling back to mock')
            return MockASRAdapter()

    @classmethod
    def get_active_llm(cls) -> BaseLLMAdapter:
        """
        Return the active LLM adapter.

        Queries the database for the active LLM configuration.
        Falls back to MockLLMAdapter if none is found or instantiation fails.

        Returns:
            Active BaseLLMAdapter instance (never raises).
        """
        try:
            from .models import ProviderConfiguration

            config = ProviderConfiguration.objects.filter(
                category=ProviderConfiguration.CATEGORY_LLM,
                is_active=True,
            ).first()

            if config is None:
                logger.debug('No active LLM provider configured; using mock')
                return MockLLMAdapter()

            adapter = cls.get_llm_adapter(config)
            logger.debug('Using LLM adapter: %s', config.provider_type)
            return adapter

        except Exception:
            logger.exception('Failed to load active LLM adapter; falling back to mock')
            return MockLLMAdapter()
