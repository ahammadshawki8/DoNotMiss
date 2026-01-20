#!/usr/bin/env python3
"""
Quick local test for DoNotMiss Backend
Run this to verify your backend works before deploying
"""

import requests
import json
from datetime import datetime, timedelta

# Test against local server
BACKEND_URL = "http://localhost:5000"

def test_health():
    """Test health check"""
    print("\n🔍 Testing health check...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        print(f"✅ Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_create_task():
    """Test creating a task"""
    print("\n🔍 Testing task creation...")
    
    task_data = {
        "title": "Test Task from Local",
        "description": "This is a test task",
        "source": "web",
        "url": "https://example.com",
        "priority": "high",
        "deadline": (datetime.now() + timedelta(days=7)).date().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/tasks",
            json=task_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        print(f"✅ Status: {response.status_code}")
        task = response.json()
        print(f"   Created task ID: {task['id']}")
        print(f"   Title: {task['title']}")
        print(f"   Status: {task['status']}")
        return task['id']
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None

def test_get_tasks():
    """Test getting all tasks"""
    print("\n🔍 Testing get all tasks...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/tasks", timeout=5)
        tasks = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   Found {len(tasks)} tasks")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_mark_sent(task_id):
    """Test marking task as sent"""
    print(f"\n🔍 Testing mark task as sent (ID: {task_id})...")
    
    data = {
        "jiraKey": "TEST-123",
        "jiraUrl": "https://example.atlassian.net/browse/TEST-123"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/tasks/{task_id}/mark-sent",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        task = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"   Task status: {task['status']}")
        print(f"   Jira key: {task['jiraKey']}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_delete_task(task_id):
    """Test deleting a task"""
    print(f"\n🔍 Testing delete task (ID: {task_id})...")
    try:
        response = requests.delete(f"{BACKEND_URL}/api/tasks/{task_id}", timeout=5)
        print(f"✅ Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 DoNotMiss Backend Local Tests")
    print("=" * 60)
    print(f"Testing backend at: {BACKEND_URL}")
    print("\nMake sure the backend is running:")
    print("  cd backend")
    print("  python app.py")
    print()
    
    # Run tests
    if not test_health():
        print("\n❌ Backend is not running!")
        print("Start it with: cd backend && python app.py")
        return
    
    test_get_tasks()
    task_id = test_create_task()
    
    if task_id:
        test_mark_sent(task_id)
        test_delete_task(task_id)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Deploy to Render")
    print("2. Update extension with Render URL")
    print("3. Deploy Forge app")
    print()

if __name__ == "__main__":
    main()
