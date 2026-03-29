"""
Task views for VoiceTasks.

All data-mutation endpoints return JSON so they can be consumed by
HTMX partial updates and vanilla JS (kanban.js).
"""
import json
import logging
from collections import defaultdict

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Task
from .services import TaskService

logger = logging.getLogger(__name__)
_service = TaskService()


def _parse_json_body(request) -> dict:
    """Parse the request body as JSON. Returns empty dict on failure."""
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}


# ---------------------------------------------------------------------------
# Read views
# ---------------------------------------------------------------------------

@require_GET
def task_list(request):
    """
    GET /tasks/list/

    Return all tasks grouped by status as JSON.
    """
    status_columns = ['OPEN', 'PENDING', 'IN_PROGRESS', 'REVIEW', 'COMPLETED']
    result = {}
    for status in status_columns:
        result[status] = [
            t.to_dict()
            for t in Task.objects.filter(status=status).order_by('column_order', 'created_at')
        ]
    return JsonResponse({'tasks': result})


def kanban(request):
    """
    GET /tasks/

    Render the standalone Kanban board page.
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
    tasks_json = json.dumps({
        status: [t.to_dict() for t in tasks]
        for status, tasks in tasks_by_status.items()
    })

    return render(
        request,
        'tasks/kanban.html',
        {
            'tasks_by_status': tasks_by_status,
            'tasks_json': tasks_json,
            'status_columns': status_columns,
            'status_labels': status_labels,
        },
    )


# ---------------------------------------------------------------------------
# Write views
# ---------------------------------------------------------------------------

@require_POST
def task_create(request):
    """
    POST /tasks/create/

    Body (JSON): {title, description?, status?, priority?}
    Returns: task JSON with HTTP 201.
    """
    data = _parse_json_body(request)
    if not data:
        # Also accept form-encoded data
        data = {
            'title': request.POST.get('title', ''),
            'description': request.POST.get('description', ''),
            'status': request.POST.get('status', 'OPEN'),
            'priority': request.POST.get('priority', 'medium'),
        }

    title = data.get('title', '').strip()
    if not title:
        return JsonResponse({'error': 'Title is required.'}, status=400)

    task = _service.create_task(
        title=title,
        description=data.get('description', ''),
        status=data.get('status', 'OPEN'),
        priority=data.get('priority', 'medium'),
    )
    return JsonResponse({'task': task.to_dict()}, status=201)


@require_POST
def task_update(request, task_id):
    """
    POST /tasks/<task_id>/update/

    Body (JSON): any subset of {title, description, status, priority, column_order}
    Returns: updated task JSON.
    """
    data = _parse_json_body(request)
    if not data:
        data = dict(request.POST)
        # Flatten single-value lists from QueryDict
        data = {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in data.items()}

    try:
        task = _service.update_task(task_id, **data)
    except Exception as exc:
        logger.exception('Error updating task %s', task_id)
        return JsonResponse({'error': str(exc)}, status=400)

    return JsonResponse({'task': task.to_dict()})


@require_POST
def task_delete(request, task_id):
    """
    POST /tasks/<task_id>/delete/

    Returns: {'success': True}
    """
    try:
        _service.delete_task(task_id)
    except Exception as exc:
        logger.exception('Error deleting task %s', task_id)
        return JsonResponse({'error': str(exc)}, status=400)

    return JsonResponse({'success': True})


@require_POST
def task_move(request, task_id):
    """
    POST /tasks/<task_id>/move/

    Body (JSON): {status: '...', column_order?: N}
    Returns: updated task JSON.
    """
    data = _parse_json_body(request)
    new_status = data.get('status')
    if not new_status:
        return JsonResponse({'error': 'status is required.'}, status=400)

    column_order = data.get('column_order')
    if column_order is not None:
        try:
            column_order = int(column_order)
        except (TypeError, ValueError):
            column_order = None

    try:
        task = _service.move_task(task_id, new_status, column_order)
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
    except Exception as exc:
        logger.exception('Error moving task %s', task_id)
        return JsonResponse({'error': str(exc)}, status=500)

    return JsonResponse({'task': task.to_dict()})


@require_POST
def task_reorder(request):
    """
    POST /tasks/reorder/

    Body (JSON): {tasks: [{id: N, column_order: N}, ...]}
    Returns: {'success': True}
    """
    data = _parse_json_body(request)
    task_orders = data.get('tasks', [])
    if not isinstance(task_orders, list):
        return JsonResponse({'error': 'tasks must be a list.'}, status=400)

    try:
        _service.reorder_tasks(task_orders)
    except Exception as exc:
        logger.exception('Error reordering tasks')
        return JsonResponse({'error': str(exc)}, status=500)

    return JsonResponse({'success': True})


@require_POST
def task_batch_create(request):
    """
    POST /tasks/batch-create/

    Body (JSON): {tasks: [{title, description?, priority?}, ...]}
    Returns: {'tasks': [task, ...], 'count': N}
    """
    data = _parse_json_body(request)
    tasks_data = data.get('tasks', [])
    if not isinstance(tasks_data, list) or not tasks_data:
        return JsonResponse({'error': 'tasks list is required and must not be empty.'}, status=400)

    try:
        created = _service.batch_create(tasks_data)
    except Exception as exc:
        logger.exception('Error batch-creating tasks')
        return JsonResponse({'error': str(exc)}, status=500)

    return JsonResponse(
        {'tasks': [t.to_dict() for t in created], 'count': len(created)},
        status=201,
    )
