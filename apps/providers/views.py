"""
Provider views for VoiceTasks.

Handles provider connection testing.
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .factory import ProviderFactory
from .models import ProviderConfiguration

logger = logging.getLogger(__name__)


@require_POST
def test_connection(request):
    """
    POST /providers/test/

    Body (JSON): {provider_id: N}

    Tests the connection for the given provider configuration.
    Returns: {success: bool, message: str}
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON body.'}, status=400)

    provider_id = data.get('provider_id')
    if not provider_id:
        return JsonResponse({'error': 'provider_id is required.'}, status=400)

    try:
        config = ProviderConfiguration.objects.get(pk=provider_id)
    except ProviderConfiguration.DoesNotExist:
        return JsonResponse({'error': 'Provider not found.'}, status=404)

    try:
        if config.category == ProviderConfiguration.CATEGORY_ASR:
            adapter = ProviderFactory.get_asr_adapter(config)
        else:
            adapter = ProviderFactory.get_llm_adapter(config)

        success, message = adapter.test_connection()
    except Exception as exc:
        logger.exception('Error testing provider %s', provider_id)
        return JsonResponse({'success': False, 'message': str(exc)})

    return JsonResponse({'success': success, 'message': message})
