"""
Task model for VoiceTasks.

Represents a single actionable task on the Kanban board.
"""
from django.db import models


class Task(models.Model):
    """
    A single task displayed on the Kanban board.

    Tasks move through five status columns and carry a priority level.
    The column_order field controls ordering within each status column.
    """

    STATUS_OPEN = 'OPEN'
    STATUS_PENDING = 'PENDING'
    STATUS_IN_PROGRESS = 'IN_PROGRESS'
    STATUS_REVIEW = 'REVIEW'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_REVIEW, 'Review'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]

    title = models.CharField(max_length=80)
    description = models.CharField(max_length=200, blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
        db_index=True,
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        db_index=True,
    )
    column_order = models.IntegerField(default=0, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['column_order', 'created_at']
        indexes = [
            models.Index(fields=['status', 'column_order']),
        ]

    def __str__(self):
        return f'[{self.status}] {self.title}'

    def to_dict(self):
        """Return a JSON-serializable dictionary representation."""
        return {
            'id': self.pk,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'column_order': self.column_order,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
