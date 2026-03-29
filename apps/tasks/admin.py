"""Admin configuration for the tasks app."""
from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin interface for Task model."""

    list_display = ('title', 'status', 'priority', 'column_order', 'created_at', 'updated_at')
    list_filter = ('status', 'priority')
    search_fields = ('title', 'description')
    ordering = ('status', 'column_order')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'description')}),
        ('Status & Priority', {'fields': ('status', 'priority', 'column_order')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
