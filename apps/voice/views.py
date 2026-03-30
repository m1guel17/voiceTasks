"""
Voice views for VoiceTasks.

Handles audio file upload, transcription requests, and history display.
"""
import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from apps.providers.models import ProviderConfiguration

from .models import VoiceNote
from .services import ASRService

logger = logging.getLogger(__name__)
_asr_service = ASRService()

# Allowed audio MIME types
ALLOWED_AUDIO_TYPES = {
    'audio/webm',
    'audio/ogg',
    'audio/wav',
    'audio/mpeg',
    'audio/mp4',
    'audio/mp3',
    'audio/x-m4a',
    'audio/aac',
    'application/octet-stream',  # Some browsers send this for webm
}


def _validate_audio(uploaded_file) -> str | None:
    """
    Validate an uploaded audio file.

    Returns an error message string, or None if the file is valid.
    """
    if not uploaded_file:
        return 'No audio file provided.'
    if uploaded_file.size > 10 * 1024 * 1024:
        return 'Audio file exceeds 10 MB limit.'
    content_type = getattr(uploaded_file, 'content_type', 'application/octet-stream')
    if content_type not in ALLOWED_AUDIO_TYPES:
        # Be lenient — only hard-block obviously wrong types
        if content_type.startswith('text/') or content_type.startswith('image/'):
            return f'Invalid file type: {content_type}'
    return None


@require_POST
def transcribe(request):
    """
    POST /voice/transcribe/

    Multipart form fields:
        audio  — the recorded audio blob
        language — BCP-47 language code (default 'en')

    Returns JSON:
        {transcription: str, voice_note_id: int}
    """
    audio_file = request.FILES.get('audio')
    language = request.POST.get('language', 'en').strip() or 'en'

    error = _validate_audio(audio_file)
    if error:
        return JsonResponse({'error': error}, status=400)

    # Save the voice note record first (before transcription so we have an ID)
    voice_note = VoiceNote.objects.create(
        audio_file=audio_file,
        language=language,
    )

    pre_transcribed = request.POST.get('transcription', '').strip()
    active_asr_type = (
        ProviderConfiguration.objects.filter(
            category=ProviderConfiguration.CATEGORY_ASR,
            is_active=True,
        ).values_list('provider_type', flat=True).first()
    )

    if pre_transcribed and active_asr_type == 'web_speech_api':
        transcription = pre_transcribed
    else:
        transcription = _asr_service.transcribe(audio_file, language=language)

    voice_note.transcription = transcription
    voice_note.save(update_fields=['transcription'])

    logger.info('Saved VoiceNote pk=%d language=%s', voice_note.pk, language)

    return JsonResponse({
        'transcription': transcription,
        'voice_note_id': voice_note.pk,
    })


@require_GET
def voice_history(request):
    """
    GET /voice/history/

    Render the voice transcription history page.
    """
    notes = VoiceNote.objects.order_by('-created_at')[:50]
    return render(request, 'voice/history.html', {'voice_notes': notes})
