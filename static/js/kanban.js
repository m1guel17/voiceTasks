/**
 * kanban.js
 *
 * SortableJS-powered Kanban board for VoiceTasks.
 *
 * Responsibilities:
 * - Render task cards from window.TASKS_DATA (provided by the server template)
 * - Initialize SortableJS drag-and-drop on each column
 * - POST to /tasks/<id>/move/ on cross-column drops
 * - POST to /tasks/reorder/ on within-column reorders
 * - Handle inline card editing (title, description, priority)
 * - Handle task deletion
 */

'use strict';

const PRIORITY_COLORS = {
  low:    { badge: 'bg-green-100 text-green-700',  dot: 'bg-green-400'  },
  medium: { badge: 'bg-yellow-100 text-yellow-700', dot: 'bg-yellow-400' },
  high:   { badge: 'bg-red-100 text-red-700',       dot: 'bg-red-500'    },
};

// ============================================================
// HTML escape helper
// ============================================================
function escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g,  '&lt;')
    .replace(/>/g,  '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// ============================================================
// Create a task card DOM element
// ============================================================
function createTaskCard(task) {
  const pc = PRIORITY_COLORS[task.priority] || PRIORITY_COLORS.medium;

  const div = document.createElement('div');
  div.className = [
    'task-card',
    'group',
    'rounded-xl',
    'border',
    'border-stone-200',
    'bg-white',
    'p-3',
    'shadow-card',
    'cursor-grab',
    'active:cursor-grabbing',
    'select-none',
  ].join(' ');

  div.dataset.taskId  = task.id;
  div.dataset.status  = task.status;
  div.dataset.priority = task.priority;

  div.innerHTML = `
    <div class="flex items-start justify-between gap-2">
      <div class="flex-1 min-w-0 task-title-wrap">
        <p class="task-title text-xs font-semibold text-stone-900 leading-snug line-clamp-2"
           title="${escHtml(task.title)}">${escHtml(task.title)}</p>
        <input type="text"
               class="task-title-input hidden w-full rounded border border-blue-300 bg-blue-50 px-1.5 py-0.5
                      text-xs font-semibold text-stone-900 focus:outline-none"
               value="${escHtml(task.title)}" maxlength="80" />
      </div>
      <button class="delete-btn opacity-0 group-hover:opacity-100 shrink-0 rounded p-0.5 text-stone-300
                     hover:text-red-500 transition-opacity mt-0.5" title="Delete task" type="button">
        <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <div class="task-desc-wrap mt-1">
      <p class="task-desc text-xs text-stone-500 line-clamp-2${task.description ? '' : ' hidden'}"
         title="${escHtml(task.description)}">${escHtml(task.description)}</p>
      <input type="text"
             class="task-desc-input hidden w-full rounded border border-blue-200 bg-blue-50 px-1.5 py-0.5
                    text-xs text-stone-600 focus:outline-none"
             value="${escHtml(task.description)}" maxlength="200" placeholder="Description..." />
    </div>

    <div class="mt-2.5 flex items-center justify-between">
      <select class="priority-select rounded-md border-0 px-1.5 py-0.5 text-xs font-medium cursor-pointer
                     focus:outline-none focus:ring-1 focus:ring-blue-400 ${pc.badge}">
        <option value="low"    ${task.priority === 'low'    ? 'selected' : ''}>Low</option>
        <option value="medium" ${task.priority === 'medium' ? 'selected' : ''}>Medium</option>
        <option value="high"   ${task.priority === 'high'   ? 'selected' : ''}>High</option>
      </select>
      <div class="edit-controls hidden items-center gap-1">
        <button class="save-edit-btn rounded px-1.5 py-0.5 text-xs bg-blue-600 text-white hover:bg-blue-700" type="button">Save</button>
        <button class="cancel-edit-btn rounded px-1.5 py-0.5 text-xs text-stone-500 hover:bg-stone-100" type="button">×</button>
      </div>
    </div>
  `;

  // Wire up events
  wireCardEvents(div, task);
  return div;
}

// ============================================================
// Wire card interactions
// ============================================================
function wireCardEvents(card, task) {
  // Double-click to edit
  card.addEventListener('dblclick', (e) => {
    if (!e.target.closest('.delete-btn') && !e.target.closest('.priority-select')) {
      startEdit(card);
    }
  });

  // Delete
  card.querySelector('.delete-btn').addEventListener('click', async (e) => {
    e.stopPropagation();
    const taskId = card.dataset.taskId;
    if (!confirm('Delete this task?')) return;
    const data = await apiFetch(`/tasks/${taskId}/delete/`, {});
    if (data.success) {
      const col = card.parentElement;
      card.remove();
      updateColumnCount(col);
    }
  });

  // Priority change
  card.querySelector('.priority-select').addEventListener('change', async (e) => {
    e.stopPropagation();
    const newPriority = e.target.value;
    const taskId = card.dataset.taskId;
    const pc = PRIORITY_COLORS[newPriority] || PRIORITY_COLORS.medium;

    // Update badge color classes
    const sel = e.target;
    sel.className = sel.className.replace(/bg-\w+-100|text-\w+-700/g, '');
    sel.classList.add(...pc.badge.split(' '));

    card.dataset.priority = newPriority;
    await apiFetch(`/tasks/${taskId}/update/`, { priority: newPriority });
  });

  // Save edit
  card.querySelector('.save-edit-btn').addEventListener('click', () => saveEdit(card));

  // Cancel edit
  card.querySelector('.cancel-edit-btn').addEventListener('click', () => cancelEdit(card));

  // Enter key to save in inputs
  card.querySelectorAll('.task-title-input, .task-desc-input').forEach((input) => {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') saveEdit(card);
      if (e.key === 'Escape') cancelEdit(card);
    });
  });
}

// ============================================================
// Inline editing
// ============================================================
function startEdit(card) {
  card.querySelector('.task-title').classList.add('hidden');
  card.querySelector('.task-title-input').classList.remove('hidden');
  card.querySelector('.task-desc').classList.add('hidden');
  card.querySelector('.task-desc-input').classList.remove('hidden');
  card.querySelector('.edit-controls').classList.remove('hidden');
  card.querySelector('.edit-controls').classList.add('flex');
  card.querySelector('.task-title-input').focus();
  card.classList.add('cursor-default');
  card.classList.remove('cursor-grab');
}

async function saveEdit(card) {
  const taskId = card.dataset.taskId;
  const newTitle = card.querySelector('.task-title-input').value.trim();
  const newDesc  = card.querySelector('.task-desc-input').value.trim();

  if (!newTitle) {
    card.querySelector('.task-title-input').focus();
    return;
  }

  await apiFetch(`/tasks/${taskId}/update/`, { title: newTitle, description: newDesc });

  card.querySelector('.task-title').textContent = newTitle;
  card.querySelector('.task-title').title = newTitle;
  card.querySelector('.task-desc').textContent = newDesc;
  card.querySelector('.task-desc').title = newDesc;
  if (newDesc) {
    card.querySelector('.task-desc').classList.remove('hidden');
  }

  cancelEdit(card);
}

function cancelEdit(card) {
  card.querySelector('.task-title').classList.remove('hidden');
  card.querySelector('.task-title-input').classList.add('hidden');
  card.querySelector('.task-desc').classList.remove('hidden');
  card.querySelector('.task-desc-input').classList.add('hidden');
  card.querySelector('.edit-controls').classList.add('hidden');
  card.querySelector('.edit-controls').classList.remove('flex');
  card.classList.remove('cursor-default');
  card.classList.add('cursor-grab');
}

// ============================================================
// Column count badge
// ============================================================
function updateColumnCount(colEl) {
  if (!colEl) return;
  const status = colEl.dataset.status;
  const badge = document.getElementById(`count-${status}`);
  if (badge) {
    badge.textContent = colEl.children.length;
  }
}

// ============================================================
// SortableJS drag-and-drop handler
// ============================================================
async function handleDragEnd(evt) {
  const taskId   = evt.item.dataset.taskId;
  const newCol   = evt.to;
  const oldCol   = evt.from;
  const newStatus = newCol.dataset.status;

  // Update status if column changed
  if (oldCol !== newCol) {
    evt.item.dataset.status = newStatus;
    await apiFetch(`/tasks/${taskId}/move/`, {
      status:       newStatus,
      column_order: evt.newIndex,
    });
    updateColumnCount(oldCol);
    updateColumnCount(newCol);
  }

  // Reorder tasks in the destination column
  const items = Array.from(newCol.children).map((el, idx) => ({
    id:           parseInt(el.dataset.taskId, 10),
    column_order: idx,
  }));
  await apiFetch('/tasks/reorder/', { tasks: items });
}

// ============================================================
// Initialise the board
// ============================================================
function initKanban() {
  const tasksData    = window.TASKS_DATA    || {};
  const statusColumns = window.STATUS_COLUMNS || ['OPEN','PENDING','IN_PROGRESS','REVIEW','COMPLETED'];

  statusColumns.forEach((status) => {
    const colEl = document.getElementById(`column-${status}`);
    if (!colEl) return;

    // Render cards
    const tasks = tasksData[status] || [];
    tasks.forEach((task) => colEl.appendChild(createTaskCard(task)));

    // Update count badge
    updateColumnCount(colEl);

    // Initialize SortableJS
    if (typeof Sortable !== 'undefined') {
      Sortable.create(colEl, {
        group:       'kanban',
        animation:   150,
        ghostClass:  'sortable-ghost',
        chosenClass: 'sortable-chosen',
        dragClass:   'sortable-drag',
        delay:       0,
        onEnd:       handleDragEnd,
        // Highlight drop zone
        onOver(evt) {
          evt.to.classList.add('bg-blue-50', 'border-blue-200');
        },
        onLeave(evt) {
          evt.to.classList.remove('bg-blue-50', 'border-blue-200');
        },
      });
    }
  });
}

// ============================================================
// Boot on DOMContentLoaded
// ============================================================
document.addEventListener('DOMContentLoaded', initKanban);
