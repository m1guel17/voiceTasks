"""
Task service layer for VoiceTasks.

Encapsulates all business logic for creating, updating, moving,
reordering, and bulk-creating tasks. Views should call these methods
rather than manipulating models directly.
"""
from __future__ import annotations

from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Task


class TaskService:
    """Service class providing task CRUD and bulk operations."""

    # Valid status values
    VALID_STATUSES = {c[0] for c in Task.STATUS_CHOICES}
    # Valid priority values
    VALID_PRIORITIES = {c[0] for c in Task.PRIORITY_CHOICES}

    def create_task(
        self,
        title: str,
        description: str = '',
        status: str = Task.STATUS_OPEN,
        priority: str = Task.PRIORITY_MEDIUM,
        column_order: int | None = None,
    ) -> Task:
        """
        Create and persist a new task.

        Args:
            title: Task title (max 80 chars).
            description: Optional short description (max 200 chars).
            status: Initial Kanban column status.
            priority: Task priority level.
            column_order: Position within column; auto-appends if None.

        Returns:
            The newly created Task instance.
        """
        if status not in self.VALID_STATUSES:
            status = Task.STATUS_OPEN
        if priority not in self.VALID_PRIORITIES:
            priority = Task.PRIORITY_MEDIUM

        if column_order is None:
            max_order = (
                Task.objects.filter(status=status)
                .order_by('-column_order')
                .values_list('column_order', flat=True)
                .first()
            )
            column_order = (max_order or 0) + 1

        return Task.objects.create(
            title=title[:80],
            description=description[:200],
            status=status,
            priority=priority,
            column_order=column_order,
        )

    def update_task(self, task_id: int, **kwargs: Any) -> Task:
        """
        Update fields on an existing task.

        Only known, safe fields are applied. Unknown kwargs are ignored.

        Args:
            task_id: PK of the task to update.
            **kwargs: Fields to update (title, description, status, priority,
                      column_order).

        Returns:
            The updated Task instance.
        """
        task = get_object_or_404(Task, pk=task_id)

        allowed_fields = {'title', 'description', 'status', 'priority', 'column_order'}
        update_fields = []

        for field, value in kwargs.items():
            if field not in allowed_fields:
                continue
            if field == 'title':
                task.title = str(value)[:80]
            elif field == 'description':
                task.description = str(value)[:200]
            elif field == 'status' and value in self.VALID_STATUSES:
                task.status = value
            elif field == 'priority' and value in self.VALID_PRIORITIES:
                task.priority = value
            elif field == 'column_order':
                task.column_order = int(value)
            else:
                continue
            update_fields.append(field)

        if update_fields:
            task.save(update_fields=update_fields)

        return task

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task by primary key.

        Args:
            task_id: PK of the task to delete.
        """
        task = get_object_or_404(Task, pk=task_id)
        task.delete()

    def move_task(
        self,
        task_id: int,
        new_status: str,
        column_order: int | None = None,
    ) -> Task:
        """
        Move a task to a different status column.

        When column_order is None the task is appended to the end of
        the target column.

        Args:
            task_id: PK of the task to move.
            new_status: Target column status value.
            column_order: Position in the new column (optional).

        Returns:
            The updated Task instance.
        """
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f'Invalid status: {new_status}')

        task = get_object_or_404(Task, pk=task_id)

        if column_order is None:
            max_order = (
                Task.objects.filter(status=new_status)
                .exclude(pk=task_id)
                .order_by('-column_order')
                .values_list('column_order', flat=True)
                .first()
            )
            column_order = (max_order or 0) + 1

        task.status = new_status
        task.column_order = column_order
        task.save(update_fields=['status', 'column_order'])
        return task

    @transaction.atomic
    def reorder_tasks(self, task_orders: list[dict]) -> None:
        """
        Bulk-update column_order for multiple tasks atomically.

        Args:
            task_orders: List of dicts each with keys 'id' and 'column_order'.
        """
        for item in task_orders:
            Task.objects.filter(pk=item['id']).update(column_order=item['column_order'])

    @transaction.atomic
    def batch_create(self, tasks_data: list[dict]) -> list[Task]:
        """
        Create multiple tasks in a single atomic transaction.

        Args:
            tasks_data: List of dicts with keys title, description, priority.

        Returns:
            List of created Task instances.
        """
        created = []
        for idx, data in enumerate(tasks_data):
            task = Task.objects.create(
                title=str(data.get('title', 'Untitled'))[:80],
                description=str(data.get('description', ''))[:200],
                status=Task.STATUS_OPEN,
                priority=data.get('priority', Task.PRIORITY_MEDIUM)
                if data.get('priority') in self.VALID_PRIORITIES
                else Task.PRIORITY_MEDIUM,
                column_order=idx,
            )
            created.append(task)
        return created
