// Content script - handles the capture modal UI

let modal = null;

// Listen for messages from background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'ping') {
    sendResponse({ pong: true });
    return;
  }
  if (request.action === 'showCaptureModal') {
    showCaptureModal(request.data);
  }
});

function showCaptureModal(data) {
  // Remove existing modal if any
  if (modal) {
    modal.remove();
  }

  // Auto-generate title from text (first 50 chars)
  const autoTitle = data.text.length > 50 
    ? data.text.substring(0, 50).trim() + '...' 
    : data.text.trim();

  // Create modal container
  modal = document.createElement('div');
  modal.id = 'donotmiss-modal';
  modal.innerHTML = `
    <div class="dnm-overlay"></div>
    <div class="dnm-modal">
      <div class="dnm-header">
        <div class="dnm-logo">
          <svg width="24" height="24" viewBox="0 0 48 48" fill="none">
            <defs>
              <linearGradient id="dnm-grad1" x1="0%" y1="100%" x2="100%" y2="0%">
                <stop offset="0%" style="stop-color:#6B8DD6"/>
                <stop offset="50%" style="stop-color:#8E6DD6"/>
                <stop offset="100%" style="stop-color:#F97B5C"/>
              </linearGradient>
              <linearGradient id="dnm-grad2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#F9A85C"/>
                <stop offset="100%" style="stop-color:#F97B5C"/>
              </linearGradient>
            </defs>
            <path d="M8 26C8 26 14 19 16 21C18 23 20 28 20 28C20 28 30 11 38 8" stroke="url(#dnm-grad1)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <circle cx="38" cy="8" r="5" fill="url(#dnm-grad2)"/>
          </svg>
          <span>DoNotMiss</span>
        </div>
        <button class="dnm-close" aria-label="Close">&times;</button>
      </div>
      
      <div class="dnm-body">
        <div class="dnm-source-badge dnm-source-${data.source}">
          ${getSourceIcon(data.source)} ${data.source.toUpperCase()}
        </div>
        
        <div class="dnm-field">
          <label class="dnm-label">Title</label>
          <input type="text" class="dnm-input dnm-title" value="${escapeHtml(autoTitle)}" placeholder="Task title...">
        </div>
        
        <div class="dnm-field">
          <label class="dnm-label">Description</label>
          <textarea class="dnm-textarea" placeholder="Task description...">${escapeHtml(data.text)}</textarea>
        </div>
        
        <div class="dnm-row">
          <div class="dnm-field dnm-field-half">
            <label class="dnm-label">Due Date <span class="dnm-optional">(optional)</span></label>
            <input type="date" class="dnm-input dnm-deadline">
          </div>
          
          <div class="dnm-field dnm-field-half">
            <label class="dnm-label">Priority</label>
            <select class="dnm-select dnm-priority">
              <option value="low">Low</option>
              <option value="medium" selected>Medium</option>
              <option value="high">High</option>
              <option value="highest">Highest</option>
            </select>
          </div>
        </div>
        
        <div class="dnm-meta">
          <span class="dnm-url" title="${escapeHtml(data.url)}">
            ${truncateUrl(data.url)}
          </span>
        </div>
      </div>
      
      <div class="dnm-footer">
        <button class="dnm-btn dnm-btn-secondary dnm-cancel">Cancel</button>
        <button class="dnm-btn dnm-btn-primary dnm-submit">
          <span class="dnm-btn-text">Add to Jira</span>
          <span class="dnm-btn-loading">
            <svg class="dnm-spinner" width="16" height="16" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" fill="none" opacity="0.3"/>
              <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="3" fill="none" stroke-linecap="round"/>
            </svg>
          </span>
        </button>
      </div>
      
      <div class="dnm-success">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <defs>
            <linearGradient id="dnm-success-grad1" x1="0%" y1="100%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#6B8DD6"/>
              <stop offset="50%" style="stop-color:#8E6DD6"/>
              <stop offset="100%" style="stop-color:#F97B5C"/>
            </linearGradient>
            <linearGradient id="dnm-success-grad2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#F9A85C"/>
              <stop offset="100%" style="stop-color:#F97B5C"/>
            </linearGradient>
          </defs>
          <path d="M8 26C8 26 14 19 16 21C18 23 20 28 20 28C20 28 30 11 38 8" stroke="url(#dnm-success-grad1)" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          <circle cx="38" cy="8" r="5" fill="url(#dnm-success-grad2)"/>
        </svg>
        <span>Task sent to Jira!</span>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Store data for submission
  modal.taskData = data;

  // Bind events
  bindModalEvents();

  // Focus textarea
  setTimeout(() => {
    modal.querySelector('.dnm-textarea').focus();
  }, 100);
}

function bindModalEvents() {
  const overlay = modal.querySelector('.dnm-overlay');
  const closeBtn = modal.querySelector('.dnm-close');
  const cancelBtn = modal.querySelector('.dnm-cancel');
  const submitBtn = modal.querySelector('.dnm-submit');
  const textarea = modal.querySelector('.dnm-textarea');

  // Close handlers
  overlay.addEventListener('click', closeModal);
  closeBtn.addEventListener('click', closeModal);
  cancelBtn.addEventListener('click', closeModal);

  // Submit handler
  submitBtn.addEventListener('click', handleSubmit);

  // Keyboard shortcuts
  document.addEventListener('keydown', handleKeydown);

  // Auto-resize textarea
  textarea.addEventListener('input', () => {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
  });
}

function handleKeydown(e) {
  if (!modal) return;
  
  // Escape to close
  if (e.key === 'Escape') {
    closeModal();
  }
  
  // Ctrl/Cmd + Enter to submit
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    handleSubmit();
  }
}

async function handleSubmit() {
  const titleInput = modal.querySelector('.dnm-title');
  const textarea = modal.querySelector('.dnm-textarea');
  const deadlineInput = modal.querySelector('.dnm-deadline');
  const prioritySelect = modal.querySelector('.dnm-priority');
  const submitBtn = modal.querySelector('.dnm-submit');
  const btnText = submitBtn.querySelector('.dnm-btn-text');
  const btnLoading = submitBtn.querySelector('.dnm-btn-loading');
  const successEl = modal.querySelector('.dnm-success');

  const title = titleInput.value.trim();
  const text = textarea.value.trim();
  
  // Validate title
  if (!title) {
    titleInput.classList.add('dnm-error');
    setTimeout(() => titleInput.classList.remove('dnm-error'), 500);
    titleInput.focus();
    return;
  }

  // Show loading state
  submitBtn.disabled = true;
  btnText.style.display = 'none';
  btnLoading.classList.add('dnm-show');

  // Prepare task payload
  const task = {
    title: title,
    description: text,
    deadline: deadlineInput.value || null,
    priority: prioritySelect.value,
    source: modal.taskData.source,
    url: modal.taskData.url,
    timestamp: new Date().toISOString(),
    userApproved: true
  };

  try {
    // Send to background script
    const response = await chrome.runtime.sendMessage({
      action: 'submitTask',
      task: task
    });

    if (response.success) {
      // Show success state
      modal.querySelector('.dnm-body').style.display = 'none';
      modal.querySelector('.dnm-footer').style.display = 'none';
      successEl.classList.add('dnm-show');

      // Auto-close after delay
      setTimeout(closeModal, 1500);
    } else {
      throw new Error(response.error || 'Failed to create task');
    }
  } catch (error) {
    console.error('DoNotMiss error:', error);
    
    // Reset button
    submitBtn.disabled = false;
    btnText.style.display = 'inline';
    btnLoading.classList.remove('dnm-show');
    btnText.textContent = 'Retry';
    
    // Show error briefly
    submitBtn.classList.add('dnm-btn-error');
    setTimeout(() => submitBtn.classList.remove('dnm-btn-error'), 2000);
  }
}

function closeModal() {
  if (modal) {
    modal.classList.add('dnm-closing');
    setTimeout(() => {
      modal.remove();
      modal = null;
    }, 200);
  }
  document.removeEventListener('keydown', handleKeydown);
}

// Helper functions
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function truncateUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.hostname + (parsed.pathname.length > 20 ? parsed.pathname.slice(0, 20) + '...' : parsed.pathname);
  } catch {
    return url.slice(0, 40) + '...';
  }
}

function getSourceIcon(source) {
  const icons = {
    email: '📧',
    chat: '💬',
    jira: '🎫',
    web: '🌐'
  };
  return icons[source] || icons.web;
}
