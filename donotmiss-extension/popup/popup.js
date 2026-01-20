// DoNotMiss Popup - Shows AI-detected tasks

const BACKEND_URL = 'https://donotmiss.onrender.com';

// Load detected tasks on popup open
document.addEventListener('DOMContentLoaded', () => {
  loadDetectedTasks();
  
  // Refresh button
  document.getElementById('refreshBtn')?.addEventListener('click', () => {
    loadDetectedTasks();
  });
});

async function loadDetectedTasks() {
  const loading = document.getElementById('loading');
  const tasksContainer = document.getElementById('tasksContainer');
  const emptyState = document.getElementById('emptyState');
  const tasksList = document.getElementById('tasksList');
  
  // Show loading
  loading.style.display = 'block';
  tasksContainer.style.display = 'none';
  emptyState.style.display = 'none';
  
  try {
    const response = await fetch(`${BACKEND_URL}/api/tasks/detected`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch tasks');
    }
    
    const tasks = await response.json();
    
    // Hide loading
    loading.style.display = 'none';
    
    if (tasks.length === 0) {
      // Show empty state
      emptyState.style.display = 'block';
      
      // Clear badge
      chrome.action.setBadgeText({ text: '' });
    } else {
      // Show tasks
      tasksContainer.style.display = 'block';
      renderTasks(tasks, tasksList);
      
      // Update badge
      chrome.action.setBadgeText({ text: tasks.length.toString() });
      chrome.action.setBadgeBackgroundColor({ color: '#FF5630' });
    }
  } catch (error) {
    console.error('Error loading tasks:', error);
    loading.style.display = 'none';
    emptyState.style.display = 'block';
  }
}

function renderTasks(tasks, container) {
  container.innerHTML = '';
  
  tasks.forEach(task => {
    const taskCard = document.createElement('div');
    taskCard.className = 'task-card';
    taskCard.innerHTML = `
      <div class="task-header">
        <span class="task-source">📧 ${task.source.toUpperCase()}</span>
        <span class="task-priority priority-${task.priority}">${task.priority}</span>
      </div>
      <h3 class="task-title">${escapeHtml(task.title)}</h3>
      <p class="task-description">${escapeHtml(task.description || '').substring(0, 100)}${task.description?.length > 100 ? '...' : ''}</p>
      ${task.metadata?.emailSubject ? `<div class="task-meta">From: ${escapeHtml(task.metadata.emailSubject)}</div>` : ''}
      <div class="task-actions">
        <button class="btn btn-decline" data-id="${task.id}">Decline</button>
        <button class="btn btn-confirm" data-id="${task.id}">Confirm & Add to Jira</button>
      </div>
    `;
    
    container.appendChild(taskCard);
  });
  
  // Add event listeners
  container.querySelectorAll('.btn-confirm').forEach(btn => {
    btn.addEventListener('click', () => confirmTask(btn.dataset.id));
  });
  
  container.querySelectorAll('.btn-decline').forEach(btn => {
    btn.addEventListener('click', () => declineTask(btn.dataset.id));
  });
}

async function confirmTask(taskId) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/tasks/${taskId}/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.ok) {
      // Reload tasks
      loadDetectedTasks();
      
      // Show success notification
      showNotification('Task confirmed! Open Jira to send it.');
    } else {
      throw new Error('Failed to confirm task');
    }
  } catch (error) {
    console.error('Error confirming task:', error);
    alert('Failed to confirm task. Please try again.');
  }
}

async function declineTask(taskId) {
  try {
    const response = await fetch(`${BACKEND_URL}/api/tasks/${taskId}/decline`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.ok) {
      // Reload tasks
      loadDetectedTasks();
    } else {
      throw new Error('Failed to decline task');
    }
  } catch (error) {
    console.error('Error declining task:', error);
    alert('Failed to decline task. Please try again.');
  }
}

function showNotification(message) {
  chrome.notifications.create({
    type: 'basic',
    iconUrl: '../icons/icon48.png',
    title: 'DoNotMiss',
    message: message
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
