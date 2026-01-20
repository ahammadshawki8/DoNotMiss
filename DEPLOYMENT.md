# DoNotMiss - Complete Deployment Guide

This guide will help you deploy the complete DoNotMiss system: Backend, Extension, and Forge App.

## Architecture Overview

```
Chrome Extension → Flask Backend (Render) ← Jira Forge App
                         ↓
                   PostgreSQL (Render)
```

## Step 1: Deploy Backend to Render

### Option A: Using render.yaml (Recommended)

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/)
3. Click "New +" → "Blueprint"
4. Connect your GitHub repository
5. Select the repository
6. Render will automatically detect `render.yaml` and create:
   - PostgreSQL database (`donotmiss-db`)
   - Web service (`donotmiss-backend`)
7. Click "Apply"
8. Wait for deployment to complete (~5 minutes)

### Option B: Manual Setup

#### 1.1 Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "PostgreSQL"
3. Configure:
   - Name: `donotmiss-db`
   - Database: `donotmiss`
   - User: `donotmiss`
   - Region: Choose closest to you
   - Plan: Free
4. Click "Create Database"
5. **Copy the "Internal Database URL"** (starts with `postgresql://`)

#### 1.2 Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - Name: `donotmiss-backend`
   - Region: **Same as database**
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: Free

4. Add Environment Variables:
   - `DATABASE_URL`: Paste the Internal Database URL from step 1.1
   - `FLASK_ENV`: `production`
   - `PYTHON_VERSION`: `3.11.7`

5. Click "Create Web Service"

### 1.3 Get Your Backend URL

After deployment completes, you'll get a URL like:
```
https://donotmiss-backend-xxxx.onrender.com
```

**Save this URL - you'll need it for the next steps!**

### 1.4 Test the Backend

```bash
# Health check
curl https://your-backend-url.onrender.com/health

# Should return: {"status":"healthy","timestamp":"..."}
```

## Step 2: Update Chrome Extension

### 2.1 Update Backend URL

Edit `donotmiss-extension/background.js`:

```javascript
// Line 88 - Update with your Render URL
const BACKEND_URL = 'https://your-backend-url.onrender.com/api';
```

### 2.2 Update Manifest Permissions

Edit `donotmiss-extension/manifest.json`:

```json
{
  "host_permissions": [
    "https://your-backend-url.onrender.com/*"
  ]
}
```

### 2.3 Install Extension

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right)
3. Click "Load unpacked"
4. Select the `donotmiss-extension` folder
5. Extension should appear in your toolbar

### 2.4 Test Extension

1. Go to any webpage (e.g., Gmail, Slack, or any site)
2. Select some text
3. Right-click → "Add to DoNotMiss"
4. Fill in the form and click "Add to Jira"
5. Check browser console for any errors

## Step 3: Deploy Forge App to Jira

### 3.1 Update Backend URL

Edit `donotmiss-forge/src/index.js`:

```javascript
// Line 6 - Update with your Render URL
const FLASK_BACKEND_URL = 'https://your-backend-url.onrender.com';
```

### 3.2 Update Manifest Permissions

Edit `donotmiss-forge/manifest.yml`:

```yaml
permissions:
  external:
    fetch:
      backend:
        - 'your-backend-url.onrender.com'
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

# Install Forge CLI if not already installed
npm install -g @forge/cli

# Login to Forge
forge login

# Register the app (first time only)
forge register

# Deploy
forge deploy

# Install to your Jira site
forge install
```

Follow the prompts to select your Jira site and project.

### 3.5 Verify Installation

1. Go to your Jira project
2. Look for "DoNotMiss" in the left sidebar
3. Click it to open the dashboard

## Step 4: Test End-to-End Flow

### 4.1 Capture a Task

1. Go to any webpage (e.g., Gmail)
2. Select text: "Review the Q1 budget report by Friday"
3. Right-click → "Add to DoNotMiss"
4. Fill in:
   - Title: "Review Q1 Budget"
   - Priority: High
   - Due Date: This Friday
5. Click "Add to Jira"
6. Should see success message

### 4.2 View in Forge Dashboard

1. Open Jira → Your Project → DoNotMiss
2. Should see the task in "Inbox" tab
3. Task should show:
   - Title: "Review Q1 Budget"
   - Source: 🌐 WEB
   - Priority: High
   - Due date

### 4.3 Send to Jira

1. Click "Send to Jira" on the task
2. Optionally assign to a team member
3. Click to confirm
4. Task should move to "Sent" tab
5. Click the Jira key (e.g., PROJ-123) to open the issue

### 4.4 Verify Jira Issue

The created issue should have:
- ✅ Title and description
- ✅ Priority set correctly
- ✅ Due date (if provided)
- ✅ Labels: `donotmiss`, `source-web`
- ✅ Source URL in description
- ✅ Assignee (if selected)

## Troubleshooting

### Backend Issues

**Problem:** Extension can't connect to backend
- Check backend URL is correct in `background.js`
- Verify backend is running: `curl https://your-url.onrender.com/health`
- Check browser console for CORS errors
- Ensure `host_permissions` in manifest.json includes your backend URL

**Problem:** Database connection errors
- Verify DATABASE_URL is set in Render environment variables
- Use "Internal Database URL" not "External"
- Ensure database and web service are in the same region

**Problem:** Backend is slow (30+ seconds)
- This is normal for Render free tier after 15 minutes of inactivity
- First request wakes up the service
- Consider upgrading to paid plan for production

### Extension Issues

**Problem:** Context menu doesn't appear
- Reload the extension: `chrome://extensions/` → Click reload icon
- Check if extension is enabled
- Try on a different website (some sites block extensions)

**Problem:** Modal doesn't show
- Check browser console for errors
- Some sites (Facebook, Messenger) block content scripts
- Extension should automatically open popup window as fallback

**Problem:** "Failed to create task" error
- Check backend URL is correct
- Verify backend is running
- Check network tab in browser DevTools
- Look for CORS errors

### Forge App Issues

**Problem:** Dashboard doesn't load
- Check if React app was built: `cd donotmiss-forge/static/dashboard && npm run build`
- Verify deployment: `forge deploy`
- Check Forge logs: `forge logs`

**Problem:** Tasks don't appear in dashboard
- Verify backend URL in `index.js`
- Check Forge manifest permissions include your backend domain
- Test backend directly: `curl https://your-url.onrender.com/api/tasks`
- Check browser console in Jira for errors

**Problem:** Can't create Jira issues
- Verify Forge app has correct permissions in manifest.yml
- Check if you have permission to create issues in the project
- Look at Forge logs: `forge logs`

**Problem:** "Failed to fetch tasks from backend"
- Backend URL might be wrong
- Backend might be sleeping (Render free tier)
- Check external fetch permissions in manifest.yml

## Configuration Summary

After deployment, you should have updated these files:

### Extension
- `donotmiss-extension/background.js` → BACKEND_URL
- `donotmiss-extension/manifest.json` → host_permissions

### Forge App
- `donotmiss-forge/src/index.js` → FLASK_BACKEND_URL
- `donotmiss-forge/manifest.yml` → permissions.external.fetch.backend

### Backend
- Deployed to Render with PostgreSQL
- Environment variables set (DATABASE_URL, FLASK_ENV)

## Render Free Tier Limitations

- **Web Service:** Spins down after 15 minutes of inactivity
- **Database:** 90-day expiration, 1GB storage
- **First Request:** Takes ~30 seconds after spin-down
- **Bandwidth:** 100GB/month

For production use, consider upgrading to paid plans.

## Next Steps

Once everything is working:

1. **Customize the extension icon** - Replace icons in `donotmiss-extension/icons/`
2. **Add more source detection** - Update `detectSource()` in `background.js`
3. **Implement AI task detection** (Phase 2) - Add email/chat scanning
4. **Set up monitoring** - Add error tracking (Sentry, LogRocket)
5. **Publish extension** - Submit to Chrome Web Store
6. **Publish Forge app** - Submit to Atlassian Marketplace

## Support

If you encounter issues:

1. Check browser console for errors
2. Check Forge logs: `forge logs`
3. Check Render logs in dashboard
4. Test backend health endpoint
5. Verify all URLs are updated correctly

## Security Notes

- Never commit `.env` files with real credentials
- Use environment variables for all sensitive data
- Keep DATABASE_URL secret
- Regularly update dependencies
- Enable HTTPS only in production

---

**Congratulations!** 🎉 Your DoNotMiss system is now fully deployed and connected end-to-end.
