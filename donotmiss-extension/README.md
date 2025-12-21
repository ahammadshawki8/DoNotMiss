# DoNotMiss Chrome Extension

Capture tasks instantly. Never miss a thing.

## Quick Setup

1. **Convert SVG icons to PNG** (required for Chrome):
   - Open each SVG in `icons/` folder in a browser
   - Screenshot or use an online converter (e.g., svgtopng.com)
   - Save as `icon16.png`, `icon48.png`, `icon128.png`

2. **Load the extension**:
   - Open Chrome → `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select the `donotmiss-extension` folder

3. **Test it**:
   - Go to any webpage
   - Select some text
   - Right-click → "Add to DoNotMiss"
   - Confirm in the popup

## Features

- **Right-click capture**: Select text → Right-click → Add to DoNotMiss
- **Smart source detection**: Automatically detects Email/Chat/Web/Jira
- **Minimal UI**: One modal, one button, done
- **Keyboard shortcuts**: `Esc` to close, `Ctrl+Enter` to submit

## File Structure

```
donotmiss-extension/
├── manifest.json      # Extension config (Manifest V3)
├── background.js      # Service worker (context menu, API calls)
├── content.js         # Capture modal logic
├── content.css        # Modal styles
├── popup/
│   ├── popup.html     # Extension popup
│   ├── popup.css      # Popup styles
│   └── popup.js       # Popup logic
└── icons/
    ├── icon16.svg/png
    ├── icon48.svg/png
    └── icon128.svg/png
```

## Data Contract

Tasks are sent with this structure:

```json
{
  "text": "Finish API documentation",
  "source": "web",
  "url": "https://example.com",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "userApproved": true
}
```

## Connecting to Forge Backend

Update `background.js` line ~45 to point to your Forge app:

```javascript
const endpoint = 'https://your-forge-app.atlassian.net/api/tasks';
```

## Demo Tips

- Works on Gmail, Slack web, any website
- Source badge changes color based on detected source
- Success animation provides clear feedback
- No login required for demo
