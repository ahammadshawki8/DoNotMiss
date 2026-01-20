#!/usr/bin/env python3
"""
Test script for DoNotMiss Backend API
Run this after deploying to verify all endpoints work correctly
"""

import requests
import json
from datetime import datetime, timedelta

# Update this with your Render backend URL
BACKEND_URL = "http://localhost:5000"  # Change to your Render URL for production

def test_health():
    """Test health check endpoint"""
    print("\n🔍 Testing health check...")
    response = requests.get(f"{BACKEND_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Health check passed")

def test_create_task():
    """Test creating a new task"""
    print("\n🔍 Testing task creation...")
    
    task_data = {
        "title": "Test Task from API",
        "description": "This is a test task created via API",
        "source": "web",
        "url": "https://example.com",
        "priority": "high",
        "deadline": (datetime.now() + timedelta(days=7)).date().isoformat(),
        "metadata": {
            "userApproved": True,
            "capturedVia": "test_script"
        }
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/tasks",
        json=task_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 201
    
    task = response.json()
    assert task['title'] == task_data['title']
    assert task['status'] == 'pending'
    print("✅ Task creation passed")
    
    return task['id']

def test_get_tasks():
    """Test getting all tasks"""
    print("\n🔍 Testing get all tasks...")
    response = requests.get(f"{BACKEND_URL}/api/tasks")
    print(f"Status: {response.status_code}")
    tasks = response.json()
    print(f"Found {len(tasks)} tasks")
    assert response.status_code == 200
    assert isinstance(tasks, list)
    print("✅ Get tasks passed")
    return tasks

def test_get_single_task(task_id):
    """Test getting a single task"""
    print(f"\n🔍 Testing get single task (ID: {task_id})...")
    response = requests.get(f"{BACKEND_URL}/api/tasks/{task_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Get single task passed")

def test_mark_sent(task_id):
    """Test marking task as sent to Jira"""
    print(f"\n🔍 Testing mark task as sent (ID: {task_id})...")
    
    data = {
        "jiraKey": "TEST-123",
        "jiraUrl": "https://example.atlassian.net/browse/TEST-123"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/tasks/{task_id}/mark-sent",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    task = response.json()
    print(f"Task status: {task['status']}")
    assert response.status_code == 200
    assert task['status'] == 'sent'
    assert task['jiraKey'] == 'TEST-123'
    print("✅ Mark sent passed")

def test_decline_task(task_id):
    """Test declining a task"""
    print(f"\n🔍 Testing decline task (ID: {task_id})...")
    response = requests.post(f"{BACKEND_URL}/api/tasks/{task_id}/decline")
    print(f"Status: {response.status_code}")
    task = response.json()
    print(f"Task status: {task['status']}")
    assert response.status_code == 200
    assert task['status'] == 'declined'
    print("✅ Decline task passed")

def test_restore_task(task_id):
    """Test restoring a declined task"""
    print(f"\n🔍 Testing restore task (ID: {task_id})...")
    response = requests.post(f"{BACKEND_URL}/api/tasks/{task_id}/restore")
    print(f"Status: {response.status_code}")
    task = response.json()
    print(f"Task status: {task['status']}")
    assert response.status_code == 200
    assert task['status'] == 'pending'
    print("✅ Restore task passed")

def test_delete_task(task_id):
    """Test deleting a task"""
    print(f"\n🔍 Testing delete task (ID: {task_id})...")
    response = requests.delete(f"{BACKEND_URL}/api/tasks/{task_id}")
    print(f"Status: {response.status_code}")
    assert response.status_code == 200
    print("✅ Delete task passed")

def test_filter_tasks():
    """Test filtering tasks by status"""
    print("\n🔍 Testing task filtering...")
    
    # Create tasks with different statuses
    task1_id = test_create_task()
    task2_id = test_create_task()
    
    # Mark one as sent
    test_mark_sent(task1_id)
    
    # Test filter by pending
    response = requests.get(f"{BACKEND_URL}/api/tasks?status=pending")
    pending_tasks = response.json()
    print(f"Pending tasks: {len(pending_tasks)}")
    
    # Test filter by sent
    response = requests.get(f"{BACKEND_URL}/api/tasks?status=sent")
    sent_tasks = response.json()
    print(f"Sent tasks: {len(sent_tasks)}")
    
    # Cleanup
    test_delete_task(task1_id)
    test_delete_task(task2_id)
    
    print("✅ Task filtering passed")

def run_all_tests():
    """Run all API tests"""
    print("=" * 60)
    print("🚀 DoNotMiss Backend API Tests")
    print("=" * 60)
    print(f"Testing backend at: {BACKEND_URL}")
    
    try:
        # Basic tests
        test_health()
        
        # CRUD operations
        task_id = test_create_task()
        test_get_tasks()
        test_get_single_task(task_id)
        
        # Status changes
        test_mark_sent(task_id)
        test_decline_task(task_id)
        test_restore_task(task_id)
        
        # Filtering
        test_filter_tasks()
        
        # Cleanup
        test_delete_task(task_id)
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Could not connect to {BACKEND_URL}")
        print("Make sure the backend is running!")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    import sys
    
    # Allow passing backend URL as argument
    if len(sys.argv) > 1:
        BACKEND_URL = sys.argv[1].rstrip('/')
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
