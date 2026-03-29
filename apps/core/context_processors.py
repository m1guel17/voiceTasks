"""
Template context processors for the core app.

Injects global template variables available in every template.
"""
from django.urls import reverse_lazy


def app_context(request):
    """
    Inject app-wide context into every template.

    Returns:
        dict: Context variables including app name and navigation links.
    """
    nav_links = [
        {
            'label': 'Dashboard',
            'url': reverse_lazy('core:dashboard'),
            'icon': 'home',
        },
        {
            'label': 'Tasks',
            'url': reverse_lazy('tasks:kanban'),
            'icon': 'layout',
        },
        {
            'label': 'Voice History',
            'url': reverse_lazy('voice:history'),
            'icon': 'mic',
        },
        {
            'label': 'Settings',
            'url': reverse_lazy('settings_ui:providers'),
            'icon': 'settings',
        },
    ]

    return {
        'app_name': 'VoiceTasks',
        'nav_links': nav_links,
    }
