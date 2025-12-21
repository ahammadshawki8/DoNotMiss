// Capture popup - fallback for sites that block content scripts

let taskData = null;

document.addEventListener('DOMContentLoaded', async () => {
  // Get stored task data
  const result = await chrome.storage.local.get('captureTask');
  taskData = result.captureTask;

  if (!taskData) {
    window.close();
    return;
  }

  // Clear stored data
  await chrome.storage.local.remove('captureTask');

  // Populate UI
  const titleInput = document.getElementById('task-title');
  const textarea = document.getElementById('task-text');
  const badge = document.getElementById('source-badge');

  // Auto-generate title
  const autoTitle = taskData.text.length > 50 
    ? taskData.text.substring(0, 50).trim() + '...' 
    : taskData.text.trim();
  
  titleInput.value = autoTitle;
  textarea.value = taskData.text;
  
  const icons = { email: '📧', chat: '💬', jira: '🎫', web: '🌐' };
  const colors = {
    email: 'source-email',
    chat: 'source-chat',
    web: 'source-web'
  };
  
  badge.className = `source-badge ${colors[taskData.source] || 'source-web'}`;
  badge.textContent = `${icons[taskData.source] || '🌐'} ${taskData.source.toUpperCase()}`;

  // Focus title
  titleInput.focus();
  titleInput.select();

  // Bind events
  document.getElementById('btn-cancel').addEventListener('click', () => window.close());
  document.getElementById('btn-submit').addEventListener('click', handleSubmit);

  // Keyboard shortcuts
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') window.close();
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') handleSubmit();
  });
});

async function handleSubmit() {
  const titleInput = document.getElementById('task-title');
  const textarea = document.getElementById('task-text');
  const deadlineInput = document.getElementById('task-deadline');
  const prioritySelect = document.getElementById('task-priority');
  const submitBtn = document.getElementById('btn-submit');
  
  const title = titleInput.value.trim();

  if (!title) {
    titleInput.classList.add('error');
    setTimeout(() => titleInput.classList.remove('error'), 500);
    titleInput.focus();
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Sending...';

  const task = {
    title: title,
    description: textarea.value.trim(),
    deadline: deadlineInput.value || null,
    priority: prioritySelect.value,
    source: taskData.source,
    url: taskData.url,
    timestamp: new Date().toISOString(),
    userApproved: true
  };

  try {
    const response = await chrome.runtime.sendMessage({
      action: 'submitTask',
      task: task
    });

    if (response.success) {
      document.getElementById('form-view').style.display = 'none';
      document.getElementById('success-view').style.display = 'block';
      setTimeout(() => window.close(), 1200);
    } else {
      throw new Error('Failed');
    }
  } catch (error) {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Retry';
    submitBtn.style.background = '#DE350B';
  }
}
