"""
Settings UI views for VoiceTasks.

Provides the provider configuration management interface.
"""
import logging

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.providers.models import ProviderConfiguration

from .forms import ProviderConfigurationForm

logger = logging.getLogger(__name__)


def provider_settings(request):
    """
    GET /settings/

    Display all provider configurations grouped by category.
    Also renders the 'Add new provider' form inline.
    """
    asr_providers = ProviderConfiguration.objects.filter(
        category=ProviderConfiguration.CATEGORY_ASR
    ).order_by('provider_type')

    llm_providers = ProviderConfiguration.objects.filter(
        category=ProviderConfiguration.CATEGORY_LLM
    ).order_by('provider_type')

    add_form = ProviderConfigurationForm()

    return render(
        request,
        'settings/providers.html',
        {
            'asr_providers': asr_providers,
            'llm_providers': llm_providers,
            'add_form': add_form,
        },
    )


@require_POST
def provider_create(request):
    """
    POST /settings/create/

    Create a new provider configuration.
    If is_active is set, deactivate all other configs in the same category.
    """
    form = ProviderConfigurationForm(request.POST)
    if form.is_valid():
        with transaction.atomic():
            provider = form.save(commit=False)
            if provider.is_active:
                # Enforce only one active provider per category
                ProviderConfiguration.objects.filter(
                    category=provider.category
                ).update(is_active=False)
            provider.save()
        messages.success(request, f'Provider "{provider.get_provider_type_display()}" created.')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')

    return redirect('settings_ui:providers')


@require_POST
def provider_update(request, provider_id):
    """
    POST /settings/<provider_id>/update/

    Update an existing provider configuration.
    """
    config = get_object_or_404(ProviderConfiguration, pk=provider_id)
    form = ProviderConfigurationForm(request.POST, instance=config)

    if form.is_valid():
        with transaction.atomic():
            provider = form.save(commit=False)
            if provider.is_active:
                ProviderConfiguration.objects.filter(
                    category=provider.category
                ).exclude(pk=provider_id).update(is_active=False)
            provider.save()
        messages.success(request, f'Provider "{provider.get_provider_type_display()}" updated.')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')

    return redirect('settings_ui:providers')


@require_POST
def provider_delete(request, provider_id):
    """
    POST /settings/<provider_id>/delete/

    Delete a provider configuration.
    """
    config = get_object_or_404(ProviderConfiguration, pk=provider_id)
    display_name = config.get_provider_type_display()
    config.delete()
    messages.success(request, f'Provider "{display_name}" deleted.')
    return redirect('settings_ui:providers')
