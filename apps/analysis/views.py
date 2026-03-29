"""
Analysis views for VoiceTasks.

Handles LLM-powered task extraction from transcription text.
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services import LLMAnalysisService

logger = logging.getLogger(__name__)
_llm_service = LLMAnalysisService()


@require_POST
def extract_tasks(request):
    """
    POST /analysis/extract-tasks/

    Body (JSON): {text: '...', voice_note_id?: N}

    Returns JSON:
        {tasks: [{title, description, priority}, ...]}
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    text = data.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'text field is required.'}, status=400)

    try:
        tasks = _llm_service.extract_tasks(text)
    except Exception as exc:
        logger.exception('Unexpected error in extract_tasks view')
        return JsonResponse({'error': str(exc)}, status=500)

    return JsonResponse({'tasks': tasks})
