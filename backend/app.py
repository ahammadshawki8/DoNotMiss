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
            'createdAt': self.created_at.isoformat(),
            'updatedAt': self.updated_at.isoformat(),
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
