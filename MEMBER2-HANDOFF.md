# DoNotMiss — Member 2 Handoff Document

> **From:** Member 1 (Frontend & Core Backend)  
> **To:** Member 2 (AI & Backend)  
> **Date:** December 22, 2024

---

## 📋 Summary

I've completed the **Chrome Extension** and **Forge App** with full Jira integration. The product is functional end-to-end for manual task capture. Your job is to add the **AI layer** that automatically detects tasks.

---

## ✅ What Member 1 Completed

### Chrome Extension (`donotmiss-extension/`)

| Component | File | Description |
|-----------|------|-------------|
| Context Menu | `background.js` | Right-click "Add to DoNotMiss" on selected text |
| Capture Modal | `content.js`, `content.css` | Popup form with title, description, priority, due date |
| Fallback Popup | `popup/capture.html`, `capture.js` | For sites that block content scripts (Facebook, Messenger) |
| AI Tasks Popup | `popup/popup.html`, `popup.js` | Shows mock "AI-detected" tasks (YOUR INTEGRATION POINT) |
| Source Detection | `background.js` | Auto-detects email/chat/web/jira from URL |

### Forge App (`donotmiss-forge/`)

| Component | File | Description |
|-----------|------|-------------|
| Dashboard UI | `static/dashboard/src/App.js` | React app showing Inbox/Sent/Declined tasks |
| Backend Resolvers | `src/index.js` | 12 functions for task management |
| Jira Integration | `src/index.js` | Creates real issues via REST API |
| Storage | Forge Storage API | Tasks stored with status tracking |

### Jira Issue Creation Details

When "Send to Jira" is clicked, the system:
1. Creates a Jira issue with:
   - **Summary:** Task title
   - **Description:** Task description + source link + "Created via DoNotMiss"
   - **Labels:** `donotmiss`, `source-email` (or chat/web)
   - **Priority:** Mapped from highest/high/medium/low
   - **Due Date:** If provided
   - **Assignee:** If selected
2. Adds a comment: *"✨ This task was captured using DoNotMiss from email. 🔗 Source: [url]"*
3. Updates task status to `sent` with `jiraKey`

---

## 🎯 What Member 2 Needs To Do

### Primary Task: AI Task Detection

Build the AI system that:
1. **Analyzes page content** (emails, chat messages, documents)
2. **Detects potential tasks** (action items, requests, deadlines)
3. **Sends detected tasks** to the extension popup for user approval

### Integration Points

#### 1. Extension Popup (`donotmiss-extension/popup/popup.js`)

Currently uses **mock data**. Replace with real AI-detected tasks.

```javascript
// CURRENT (lines 3-22) - MOCK DATA
const MOCK_TASKS = [
  {
    id: 1,
    text: "Review the Q4 budget proposal and send feedback by Friday",
    source: "email",
    url: "https://mail.google.com/mail/u/0/#inbox/abc123",
    detectedAt: new Date(Date.now() - 1000 * 60 * 5).toISOString()
  },
  // ... more mock tasks
];

// YOUR TASK: Replace with real AI detection
// Option A: Call your AI backend API
// Option B: Run local NLP in the extension
// Option C: Use chrome.storage to receive tasks from content script analysis
```

#### 2. Content Script Analysis (`donotmiss-extension/content.js`)

Add AI analysis when page loads or content changes:

```javascript
// ADD THIS: Analyze page content for tasks
async function analyzePageForTasks() {
  const pageText = document.body.innerText;
  const url = window.location.href;
  const source = detectSource(url); // Already exists in background.js
  
  // YOUR AI LOGIC HERE
  // Send to your backend or run local detection
  const detectedTasks = await yourAIFunction(pageText);
  
  // Store for popup to display
  chrome.storage.local.set({ 
    pendingTasks: detectedTasks.map(task => ({
      id: Date.now() + Math.random(),
      text: task.text,
      source: source,
      url: url,
      detectedAt: new Date().toISOString(),
      confidence: task.confidence // Optional: show AI confidence
    }))
  });
}

// Call on page load
analyzePageForTasks();
```

#### 3. Background Script (`donotmiss-extension/background.js`)

The `submitTaskToBackend()` function currently mocks the API call:

```javascript
// CURRENT (lines 85-100) - MOCK API
async function submitTaskToBackend(task) {
  const endpoint = 'https://your-forge-app.atlassian.net/api/tasks';
  
  console.log('📤 Sending task to backend:', task);
  await new Promise(resolve => setTimeout(resolve, 800));
  
  return {
    id: 'TASK-' + Date.now(),
    status: 'created',
    jiraKey: 'DNM-' + Math.floor(Math.random() * 1000)
  };
}

// YOUR TASK: Connect to real backend
// Option A: Forge Web Trigger (recommended)
// Option B: External API that calls Forge
```

---

## 📦 Data Contract

### Task Object (Extension → Backend)

```json
{
  "title": "Review Q4 budget proposal",
  "description": "Review the Q4 budget proposal and send feedback by Friday",
  "deadline": "2024-12-25",
  "priority": "high",
  "source": "email",
  "url": "https://mail.google.com/mail/u/0/#inbox/abc123",
  "timestamp": "2024-12-22T10:30:00.000Z",
  "userApproved": true
}
```

### Field Definitions

| Field | Type | Required | Values |
|-------|------|----------|--------|
| `title` | string | Yes | Max 255 chars |
| `description` | string | Yes | Full task text |
| `deadline` | string | No | ISO date (YYYY-MM-DD) |
| `priority` | string | Yes | `highest`, `high`, `medium`, `low` |
| `source` | string | Yes | `email`, `chat`, `web`, `jira` |
| `url` | string | Yes | Source page URL |
| `timestamp` | string | Yes | ISO 8601 datetime |
| `userApproved` | boolean | Yes | Always `true` when sent |

### AI-Detected Task Object (For Popup)

```json
{
  "id": 1703234567890,
  "text": "Review the Q4 budget proposal and send feedback by Friday",
  "source": "email",
  "url": "https://mail.google.com/...",
  "detectedAt": "2024-12-22T10:30:00.000Z",
  "confidence": 0.92
}
```

---

## 🔌 Integration Options

### Option A: Forge Web Trigger (Recommended)

Add a web trigger to receive tasks from the extension:

**1. Update `donotmiss-forge/manifest.yml`:**
```yaml
modules:
  webtrigger:
    - key: add-task-trigger
      function: addTaskHandler
  function:
    - key: addTaskHandler
      handler: index.addTaskHandler
```

**2. Add handler in `donotmiss-forge/src/index.js`:**
```javascript
export async function addTaskHandler(request) {
  const task = JSON.parse(request.body);
  
  // Use existing addTask logic
  const tasks = await storage.get('tasks') || [];
  const newTask = {
    id: `task-${Date.now()}`,
    title: task.title,
    description: task.description,
    source: task.source,
    url: task.url,
    priority: task.priority || 'medium',
    deadline: task.deadline || null,
    status: 'pending',
    createdAt: task.timestamp || new Date().toISOString(),
    createdVia: 'donotmiss-extension'
  };
  
  tasks.unshift(newTask);
  await storage.set('tasks', tasks);
  
  return {
    statusCode: 200,
    body: JSON.stringify({ success: true, task: newTask })
  };
}
```

**3. Get the trigger URL:**
```bash
forge webtrigger
# Returns: https://xxx.atlassian.net/x/xxx/xxx
```

**4. Update extension to call it:**
```javascript
async function submitTaskToBackend(task) {
  const response = await fetch('YOUR_WEBTRIGGER_URL', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(task)
  });
  return response.json();
}
```

### Option B: External AI Backend

If you need a separate AI server:

1. Build your AI API (Python/Node/etc.)
2. API receives page content, returns detected tasks
3. Extension calls your API, then calls Forge web trigger
4. Or your API directly calls Forge web trigger

---

## 🧪 Testing the Current System

### Test Manual Capture (Already Working)
1. Load extension in Chrome (`chrome://extensions/` → Load unpacked)
2. Go to Gmail or any webpage
3. Select text → Right-click → "Add to DoNotMiss"
4. Fill form → Click "Add to Jira"
5. Open Jira → Project → DoNotMiss dashboard
6. Click "Send to Jira" → Creates real issue

### Test AI Popup (Mock Data)
1. Click the extension icon in Chrome toolbar
2. See 3 mock "AI-detected" tasks
3. Click "Add to Jira" or "Dismiss"
4. This is where YOUR AI integration goes

---

## 📁 Files You'll Modify

| File | What to Change |
|------|----------------|
| `donotmiss-extension/popup/popup.js` | Replace `MOCK_TASKS` with real AI detection |
| `donotmiss-extension/content.js` | Add page analysis on load |
| `donotmiss-extension/background.js` | Update `submitTaskToBackend()` for real API |
| `donotmiss-forge/manifest.yml` | Add web trigger module (if using Option A) |
| `donotmiss-forge/src/index.js` | Add web trigger handler (if using Option A) |

---

## 🚀 Deployment Commands

### Chrome Extension
```bash
# No build needed - just reload in chrome://extensions/
```

### Forge App
```bash
cd donotmiss-forge

# If you changed the React dashboard
cd static/dashboard && npm run build && cd ../..

# Deploy to Atlassian
forge deploy

# If you added new permissions
forge install --upgrade
```

---

## ❓ Questions?

### What's the Jira project key?
`DD` (DoNotMiss Demo)

### What's the Jira site?
`ahammadshawki8.atlassian.net`

### What's the Forge app ID?
`ari:cloud:ecosystem::app/c64bd487-9dc2-47bb-8777-dd2fbd96410e`

### Where are tasks stored?
Forge Storage API (`storage.get('tasks')` / `storage.set('tasks', [...])`)

### How do I clear test data?
In the Forge dashboard, click the 🗑️ button in the header.

---
