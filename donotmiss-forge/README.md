# DoNotMiss Forge App

Jira integration for DoNotMiss task capture system.

## Quick Setup

### Prerequisites
- Node.js 18+
- Forge CLI: `npm install -g @forge/cli`
- Atlassian account with Jira access

### Installation

1. **Login to Forge:**
   ```bash
   forge login
   ```

2. **Install dependencies:**
   ```bash
   cd donotmiss-forge
   npm install
   
   cd static/dashboard
   npm install
   npm run build
   
   cd ../focus
   npm install
   npm run build
   ```

3. **Register the app:**
   ```bash
   cd ../..
   forge register
   ```

4. **Deploy:**
   ```bash
   forge deploy
   ```

5. **Install on your Jira site:**
   ```bash
   forge install
   ```

## Features

### 1. Dashboard (Project Page)
- View all captured tasks
- Filter by status (Pending / Sent to Jira)
- Send tasks to Jira with one click
- Discard unwanted tasks

### 2. Focus Mode (Project Page)
- Shows only pending DoNotMiss tasks
- Sorted by priority
- One-click completion
- Clean, distraction-free UI

## Data Structure

Tasks stored in Forge Storage:

```json
{
  "id": "task-123",
  "title": "Review budget proposal",
  "description": "Full task description...",
  "source": "email",
  "url": "https://mail.google.com/...",
  "priority": "high",
  "status": "pending",
  "createdAt": "ISO-8601",
  "createdVia": "donotmiss"
}
```

## API Endpoints (Resolver Functions)

| Function | Description |
|----------|-------------|
| `getTasks` | Get all tasks |
| `addTask` | Add a new task |
| `sendToJira` | Send task to Jira (creates issue) |
| `deleteTask` | Delete a task |
| `initMockData` | Initialize demo data |

## Demo Mode

The app auto-initializes with mock data for demo purposes.
To reset: clear Forge storage and reload.

## Connecting to Chrome Extension

The Chrome extension sends tasks to this Forge app.
Update the extension's `background.js` endpoint to your Forge app URL.
