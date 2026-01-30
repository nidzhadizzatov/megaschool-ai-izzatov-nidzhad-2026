"""
Unit tests for the Task Manager API
"""

import pytest
import json
import os
from flask_app import app, init_db

@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    
    # Use a test database
    app.config['DATABASE'] = ':memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_create_task_success(client):
    """Test creating a task with valid data."""
    response = client.post('/tasks',
                          data=json.dumps({
                              'title': 'Test Task',
                              'description': 'A test task',
                              'priority': 1
                          }),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Task'
    assert data['id'] is not None


def test_create_task_missing_title(client):
    """Test that POST /tasks returns error when title is missing."""
    response = client.post('/tasks',
                          data=json.dumps({
                              'description': 'No title'
                          }),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_get_tasks(client):
    """Test getting all tasks."""
    # Create some tasks
    client.post('/tasks',
               data=json.dumps({'title': 'Task 1', 'priority': 1}),
               content_type='application/json')
    
    client.post('/tasks',
               data=json.dumps({'title': 'Task 2', 'priority': 2}),
               content_type='application/json')
    
    response = client.get('/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 2


def test_task_sorting(client):
    """Test that tasks are sorted by priority (highest first)."""
    client.post('/tasks',
               data=json.dumps({'title': 'Low Priority', 'priority': 1}),
               content_type='application/json')
    
    client.post('/tasks',
               data=json.dumps({'title': 'High Priority', 'priority': 5}),
               content_type='application/json')
    
    response = client.get('/tasks')
    data = json.loads(response.data)
    
    assert data['tasks'][0]['priority'] == 5
    assert data['tasks'][0]['title'] == 'High Priority'


def test_stats_with_tasks(client):
    """Test statistics endpoint with tasks."""
    # Create tasks
    client.post('/tasks',
               data=json.dumps({'title': 'Task 1', 'done': False}),
               content_type='application/json')
    
    client.post('/tasks',
               data=json.dumps({'title': 'Task 2', 'done': True}),
               content_type='application/json')
    
    response = client.get('/tasks/stats')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 2
    assert data['completed'] == 1
    assert data['completion_rate'] == 50.0


def test_stats_with_no_tasks(client):
    """Test stats endpoint when database is empty."""
    response = client.get('/tasks/stats')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total'] == 0
    assert data['completion_rate'] == 0


def test_get_specific_task(client):
    """Test getting a specific task."""
    # Create a task
    response = client.post('/tasks',
                          data=json.dumps({'title': 'Specific Task'}),
                          content_type='application/json')
    task_id = json.loads(response.data)['id']
    
    # Get it
    response = client.get(f'/tasks/{task_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Specific Task'


def test_get_nonexistent_task(client):
    """Test getting a task that doesn't exist."""
    response = client.get('/tasks/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data


def test_update_task(client):
    """Test updating a task."""
    # Create a task
    response = client.post('/tasks',
                          data=json.dumps({'title': 'Original Title'}),
                          content_type='application/json')
    task_id = json.loads(response.data)['id']
    
    # Update it
    response = client.put(f'/tasks/{task_id}',
                         data=json.dumps({'title': 'Updated Title', 'done': True}),
                         content_type='application/json')
    assert response.status_code == 200
    
    # Verify update
    response = client.get(f'/tasks/{task_id}')
    data = json.loads(response.data)
    assert data['title'] == 'Updated Title'
    assert data['done'] == 1


def test_delete_task(client):
    """Test deleting a task."""
    # Create a task
    response = client.post('/tasks',
                          data=json.dumps({'title': 'To Delete'}),
                          content_type='application/json')
    task_id = json.loads(response.data)['id']
    
    # Delete it
    response = client.delete(f'/tasks/{task_id}')
    assert response.status_code == 204
    
    # Verify deletion
    response = client.get(f'/tasks/{task_id}')
    assert response.status_code == 404


def test_search_tasks(client):
    """Test searching tasks."""
    # Create tasks
    client.post('/tasks',
               data=json.dumps({'title': 'Python Project', 'description': 'Learn Python'}),
               content_type='application/json')
    
    client.post('/tasks',
               data=json.dumps({'title': 'JavaScript Project', 'description': 'Learn JS'}),
               content_type='application/json')
    
    # Search for Python
    response = client.get('/tasks/search?q=Python')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] >= 1
    assert any('Python' in task['title'] or 'Python' in task['description'] 
              for task in data['tasks'])


def test_cache_growth(client):
    """Test cache behavior when creating multiple tasks."""
    for i in range(10):
        client.post('/tasks',
                   data=json.dumps({'title': f'Task {i}'}),
                   content_type='application/json')
    
    response = client.get('/tasks/cache')
    data = json.loads(response.data)
    assert data['cache_size'] == 10


def test_cache_clear(client):
    """Test clearing the cache."""
    # Create tasks
    client.post('/tasks',
               data=json.dumps({'title': 'Task 1'}),
               content_type='application/json')
    
    # Clear cache
    response = client.post('/tasks/clear-cache')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['items_cleared'] > 0
    
    # Verify cache is empty
    response = client.get('/tasks/cache')
    data = json.loads(response.data)
    assert data['cache_size'] == 0
