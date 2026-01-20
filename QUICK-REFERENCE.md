# DoNotMiss - Quick Reference Card

## 🚀 Deployment Commands

### Backend (Render)
```bash
git push origin main
# Then: Render Dashboard → New Blueprint → Connect repo
```

### Extension (Chrome)
```bash
# Update URLs in:
# - donotmiss-extension/background.js (line 88)
# - donotmiss-extension/manifest.json (host_permissions)

# Load: chrome://extensions/ → Load unpacked → Select folder
```

### Forge (Jira)
```bash
cd donotmiss-forge/static/dashboard
npm install && npm run build
cd ../..

forge login
forge register
forge deploy
forge install
```

---

## 📝 Configuration Checklist

- [ ] Backend deployed to Render
- [ ] Backend URL: `https://_____________________________.onrender.com`
- [ ] Extension `background.js` updated with backend URL
- [ ] Extension `manifest.json` updated with backend URL
- [ ] Extension loaded in Chrome
- [ ] Forge `src/index.js` updated with backend URL
- [ ] Forge `manifest.yml` updated with backend URL
- [ ] Forge React app built
- [ ] Forge app deployed and installed

---

## 🧪 Testing Commands

### Verify Configuration
```bash
python verify-config.py
```

### Test Backend Locally
```bash
cd backend
python app.py
# In another terminal:
python test_local.py
```

### Test Backend Production
```bash
curl https://your-backend-url.onrender.com/health
```

### View Forge Logs
```bash
cd donotmiss-forge
forge logs
```

---

## 🔗 API Endpoints

### Backend
```
GET  /health                    - Health check
GET  /api/tasks                 - Get all tasks
POST /api/tasks                 - Create task
POST /api/tasks/:id/mark-sent   - Mark as sent
POST /api/tasks/:id/decline     - Decline task
POST /api/tasks/:id/restore     - Restore task
DELETE /api/tasks/:id           - Delete task
```

### Test API
```bash
# Health check
curl https://your-url.onrender.com/health

# Create task
curl -X POST https://your-url.onrender.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","source":"web","priority":"high"}'

# Get all tasks
curl https://your-url.onrender.com/api/tasks
```

---

## 🎯 Data Flow

```
User selects text
    ↓
Right-click → "Add to DoNotMiss"
    ↓
Modal appears → Fill form → Submit
    ↓
Extension → POST /api/tasks → Backend
    ↓
Backend → Store in PostgreSQL
    ↓
Forge → GET /api/tasks → Backend
    ↓
Forge displays in Inbox tab
    ↓
User clicks "Send to Jira"
    ↓
Forge → POST /rest/api/3/issue → Jira
    ↓
Jira issue created ✅
```

---

## 🔧 Troubleshooting

### Extension: "Failed to create task"
```bash
# Check backend
curl https://your-url.onrender.com/health

# Check browser console (F12)
# Verify BACKEND_URL in background.js
# Verify host_permissions in manifest.json
```

### Forge: "No tasks found"
```bash
# Click "Refresh" button
# Check Forge logs
forge logs

# Verify backend URL in src/index.js
# Test backend directly
curl https://your-url.onrender.com/api/tasks
```

### Backend: Slow response
```
Normal for Render free tier after 15 min inactivity
First request takes ~30 seconds (cold start)
Subsequent requests are fast
```

---

## 📂 Important Files

### Must Update After Deployment
- `donotmiss-extension/background.js` (line 88)
- `donotmiss-extension/manifest.json` (host_permissions)
- `donotmiss-forge/src/index.js` (line 6)
- `donotmiss-forge/manifest.yml` (permissions.external.fetch)

### Configuration Files
- `backend/.env.example` - Environment variables
- `render.yaml` - Render deployment config
- `backend/requirements.txt` - Python dependencies
- `donotmiss-forge/package.json` - Node dependencies

---

## 📚 Documentation

- **START-HERE.md** - Entry point
- **QUICKSTART.md** - 15-minute setup
- **DEPLOYMENT.md** - Detailed guide
- **SYSTEM-OVERVIEW.md** - Architecture
- **CHECKLIST.md** - Verification
- **FINAL-SUMMARY.md** - Complete summary

---

## 🎯 Success Criteria

✅ Backend health check returns 200
✅ Extension captures tasks
✅ Tasks appear in Forge dashboard
✅ Can create Jira issues
✅ End-to-end flow works

---

## 🔑 Key URLs

### After Deployment
- Backend: `https://donotmiss-backend-xxxx.onrender.com`
- Jira: `https://your-site.atlassian.net`
- Extension: `chrome://extensions/`

### Development
- Render Dashboard: https://dashboard.render.com/
- Forge CLI Docs: https://developer.atlassian.com/platform/forge/
- Chrome Extensions: https://developer.chrome.com/docs/extensions/

---

## ⚡ Quick Commands

```bash
# Verify config
python verify-config.py

# Test backend
cd backend && python test_local.py

# Build Forge
cd donotmiss-forge/static/dashboard && npm run build

# Deploy Forge
cd donotmiss-forge && forge deploy

# View logs
forge logs

# Reload extension
# chrome://extensions/ → Click reload icon
```

---

## 📊 Task States

- **pending** - New task in Inbox
- **sent** - Created as Jira issue
- **declined** - In Trash

---

## 🎨 Priority Mapping

| Extension | Jira |
|-----------|------|
| Highest   | 1    |
| High      | 2    |
| Medium    | 3    |
| Low       | 4    |

---

## 🔐 Security

- ✅ CORS enabled for extension and Forge
- ✅ HTTPS only in production
- ✅ No credentials in code
- ✅ Environment variables for sensitive data
- ✅ Forge OAuth for Jira access

---

## 📈 Performance

### Backend (Render Free)
- Cold start: ~30s
- Warm: <500ms
- Database: 1GB

### Extension
- Modal: Instant
- API: <2s

### Forge
- Load: <3s
- Sync: <1s
- Create: <2s

---

## 🆘 Support

1. Check browser console (F12)
2. Check Forge logs: `forge logs`
3. Check Render logs in dashboard
4. Test backend: `curl https://your-url.onrender.com/health`
5. Read documentation files

---

**Quick Reference v1.0**
**Last Updated:** January 20, 2026
