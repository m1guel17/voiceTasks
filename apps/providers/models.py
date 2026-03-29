"""
ProviderConfiguration model for VoiceTasks.

Stores configuration for ASR (speech-to-text) and LLM providers.
API keys are stored server-side only — never exposed to the browser.
"""
from django.db import models


class ProviderConfiguration(models.Model):
    """
    Configuration record for a single ASR or LLM provider.

    Only one configuration per category (ASR/LLM) should have
    is_active=True at a time. The ProviderFactory enforces this.
    """

    CATEGORY_ASR = 'ASR'
    CATEGORY_LLM = 'LLM'

    CATEGORY_CHOICES = [
        (CATEGORY_ASR, 'Speech Recognition (ASR)'),
        (CATEGORY_LLM, 'Language Model (LLM)'),
    ]

    # Recognised provider type slugs
    PROVIDER_TYPE_CHOICES = [
        # ASR providers
        ('mock', 'Mock / Test'),
        ('openai_whisper', 'OpenAI Whisper'),
        ('azure_speech', 'Azure Speech'),
        ('google_speech', 'Google Cloud Speech'),
        ('custom_asr', 'Custom OpenAI-compatible ASR'),
        # LLM providers
        ('openai', 'OpenAI'),
        ('azure_openai', 'Azure OpenAI'),
        ('anthropic', 'Anthropic Claude'),
        ('google_gemini', 'Google Gemini'),
        ('deepseek', 'DeepSeek'),
        ('qwen', 'Qwen'),
        ('groq', 'Groq'),
        ('mistral', 'Mistral'),
        ('ollama', 'Ollama'),
        ('custom_llm', 'Custom OpenAI-compatible LLM'),
    ]

    provider_type = models.CharField(
        max_length=50,
        choices=PROVIDER_TYPE_CHOICES,
    )
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        db_index=True,
    )
    api_key = models.CharField(max_length=500, blank=True, default='')
    endpoint = models.URLField(max_length=500, blank=True, default='')
    model = models.CharField(max_length=100, blank=True, default='')
    parameters = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['category', 'provider_type']

    def __str__(self):
        active_marker = ' [ACTIVE]' if self.is_active else ''
        return f'{self.get_category_display()} — {self.get_provider_type_display()}{active_marker}'

    @property
    def parameters_json_display(self) -> str:
        """Return the parameters field formatted as a JSON string for form display."""
        import json
        return json.dumps(self.parameters, indent=2) if self.parameters else '{}'

    def to_dict(self, include_key: bool = False) -> dict:
        """
        Return a JSON-serializable dict.

        Args:
            include_key: If True, include the api_key (default False for
                         security — never send keys to the browser).
        """
        data = {
            'id': self.pk,
            'provider_type': self.provider_type,
            'category': self.category,
            'endpoint': self.endpoint,
            'model': self.model,
            'parameters': self.parameters,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_key:
            data['api_key'] = self.api_key
        return data
