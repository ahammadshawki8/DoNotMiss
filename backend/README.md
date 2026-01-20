# DoNotMiss Backend

Flask + PostgreSQL backend for DoNotMiss task management system.

## Features

- RESTful API for task management
- PostgreSQL database with SQLAlchemy ORM
- CORS enabled for Chrome extension and Forge app
- Ready for Render deployment

## API Endpoints

### Health Check
- `GET /health` - Check if server is running

### Tasks
- `GET /api/tasks` - Get all tasks (optional: ?status=pending|sent|declined)
- `GET /api/tasks/:id` - Get single task
- `POST /api/tasks` - Create new task
- `DELETE /api/tasks/:id` - Delete task
- `DELETE /api/tasks` - Clear all tasks

### Task Actions
- `POST /api/tasks/:id/mark-sent` - Mark task as sent to Jira
- `POST /api/tasks/:id/decline` - Decline task
- `POST /api/tasks/:id/restore` - Restore declined task

## Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create PostgreSQL database:
```bash
createdb donotmiss
```

3. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your database URL
```

4. Run the server:
```bash
python app.py
```

Server will run on http://localhost:5000

## Deploy to Render

### 1. Create PostgreSQL Database

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "PostgreSQL"
3. Name: `donotmiss-db`
4. Database: `donotmiss`
5. User: `donotmiss`
6. Region: Choose closest to you
7. Plan: Free
8. Click "Create Database"
9. Copy the "Internal Database URL" (starts with `postgresql://`)

### 2. Create Web Service

1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - Name: `donotmiss-backend`
   - Region: Same as database
   - Branch: `main`
   - Root Directory: `backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Plan: Free

4. Add Environment Variables:
   - `DATABASE_URL`: Paste the Internal Database URL from step 1
   - `FLASK_ENV`: `production`
   - `PYTHON_VERSION`: `3.11.7`

5. Click "Create Web Service"

### 3. Get Your Backend URL

After deployment completes, you'll get a URL like:
```
https://donotmiss-backend.onrender.com
```

### 4. Update Extension and Forge App

Update the backend URL in:

**Extension** (`donotmiss-extension/background.js`):
```javascript
const BACKEND_URL = 'https://donotmiss-backend.onrender.com/api';
```

**Forge App** (`donotmiss-forge/src/index.js`):
```javascript
const FLASK_BACKEND_URL = 'https://donotmiss-backend.onrender.com';
```

**Forge Manifest** (`donotmiss-forge/manifest.yml`):
```yaml
permissions:
  external:
    fetch:
      backend:
        - 'donotmiss-backend.onrender.com'
```

## Database Schema

### Task Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| title | String(500) | Task title |
| description | Text | Task description |
| source | String(50) | Source type (web, email, chat) |
| url | Text | Source URL |
| priority | String(20) | Priority (low, medium, high, highest) |
| deadline | Date | Optional due date |
| status | String(20) | Status (pending, sent, declined) |
| jira_key | String(50) | Jira issue key (e.g., PROJ-123) |
| jira_url | Text | Jira issue URL |
| created_at | DateTime | Creation timestamp |
| updated_at | DateTime | Last update timestamp |
| metadata | JSON | Additional metadata |

## Testing

Test the API with curl:

```bash
# Health check
curl https://donotmiss-backend.onrender.com/health

# Create task
curl -X POST https://donotmiss-backend.onrender.com/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "This is a test",
    "source": "web",
    "priority": "high"
  }'

# Get all tasks
curl https://donotmiss-backend.onrender.com/api/tasks

# Get pending tasks only
curl https://donotmiss-backend.onrender.com/api/tasks?status=pending
```

## Troubleshooting

### Database Connection Issues

If you see connection errors, check:
1. DATABASE_URL is set correctly in Render environment variables
2. Database and web service are in the same region
3. Using "Internal Database URL" (not External)

### CORS Issues

If extension can't connect:
1. Check backend URL in extension code
2. Verify CORS is enabled in app.py
3. Check browser console for errors

### Render Free Tier

- Services spin down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- Database has 90-day expiration on free tier
- Upgrade to paid plan for production use

## License

MIT
