from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/donotmiss')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(app)

# Task Model
class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text)
    source = db.Column(db.String(50), default='web')
    url = db.Column(db.Text)
    priority = db.Column(db.String(20), default='medium')
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='pending')
    jira_key = db.Column(db.String(50), nullable=True)
    jira_url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    task_metadata = db.Column(db.JSON, default={})
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'url': self.url,
            'priority': self.priority,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'status': self.status,
            'jiraKey': self.jira_key,
            'jiraUrl': self.jira_url,
            'createdAt': self.created_at.isoformat() if self.created_at else datetime.utcnow().isoformat(),
            'updatedAt': self.updated_at.isoformat() if self.updated_at else datetime.utcnow().isoformat(),
            'metadata': self.task_metadata or {}
        }

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

# Get all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        status = request.args.get('status')
        query = Task.query
        
        if status:
            query = query.filter_by(status=status)
        else:
            # By default, exclude detected tasks (they're only for extension)
            query = query.filter(Task.status != 'detected')
        
        tasks = query.order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Get single task
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        return jsonify(task.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# Create task (from extension)
@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        
        # Parse deadline if provided
        deadline = None
        if data.get('deadline'):
            try:
                deadline = datetime.fromisoformat(data['deadline'].replace('Z', '+00:00')).date()
            except:
                deadline = None
        
        task = Task(
            title=data.get('title', data.get('text', 'Untitled Task')[:500]),
            description=data.get('description', data.get('text', '')),
            source=data.get('source', 'web'),
            url=data.get('url', ''),
            priority=data.get('priority', 'medium'),
            deadline=deadline,
            status='pending',
            task_metadata=data.get('metadata', {})
        )
        
        db.session.add(task)
        db.session.commit()
        
        return jsonify(task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Mark task as sent to Jira
@app.route('/api/tasks/<int:task_id>/mark-sent', methods=['POST'])
def mark_sent(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        data = request.json
        
        task.status = 'sent'
        task.jira_key = data.get('jiraKey')
        task.jira_url = data.get('jiraUrl')
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(task.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Decline task
@app.route('/api/tasks/<int:task_id>/decline', methods=['POST'])
def decline_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        task.status = 'declined'
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(task.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Restore declined task
@app.route('/api/tasks/<int:task_id>/restore', methods=['POST'])
def restore_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        task.status = 'pending'
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(task.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Confirm detected task (move from detected to pending)
@app.route('/api/tasks/<int:task_id>/confirm', methods=['POST'])
def confirm_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        task.status = 'pending'
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        return jsonify(task.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Get detected tasks (for extension popup)
@app.route('/api/tasks/detected', methods=['GET'])
def get_detected_tasks():
    try:
        tasks = Task.query.filter_by(status='detected').order_by(Task.created_at.desc()).all()
        return jsonify([task.to_dict() for task in tasks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Analyze text for tasks using AI (for on-page detection)
@app.route('/api/analyze-tasks', methods=['POST'])
def analyze_tasks():
    try:
        data = request.json
        text = data.get('text', '')
        source = data.get('source', 'web')
        url = data.get('url', '')
        metadata = data.get('metadata', {})
        
        if not text or len(text) < 50:
            return jsonify({'tasks': []})
        
        # Use Groq AI to detect tasks
        groq_api_key = os.getenv('GROQ_API_KEY')
        
        if not groq_api_key:
            # Fallback to simple keyword detection
            tasks = detect_tasks_simple(text)
        else:
            # Use Groq AI
            try:
                from groq import Groq
                client = Groq(api_key=groq_api_key)
            except Exception as e:
                print(f"Groq initialization error: {e}")
                tasks = detect_tasks_simple(text)
                return jsonify({
                    'tasks': [task.to_dict() for task in [Task(
                        title=t['title'],
                        description=t['description'],
                        source=source,
                        url=url,
                        priority=t['priority'],
                        status='detected',
                        task_metadata={'aiDetected': False, 'detectedAt': datetime.utcnow().isoformat(), **metadata}
                    ) for t in tasks]],
                    'count': len(tasks)
                })
            
            try:
                prompt = f"""
Analyze this text and extract any action items or tasks.
For each task found, provide:
1. A clear task title (max 50 chars)
2. A brief description
3. Priority (low/medium/high/highest)
4. Estimated deadline if mentioned (format: YYYY-MM-DD)

Text:
{text[:2000]}

Return ONLY a JSON array of tasks. If no tasks found, return empty array [].
Format: [{{"title": "...", "description": "...", "priority": "medium", "deadline": "2026-01-25"}}]
"""
                
                response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a task detection assistant. Extract actionable tasks. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                result = response.choices[0].message.content.strip()
                
                # Parse JSON
                import json
                tasks = json.loads(result)
                if not isinstance(tasks, list):
                    tasks = []
            except Exception as e:
                print(f"Groq API error: {e}")
                # Fallback to simple detection
                tasks = detect_tasks_simple(text)
        
        # Create detected tasks in database
        created_tasks = []
        for task_data in tasks:
            # Parse deadline
            deadline = None
            if task_data.get('deadline'):
                try:
                    from datetime import datetime as dt
                    deadline = dt.fromisoformat(task_data['deadline']).date()
                except:
                    deadline = None
            
            task = Task(
                title=task_data.get('title', 'Untitled Task')[:500],
                description=task_data.get('description', ''),
                source=source,
                url=url,
                priority=task_data.get('priority', 'medium'),
                deadline=deadline,
                status='detected',
                task_metadata={
                    'aiDetected': True,
                    'detectedAt': datetime.utcnow().isoformat(),
                    **metadata
                }
            )
            
            db.session.add(task)
            created_tasks.append(task)
        
        if created_tasks:
            db.session.commit()
        
        return jsonify({
            'tasks': [task.to_dict() for task in created_tasks],
            'count': len(created_tasks)
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error analyzing tasks: {e}")
        return jsonify({'error': str(e), 'tasks': []}), 500

def detect_tasks_simple(text):
    """Simple keyword-based task detection (fallback)"""
    import re
    tasks = []
    
    # Keywords that indicate tasks
    patterns = [
        r'please\s+(\w+\s+\w+)',
        r'can you\s+(\w+\s+\w+)',
        r'need to\s+(\w+\s+\w+)',
        r'should\s+(\w+\s+\w+)',
        r'must\s+(\w+\s+\w+)',
        r'action item[s]?:?\s*(.+)',
        r'todo[s]?:?\s*(.+)',
        r'task[s]?:?\s*(.+)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Extract context
            start = max(0, match.start() - 50)
            end = min(len(text), match.end() + 100)
            context = text[start:end].strip()
            
            task = {
                'title': context[:50] + '...' if len(context) > 50 else context,
                'description': context,
                'priority': 'medium',
                'deadline': None
            }
            tasks.append(task)
            
            if len(tasks) >= 3:
                break
    
    return tasks

# Delete task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Clear all tasks (admin)
@app.route('/api/tasks', methods=['DELETE'])
def clear_tasks():
    try:
        Task.query.delete()
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Initialize database
@app.before_request
def create_tables():
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')
