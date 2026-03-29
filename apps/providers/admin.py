"""Admin configuration for the providers app."""
from django.contrib import admin

from .models import ProviderConfiguration


@admin.register(ProviderConfiguration)
class ProviderConfigurationAdmin(admin.ModelAdmin):
    """Admin interface for ProviderConfiguration model."""

    list_display = ('provider_type', 'category', 'model', 'is_active', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('provider_type', 'model')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('provider_type', 'category', 'is_active')}),
        ('Connection', {'fields': ('api_key', 'endpoint', 'model')}),
        ('Parameters', {'fields': ('parameters',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
