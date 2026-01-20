# DoNotMiss - Quick Start Guide

**Get your complete task capture system running in 15 minutes!**

## What You're Building

```
┌─────────────────┐
│ Chrome Extension│  ← User selects text, right-clicks "Add to DoNotMiss"
└────────┬────────┘
         │ POST /api/tasks
         ▼
┌─────────────────┐
│ Flask Backend   │  ← Stores tasks in PostgreSQL
│   (Render)      │
└────────┬────────┘
         │ GET /api/tasks
         ▼
┌─────────────────┐
│ Jira Forge App  │  ← Shows tasks, creates Jira issues
│   (Dashboard)   │
└─────────────────┘
```

## Prerequisites (5 min)

- [ ] GitHub account
- [ ] Render account (free): https://render.com/
- [ ] Jira Cloud instance
- [ ] Chrome browser
- [ ] Node.js 20+ installed
- [ ] Forge CLI: `npm install -g @forge/cli`

## Step 1: Deploy Backend (5 min)

### 1.1 Push to GitHub

```bash
git add .
git commit -m "Initial DoNotMiss setup"
git push origin main
```

### 1.2 Deploy on Render

1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Blueprint"**
3. Click **"Connect GitHub"** and authorize
4. Select your **donotmiss** repository
5. Click **"Apply"**
6. Wait 5 minutes for deployment

### 1.3 Get Your Backend URL

After deployment completes:
1. Click on **"donotmiss-backend"** service
2. Copy the URL at the top (e.g., `https://donotmiss-backend-xxxx.onrender.com`)
3. **Save this URL** - you'll need it next!

### 1.4 Test Backend

```bash
# Replace with your actual URL
curl https://your-backend-url.onrender.com/health

# Should return: {"status":"healthy","timestamp":"..."}
```

✅ **Backend is live!**

## Step 2: Configure Extension (3 min)

### 2.1 Update Backend URL

Open `donotmiss-extension/background.js` and find line 88:

```javascript
// BEFORE
const BACKEND_URL = 'https://donotmiss-backend.onrender.com';

// AFTER - Replace with YOUR actual URL
const BACKEND_URL = 'https://donotmiss-backend-xxxx.onrender.com';
```

### 2.2 Update Permissions

Open `donotmiss-extension/manifest.json` and update:

```json
{
  "host_permissions": [
    "https://donotmiss-backend-xxxx.onrender.com/*"
  ]
}
```

### 2.3 Load Extension

1. Open Chrome → `chrome://extensions/`
2. Enable **"Developer mode"** (top right toggle)
3. Click **"Load unpacked"**
4. Select the `donotmiss-extension` folder
5. Extension icon should appear in toolbar

### 2.4 Test Extension

1. Go to **Gmail** or any webpage
2. Select some text (e.g., "Review budget report")
3. Right-click → **"Add to DoNotMiss"**
4. Fill the form:
   - Title: "Review Budget"
   - Priority: High
   - Due Date: Tomorrow
5. Click **"Add to Jira"**
6. Should see success message ✅

✅ **Extension is working!**

## Step 3: Deploy Forge App (5 min)

### 3.1 Update Backend URL

Open `donotmiss-forge/src/index.js` and find line 6:

```javascript
// BEFORE
const FLASK_BACKEND_URL = 'https://donotmiss-backend.onrender.com';

// AFTER - Replace with YOUR actual URL
const FLASK_BACKEND_URL = 'https://donotmiss-backend-xxxx.onrender.com';
```

### 3.2 Update Permissions

Open `donotmiss-forge/manifest.yml` and update:

```yaml
permissions:
  external:
    fetch:
      backend:
        - 'donotmiss-backend-xxxx.onrender.com'  # Your actual domain
```

### 3.3 Build React Dashboard

```bash
cd donotmiss-forge/static/dashboard
npm install
npm run build
cd ../..
```

### 3.4 Deploy to Forge

```bash
cd donotmiss-forge

# Login (first time only)
forge login

# Register app (first time only)
forge register

# Deploy
forge deploy

# Install to Jira
forge install
```

Follow the prompts:
- Select your Jira site
- Select your project
- Confirm installation

### 3.5 Open Dashboard

1. Go to your Jira project
2. Look for **"DoNotMiss"** in the left sidebar
3. Click it to open the dashboard

✅ **Forge app is live!**

## Step 4: Test End-to-End (2 min)

### Complete Flow Test

1. **Capture Task**
   - Go to any webpage
   - Select text: "Prepare presentation for Monday"
   - Right-click → "Add to DoNotMiss"
   - Fill form and submit

2. **View in Dashboard**
   - Open Jira → Your Project → DoNotMiss
   - Click **"Refresh"** button
   - Task should appear in **"Inbox"** tab

3. **Send to Jira**
   - Click **"Send to Jira"** on the task
   - Optionally assign to team member
   - Confirm

4. **Verify Issue**
   - Task moves to **"Sent"** tab
   - Click the Jira key (e.g., PROJ-123)
   - Issue opens with all details ✅

## Troubleshooting

### Extension: "Failed to create task"

```bash
# Check backend is running
curl https://your-backend-url.onrender.com/health

# Check browser console (F12) for errors
# Verify BACKEND_URL in background.js is correct
# Verify host_permissions in manifest.json includes your URL
```

### Forge: "No tasks found"

```bash
# Check backend has tasks
curl https://your-backend-url.onrender.com/api/tasks

# Click "Refresh" button in dashboard
# Check Forge logs: forge logs
# Verify FLASK_BACKEND_URL in src/index.js is correct
```

### Backend: Slow response (30+ seconds)

This is normal for Render free tier after 15 minutes of inactivity. The first request wakes up the service. Subsequent requests are fast.

## What's Next?

### Immediate
- ✅ System is fully functional
- ✅ Can capture tasks from anywhere
- ✅ Can create Jira issues

### Phase 2 (Future)
- 🤖 AI task detection from emails
- 📧 Automatic email scanning
- 💬 Telegram integration
- 🔔 Browser notifications

### Production
- 📦 Publish extension to Chrome Web Store
- 🏪 Publish Forge app to Atlassian Marketplace
- 📊 Add analytics and monitoring
- 💰 Upgrade Render to paid plan

## Quick Reference

### Backend URL
```
https://donotmiss-backend-xxxx.onrender.com
```

### API Endpoints
```
GET  /health                          - Health check
GET  /api/tasks                       - Get all tasks
POST /api/tasks                       - Create task
POST /api/tasks/:id/mark-sent         - Mark as sent
POST /api/tasks/:id/decline           - Decline task
POST /api/tasks/:id/restore           - Restore task
DELETE /api/tasks/:id                 - Delete task
```

### Useful Commands
```bash
# Test backend
curl https://your-url.onrender.com/health

# View Forge logs
cd donotmiss-forge && forge logs

# Rebuild React app
cd donotmiss-forge/static/dashboard && npm run build

# Redeploy Forge
cd donotmiss-forge && forge deploy

# Reload extension
chrome://extensions/ → Click reload icon
```

## Support

Need help? Check:
1. [DEPLOYMENT.md](DEPLOYMENT.md) - Detailed deployment guide
2. [CHECKLIST.md](CHECKLIST.md) - Complete verification checklist
3. [TESTING.md](TESTING.md) - Testing procedures
4. Browser console (F12) - For extension errors
5. `forge logs` - For Forge app errors
6. Render dashboard - For backend logs

---

**🎉 Congratulations!**

Your DoNotMiss system is now live and ready to capture tasks from anywhere on the web!

**Total Setup Time:** ~15 minutes
