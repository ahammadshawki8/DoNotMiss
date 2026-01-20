# On-Page Task Detection - Setup Guide

## 🎯 Overview

**New Feature:** Extension automatically detects tasks as you browse Gmail, Outlook, Slack, etc. - **NO user API keys needed!**

### How It Works:

```
User visits Gmail → Extension reads email → Sends to YOUR backend → 
YOUR Groq API analyzes → Creates detected tasks → Shows in extension popup
```

**Key Benefits:**
- ✅ Works for ALL users (no setup required from them)
- ✅ Only YOU need Groq API key (on backend)
- ✅ Privacy-friendly (only analyzes visible content)
- ✅ Automatic detection as users browse

---

## 🚀 Setup (5 minutes)

### Step 1: Get Groq API Key (2 min)

1. Go to: https://console.groq.com/
2. Sign up (free, no credit card)
3. Click "API Keys" → "Create API Key"
4. Copy the key (starts with `gsk_...`)

### Step 2: Add to Render Environment (2 min)

1. Go to Render Dashboard: https://dashboard.render.com/
2. Click on your **donotmiss-backend** service
3. Go to "Environment" tab
4. Click "Add Environment Variable"
5. Add:
   - **Key:** `GROQ_API_KEY`
   - **Value:** `gsk_your_key_here`
6. Click "Save Changes"
7. Service will automatically redeploy (wait 2 min)

### Step 3: Deploy Updated Code (1 min)

```bash
git add .
git commit -m "Add on-page task detection"
git push origin main
```

Render will automatically redeploy.

### Step 4: Reload Extension

1. Go to `chrome://extensions/`
2. Find DoNotMiss
3. Click reload icon
4. Done!

---

## 🧪 Test It

### Test on Gmail:

1. **Open Gmail:** https://mail.google.com/
2. **Open an email** with action items (e.g., "Please review the budget report by Friday")
3. **Wait 5 seconds** - Extension scans automatically
4. **See notification:** "🤖 DoNotMiss detected 1 task!"
5. **Click extension icon** - See detected task in popup
6. **Click "Confirm"** - Task moves to Forge Inbox
7. **Open Jira** → DoNotMiss → Send to Jira ✅

### Test on Outlook:

1. Go to: https://outlook.office.com/
2. Open an email
3. Extension detects tasks automatically!

### Test on Slack:

1. Go to: https://slack.com/
2. Open a conversation
3. Extension scans messages for tasks!

---

## 📊 Supported Platforms

| Platform | Status | Auto-Scan |
|----------|--------|-----------|
| Gmail | ✅ Full support | Every 5 sec |
| Outlook | ✅ Full support | Every 5 sec |
| Slack | ✅ Full support | Every 5 sec |
| Teams | ✅ Full support | Every 5 sec |
| Telegram Web | ✅ Full support | Every 5 sec |

---

## 🔐 Privacy & Security

### What Gets Sent to Backend:
- ✅ Email/message text (only what's visible on screen)
- ✅ Subject line
- ✅ Page URL
- ❌ NO passwords
- ❌ NO authentication tokens
- ❌ NO personal data beyond visible text

### User Privacy:
- Users don't need to give any API keys
- Only YOU (the developer) need Groq API key
- Extension only reads content user is actively viewing
- No background scanning of entire inbox

### Your Groq API Key:
- Stored securely on Render (environment variable)
- Never exposed to users
- Used only for AI analysis on YOUR backend

---

## 💰 Cost Estimate

### Groq API (FREE Tier):
- **Limit:** 30 requests/minute, 14,400/day
- **Cost:** $0 (completely free!)

### Typical Usage:
- 1 email viewed = 1 request
- 100 users × 10 emails/day = 1,000 requests/day
- Well within free limits!

### If You Exceed Free Tier:
- Groq has paid plans starting at $0.27 per million tokens
- Very affordable even at scale

---

## 🎯 How It Works Technically

### 1. Page Scanner (Extension)
```javascript
// Runs on Gmail, Outlook, etc.
// Extracts email content every 5 seconds
// Sends to background script
```

### 2. Background Script (Extension)
```javascript
// Receives content from page scanner
// Sends to backend API: POST /api/analyze-tasks
// Receives detected tasks
// Updates badge count
```

### 3. Backend API (Your Server)
```python
# Receives text from extension
# Uses YOUR Groq API key
# Analyzes with Llama 3.3 70B
# Creates tasks with status="detected"
# Returns tasks to extension
```

### 4. Extension Popup
```javascript
// Fetches detected tasks: GET /api/tasks/detected
// Shows in popup UI
// User confirms → status changes to "pending"
// Task appears in Forge Inbox
```

---

## 🔧 Configuration

### Adjust Scan Interval

Edit `donotmiss-extension/page-scanner.js`:
```javascript
const SCAN_INTERVAL = 5000; // Change to 10000 for 10 seconds
```

### Adjust Minimum Text Length

```javascript
const MIN_TEXT_LENGTH = 50; // Change to 100 for longer texts only
```

### Add More Platforms

Edit `manifest.json`:
```json
"matches": [
  "*://mail.google.com/*",
  "*://your-platform.com/*"  // Add new platform
]
```

Then add extraction logic in `page-scanner.js`.

---

## 🐛 Troubleshooting

### "No tasks detected"
- Check if Groq API key is set on Render
- Check backend logs on Render
- Try with email containing clear action items: "Please review X by Friday"

### "Extension not scanning"
- Reload extension: `chrome://extensions/` → Reload
- Check browser console (F12) for errors
- Make sure you're on a supported platform (Gmail, Outlook, etc.)

### "Backend error"
- Check Render logs
- Verify Groq API key is correct
- Test endpoint: `POST https://donotmiss.onrender.com/api/analyze-tasks`

### "Badge not updating"
- Extension updates badge every 30 seconds
- Click refresh in popup to force update
- Check if detected tasks exist: `GET /api/tasks/detected`

---

## 📈 Scaling for Production

### For 1,000+ Users:

1. **Monitor Groq Usage:**
   - Check usage at: https://console.groq.com/
   - Set up alerts for approaching limits

2. **Optimize Scanning:**
   - Increase scan interval to 10-15 seconds
   - Only scan when user is actively viewing email

3. **Add Caching:**
   - Cache analyzed emails (don't re-analyze same email)
   - Store hash of email content

4. **Rate Limiting:**
   - Limit requests per user
   - Queue requests if needed

---

## 🎉 Benefits Over API Key Approach

### Old Way (User API Keys):
- ❌ Each user needs Gmail API setup
- ❌ Each user needs OAuth authentication
- ❌ Complex setup process
- ❌ Privacy concerns (full inbox access)

### New Way (On-Page Detection):
- ✅ Zero setup for users
- ✅ Works immediately after install
- ✅ Only reads visible content
- ✅ You control the AI (one API key)

---

## 🚀 Next Steps

1. ✅ Deploy backend with Groq API key
2. ✅ Reload extension
3. ✅ Test on Gmail
4. 🔮 Add more platforms (Discord, WhatsApp Web, etc.)
5. 🔮 Add caching to reduce API calls
6. 🔮 Add user preferences (scan interval, platforms, etc.)

---

**Setup Time:** 5 minutes
**User Setup:** 0 minutes (just install extension!)
**Cost:** FREE (Groq free tier)
**Privacy:** ✅ Only visible content analyzed
