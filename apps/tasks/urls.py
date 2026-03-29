"""URL configuration for the tasks app."""
from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    # Page views
    path('', views.kanban, name='kanban'),
    # JSON API endpoints
    path('list/', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('reorder/', views.task_reorder, name='task_reorder'),
    path('batch-create/', views.task_batch_create, name='task_batch_create'),
    path('<int:task_id>/update/', views.task_update, name='task_update'),
    path('<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('<int:task_id>/move/', views.task_move, name='task_move'),
]
