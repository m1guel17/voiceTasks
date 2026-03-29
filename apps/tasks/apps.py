"""AppConfig for the tasks app."""
from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Tasks app: Kanban board, CRUD operations, and bulk task management."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'
    label = 'tasks'
