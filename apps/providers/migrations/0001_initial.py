"""Initial migration for the providers app."""
from django.db import migrations, models


class Migration(migrations.Migration):
    """Create the ProviderConfiguration table."""

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ProviderConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_type', models.CharField(
                    choices=[
                        ('mock', 'Mock / Test'),
                        ('openai_whisper', 'OpenAI Whisper'),
                        ('azure_speech', 'Azure Speech'),
                        ('google_speech', 'Google Cloud Speech'),
                        ('custom_asr', 'Custom OpenAI-compatible ASR'),
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
                    ],
                    max_length=50,
                )),
                ('category', models.CharField(
                    choices=[('ASR', 'Speech Recognition (ASR)'), ('LLM', 'Language Model (LLM)')],
                    db_index=True,
                    max_length=10,
                )),
                ('api_key', models.CharField(blank=True, default='', max_length=500)),
                ('endpoint', models.URLField(blank=True, default='', max_length=500)),
                ('model', models.CharField(blank=True, default='', max_length=100)),
                ('parameters', models.JSONField(blank=True, default=dict)),
                ('is_active', models.BooleanField(db_index=True, default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['category', 'provider_type'],
            },
        ),
    ]
