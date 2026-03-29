"""Initial migration for the voice app."""
from django.db import migrations, models


class Migration(migrations.Migration):
    """Create the VoiceNote table."""

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='VoiceNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio_file', models.FileField(upload_to='voice_notes/')),
                ('language', models.CharField(default='en', max_length=10)),
                ('transcription', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
