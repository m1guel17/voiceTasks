"""
Core views for VoiceTasks.

The dashboard is the primary entry point, combining:
- Voice recorder panel
- Extracted tasks preview
- Kanban board
"""
import json

from django.shortcuts import render

from apps.tasks.models import Task
from apps.voice.models import VoiceNote


def dashboard(request):
    """
    Main dashboard view.

    Renders the voice panel, extracted task preview, and Kanban board
    with tasks grouped by their status column.
    """
    status_columns = ['OPEN', 'PENDING', 'IN_PROGRESS', 'REVIEW', 'COMPLETED']
    status_labels = {
        'OPEN': 'Open',
        'PENDING': 'Pending',
        'IN_PROGRESS': 'In Progress',
        'REVIEW': 'Review',
        'COMPLETED': 'Completed',
    }

    tasks_by_status = {
        status: list(
            Task.objects.filter(status=status).order_by('column_order', 'created_at')
        )
        for status in status_columns
    }

    recent_voice_notes = list(VoiceNote.objects.order_by('-created_at')[:5])

    task_counts = {status: len(tasks) for status, tasks in tasks_by_status.items()}
    total_tasks = sum(task_counts.values())

    # JSON representation for the JavaScript kanban initializer
    tasks_json = json.dumps({
        status: [t.to_dict() for t in tasks]
        for status, tasks in tasks_by_status.items()
    })

    return render(
        request,
        'dashboard/index.html',
        {
            'tasks_by_status': tasks_by_status,
            'tasks_json': tasks_json,
            'recent_voice_notes': recent_voice_notes,
            'status_columns': status_columns,
            'status_labels': status_labels,
            'task_counts': task_counts,
            'total_tasks': total_tasks,
        },
    )
