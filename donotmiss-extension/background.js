// Background service worker - handles context menu and messaging

// Create context menu on install
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'donotmiss-capture',
    title: 'Add to DoNotMiss',
    contexts: ['selection']
  });
});

// Handle context menu click
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'donotmiss-capture' && info.selectionText) {
    // Detect source type based on URL
    const source = detectSource(tab.url);
    
    const taskData = {
      text: info.selectionText.trim(),
      source: source,
      url: tab.url,
      title: tab.title
    };

    // Check if content script is available by pinging it
    let contentScriptReady = false;
    try {
      const response = await chrome.tabs.sendMessage(tab.id, { action: 'ping' });
      contentScriptReady = response && response.pong;
    } catch (e) {
      contentScriptReady = false;
    }

    if (contentScriptReady) {
      // Content script available - show modal
      chrome.tabs.sendMessage(tab.id, {
        action: 'showCaptureModal',
        data: taskData
      });
    } else {
      // Content script blocked - use popup fallback
      console.log('Content script blocked, using popup fallback');
      
      // Store task data for popup to retrieve
      await chrome.storage.local.set({ captureTask: taskData });
      
      // Open popup window
      chrome.windows.create({
        url: 'popup/capture.html',
        type: 'popup',
        width: 400,
        height: 300,
        top: 100,
        left: Math.round((screen.width - 400) / 2)
      });
    }
  }
});

// Detect source type from URL
function detectSource(url) {
  if (!url) return 'web';
  
  const lowerUrl = url.toLowerCase();
  
  if (lowerUrl.includes('mail.google.com') || 
      lowerUrl.includes('outlook.') || 
      lowerUrl.includes('/mail')) {
    return 'email';
  }
  
  if (lowerUrl.includes('slack.com') || 
      lowerUrl.includes('teams.microsoft.com') || 
      lowerUrl.includes('discord.com')) {
    return 'chat';
  }
  
  if (lowerUrl.includes('atlassian.net') || 
      lowerUrl.includes('jira')) {
    return 'jira';
  }
  
  return 'web';
}

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'submitTask') {
    submitTaskToBackend(request.task)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }
});

// Mock API call to backend (Forge app)
async function submitTaskToBackend(task) {
  // In production, this would call your Forge backend
  const endpoint = 'https://your-forge-app.atlassian.net/api/tasks';
  
  // For demo/hackathon: simulate API call
  console.log('📤 Sending task to backend:', task);
  
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Mock success response
  return {
    id: 'TASK-' + Date.now(),
    status: 'created',
    jiraKey: 'DNM-' + Math.floor(Math.random() * 1000)
  };
}
