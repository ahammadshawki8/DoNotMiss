# DoNotMiss

> **AI-Powered Task Capture for Jira** - Never let important tasks slip through the cracks.

Built for the **Atlassian Codegeist 2025 Hackathon**.

---

## 🎯 The Problem

Every day, critical tasks hide in plain sight:
- An urgent request buried in a long email thread
- A quick "can you handle this?" in Slack that gets forgotten
- Action items mentioned in meetings that never make it to Jira

**Result:** Missed deadlines, dropped balls, frustrated teams.

## 💡 The Solution

**DoNotMiss** captures tasks from anywhere on the web and sends them directly to Jira — in seconds.

1. **Select text** on any webpage (Gmail, Slack, Confluence, anywhere)
2. **Right-click → "Add to DoNotMiss"**
3. **Review & send** to Jira with one click

No context switching. No copy-paste. No forgotten tasks.

---

## ✨ Features

### Chrome Extension
- **One-click capture** — Right-click any selected text to create a task
- **Smart detection** — Automatically identifies source type (email, chat, web)
- **Quick form** — Add title, description, priority, and due date
- **AI-detected tasks** — Popup shows potential tasks for quick approval (demo mode)
- **CSP-safe** — Works on sites that block content scripts (Facebook, Messenger)

### Jira Forge App
- **Approval Dashboard** — Review captured tasks before sending to Jira
- **Real Jira Issues** — Creates actual issues with full metadata
- **Source Tracking** — Labels (`donotmiss`, `source-email`) and linked source URLs
- **Team Assignment** — Assign tasks to team members on creation
- **Decline & Restore** — Trash tasks you don't need, restore if you change your mind

### Jira Integration
- **Rich Descriptions** — Source link, timestamp, and original snippet
- **System Comments** — "✨ This task was captured using DoNotMiss"
- **Priority Mapping** — Highest/High/Medium/Low mapped to Jira priorities
- **Due Dates** — Optional deadline synced to Jira

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER'S BROWSER                          │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │ Chrome Extension│───▶│ Capture Modal / Popup           │ │
│  │ (Manifest V3)   │    │ Title, Description, Priority... │ │
│  └─────────────────┘    └───────────────┬─────────────────┘ │
└─────────────────────────────────────────┼───────────────────┘
                                          │
                                          ▼
                    ┌─────────────────────────────────┐
                    │   Flask Backend (Render)        │
                    │   • RESTful API                 │
                    │   • Task Storage                │
                    │   • CORS Enabled                │
                    └──────────┬──────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  PostgreSQL (Render)│
                    │  • Tasks Table      │
                    │  • Metadata         │
                    └──────────┬──────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     ATLASSIAN JIRA                          │
│  ┌─────────────────────────────────────────────────────────┐│
│  │              Forge App (DoNotMiss Dashboard)            ││
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐                 ││
│  │  │  Inbox  │  │  Sent   │  │ Declined│                 ││
│  │  │(Pending)│  │(In Jira)│  │ (Trash) │                 ││
│  │  └────┬────┘  └────┬────┘  └─────────┘                 ││
│  │       │            │                                    ││
│  │       ▼            ▼                                    ││
│  │  ┌─────────────────────────────────────────────────┐   ││
│  │  │           Jira REST API v3                      │   ││
│  │  │  • Create Issue  • Add Comment  • Assign User   │   ││
│  │  └─────────────────────────────────────────────────┘   ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Atlassian Forge CLI (`npm install -g @forge/cli`)
- Chrome browser
- Jira Cloud instance
- Render account (free tier works)
- GitHub account

### Quick Start (15 minutes)

**See [QUICKSTART.md](QUICKSTART.md) for the fastest way to get started!**

Or follow the detailed guide in [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions.

### Verification

Before deploying, run the configuration checker:
```bash
python verify-config.py
```

This will verify all files are properly configured.

### 1. Deploy Backend to Render

```bash
# Push code to GitHub
git push origin main

# Go to Render Dashboard → New Blueprint
# Connect repository → Render auto-deploys from render.yaml
# Get your backend URL: https://donotmiss-backend-xxxx.onrender.com
```

### 2. Install Chrome Extension

```bash
# Update backend URL in donotmiss-extension/background.js
# Then load extension:
# 1. Go to chrome://extensions/
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select donotmiss-extension folder
```

### 3. Deploy Forge App

```bash
cd donotmiss-forge

# Update backend URL in src/index.js and manifest.yml

# Build React dashboard
cd static/dashboard && npm install && npm run build && cd ../..

# Deploy to Forge
forge login
forge register
forge deploy
forge install
```

### 4. Test End-to-End

1. Select text on any webpage → Right-click → "Add to DoNotMiss"
2. Fill form → Click "Add to Jira"
3. Open Jira → Your Project → DoNotMiss
4. See task in Inbox → Click "Send to Jira"
5. Task creates real Jira issue!

---

## 📁 Project Structure

```
donotmiss/
├── README.md
├── DEPLOYMENT.md                 # Complete deployment guide
├── render.yaml                   # Render deployment config
│
├── backend/                      # Flask + PostgreSQL Backend
│   ├── app.py                    # Main Flask application
│   ├── requirements.txt          # Python dependencies
│   ├── Procfile                  # Render start command
│   ├── runtime.txt               # Python version
│   ├── .env.example              # Environment variables template
│   └── README.md                 # Backend documentation
│
├── donotmiss-extension/          # Chrome Extension (Manifest V3)
│   ├── manifest.json
│   ├── background.js             # Service worker, API calls
│   ├── content.js                # Capture modal injection
│   ├── content.css               # Modal styles
│   ├── icons/                    # Extension icons
│   └── popup/                    # Extension popup UI
│       ├── popup.html
│       ├── popup.js
│       ├── capture.html          # Fallback capture window
│       └── capture.js
│
└── donotmiss-forge/              # Atlassian Forge App
    ├── manifest.yml              # Forge configuration
    ├── package.json
    ├── src/
    │   └── index.js              # Resolver functions (API client)
    └── static/
        └── dashboard/            # React dashboard UI
            ├── src/
            │   ├── App.js
            │   ├── App.css
            │   └── index.js
            └── package.json
```

---

## 🔧 Configuration

### Chrome Extension
The extension works out of the box. No configuration needed.

### Forge App
Update `donotmiss-forge/manifest.yml` if you need to:
- Change the app name
- Add additional Jira permissions
- Configure different modules

### Permissions Used
| Permission | Purpose |
|------------|---------|
| `read:jira-work` | Read issues and projects |
| `write:jira-work` | Create issues, add comments |
| `read:jira-user` | Get assignable users |
| `storage:app` | Store captured tasks |

---

## 🎨 Screenshots

### Chrome Extension - Capture Modal
Select text → Right-click → Add to DoNotMiss → Fill details → Send

### Forge Dashboard
Review pending tasks → Send to Jira → Track sent issues

### Jira Issue Created
Full description with source link, labels, and system comment

---

## 🛠️ Tech Stack

- **Backend**: Flask 3.0, PostgreSQL, SQLAlchemy
- **Hosting**: Render (free tier)
- **Chrome Extension**: Manifest V3, Vanilla JS
- **Forge App**: Node.js 20, React 18
- **Jira Integration**: REST API v3, Atlassian Document Format (ADF)
- **Database**: PostgreSQL with JSON support

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Atlassian Forge team for the excellent platform
- Codegeist hackathon organizers
- The Jira community for inspiration

---

<p align="center">
  <strong>DoNotMiss</strong> — Because every task deserves to be tracked.
</p>
