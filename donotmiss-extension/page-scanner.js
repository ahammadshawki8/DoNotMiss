// Page Scanner - Detects tasks from email/chat pages
// Runs on Gmail, Outlook, Slack, etc.

console.log('DoNotMiss page scanner loaded');

// Configuration
const SCAN_INTERVAL = 5000; // Scan every 5 seconds
const MIN_TEXT_LENGTH = 50; // Minimum text length to analyze
let lastScannedContent = '';
let scanTimeout = null;

// Detect which platform we're on
function detectPlatform() {
  const hostname = window.location.hostname;
  
  if (hostname.includes('mail.google.com')) return 'gmail';
  if (hostname.includes('outlook.')) return 'outlook';
  if (hostname.includes('slack.com')) return 'slack';
  if (hostname.includes('teams.microsoft.com')) return 'teams';
  if (hostname.includes('web.telegram.org')) return 'telegram';
  
  return null;
}

// Extract email content from Gmail
function extractGmailContent() {
  try {
    // Get the email body
    const emailBody = document.querySelector('.a3s.aiL') || 
                     document.querySelector('[data-message-id]');
    
    if (!emailBody) return null;
    
    // Get subject
    const subject = document.querySelector('h2.hP')?.textContent || '';
    
    // Get sender
    const sender = document.querySelector('.gD')?.getAttribute('email') || '';
    
    // Get body text
    const bodyText = emailBody.textContent || '';
    
    // Get email URL
    const url = window.location.href;
    
    return {
      platform: 'gmail',
      subject: subject.trim(),
      sender: sender,
      body: bodyText.trim(),
      url: url,
      fullText: `Subject: ${subject}\n\n${bodyText}`
    };
  } catch (e) {
    console.error('Error extracting Gmail content:', e);
    return null;
  }
}

// Extract email content from Outlook
function extractOutlookContent() {
  try {
    // Get subject
    const subject = document.querySelector('[aria-label*="Subject"]')?.textContent || 
                   document.querySelector('.customScrollBar')?.textContent || '';
    
    // Get body
    const emailBody = document.querySelector('[role="document"]') ||
                     document.querySelector('.ReadingPaneContents');
    
    if (!emailBody) return null;
    
    const bodyText = emailBody.textContent || '';
    const url = window.location.href;
    
    return {
      platform: 'outlook',
      subject: subject.trim(),
      sender: '',
      body: bodyText.trim(),
      url: url,
      fullText: `Subject: ${subject}\n\n${bodyText}`
    };
  } catch (e) {
    console.error('Error extracting Outlook content:', e);
    return null;
  }
}

// Extract message content from Slack
function extractSlackContent() {
  try {
    // Get the active message thread
    const messages = document.querySelectorAll('[data-qa="message_container"]');
    
    if (messages.length === 0) return null;
    
    // Get last few messages
    const recentMessages = Array.from(messages).slice(-5);
    const messageTexts = recentMessages.map(msg => {
      const text = msg.querySelector('.p-rich_text_section')?.textContent || '';
      return text.trim();
    }).filter(t => t.length > 0);
    
    const fullText = messageTexts.join('\n\n');
    const url = window.location.href;
    
    return {
      platform: 'slack',
      subject: 'Slack Conversation',
      sender: '',
      body: fullText,
      url: url,
      fullText: fullText
    };
  } catch (e) {
    console.error('Error extracting Slack content:', e);
    return null;
  }
}

// Extract content based on platform
function extractPageContent() {
  const platform = detectPlatform();
  
  if (!platform) return null;
  
  switch (platform) {
    case 'gmail':
      return extractGmailContent();
    case 'outlook':
      return extractOutlookContent();
    case 'slack':
      return extractSlackContent();
    default:
      return null;
  }
}

// Send content to background for AI analysis
async function analyzeContent(content) {
  try {
    // Don't analyze if content hasn't changed
    if (content.fullText === lastScannedContent) {
      return;
    }
    
    // Don't analyze if too short
    if (content.fullText.length < MIN_TEXT_LENGTH) {
      return;
    }
    
    lastScannedContent = content.fullText;
    
    console.log('📧 Analyzing content for tasks...');
    
    // Send to background script for AI analysis
    const response = await chrome.runtime.sendMessage({
      action: 'analyzeForTasks',
      content: content
    });
    
    if (response.success && response.tasks && response.tasks.length > 0) {
      console.log(`✅ Found ${response.tasks.length} potential tasks!`);
      
      // Show notification
      showTaskDetectedNotification(response.tasks.length);
      
      // Update badge
      chrome.runtime.sendMessage({
        action: 'updateBadge',
        count: response.tasks.length
      });
    }
  } catch (error) {
    console.error('Error analyzing content:', error);
  }
}

// Show notification when tasks are detected
function showTaskDetectedNotification(count) {
  // Create a small notification on the page
  const notification = document.createElement('div');
  notification.id = 'donotmiss-notification';
  notification.innerHTML = `
    <div style="
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 16px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      z-index: 999999;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      animation: slideIn 0.3s ease;
    ">
      🤖 DoNotMiss detected ${count} task${count > 1 ? 's' : ''}!
      <div style="font-size: 12px; font-weight: 400; margin-top: 4px; opacity: 0.9;">
        Click extension icon to review
      </div>
    </div>
    <style>
      @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
      }
    </style>
  `;
  
  // Remove existing notification
  const existing = document.getElementById('donotmiss-notification');
  if (existing) existing.remove();
  
  document.body.appendChild(notification);
  
  // Auto-remove after 5 seconds
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease';
    setTimeout(() => notification.remove(), 300);
  }, 5000);
  
  // Click to open popup
  notification.addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'openPopup' });
    notification.remove();
  });
}

// Start scanning when page loads
function startScanning() {
  const platform = detectPlatform();
  
  if (!platform) {
    console.log('DoNotMiss: Not on a supported platform');
    return;
  }
  
  console.log(`DoNotMiss: Scanning ${platform} for tasks...`);
  
  // Initial scan after 2 seconds (let page load)
  setTimeout(() => {
    const content = extractPageContent();
    if (content) {
      analyzeContent(content);
    }
  }, 2000);
  
  // Periodic scanning
  scanTimeout = setInterval(() => {
    const content = extractPageContent();
    if (content) {
      analyzeContent(content);
    }
  }, SCAN_INTERVAL);
}

// Stop scanning when leaving page
function stopScanning() {
  if (scanTimeout) {
    clearInterval(scanTimeout);
    scanTimeout = null;
  }
}

// Listen for page visibility changes
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    stopScanning();
  } else {
    startScanning();
  }
});

// Start scanning
startScanning();

// Cleanup on unload
window.addEventListener('beforeunload', stopScanning);
