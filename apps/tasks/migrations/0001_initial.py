"""Initial migration for the tasks app."""
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    """Create the Task table."""

    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=80)),
                ('description', models.CharField(blank=True, default='', max_length=200)),
                ('status', models.CharField(
                    choices=[
                        ('OPEN', 'Open'),
                        ('PENDING', 'Pending'),
                        ('IN_PROGRESS', 'In Progress'),
                        ('REVIEW', 'Review'),
                        ('COMPLETED', 'Completed'),
                    ],
                    db_index=True,
                    default='OPEN',
                    max_length=20,
                )),
                ('priority', models.CharField(
                    choices=[
                        ('low', 'Low'),
                        ('medium', 'Medium'),
                        ('high', 'High'),
                    ],
                    db_index=True,
                    default='medium',
                    max_length=10,
                )),
                ('column_order', models.IntegerField(db_index=True, default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['column_order', 'created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(fields=['status', 'column_order'], name='tasks_task_status_column_idx'),
        ),
    ]
