"""
Unit tests for Task Manager API

Some tests are expected to FAIL due to intentional bugs in the application.
These tests demonstrate the bugs that the Coding Agent will fix.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import app, init_db


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client


def test_index(client):
    """Test health check endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert 'version' in data


def test_create_task_success(client):
    """Test creating a task with valid data."""
    response = client.post('/tasks', json={
        'title': 'Test Task',
        'description': 'Test Description',
        'priority': 1
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test Task'
    assert data['priority'] == 1


def test_create_task_missing_title(client):
    """
    TEST THAT EXPOSES BUG #2: Missing validation
    
    This test SHOULD pass but WILL FAIL because app doesn't validate input!
    Expected: 400 Bad Request
    Actual: 500 Internal Server Error (KeyError)
    """
    response = client.post('/tasks', json={
        'description': 'No title provided'
    })
    # Should return 400, but crashes with 500
    assert response.status_code == 400  # ❌ THIS TEST WILL FAIL!


def test_get_tasks(client):
    """Test getting all tasks."""
    # Create some tasks first
    client.post('/tasks', json={'title': 'Task 1', 'priority': 1})
    client.post('/tasks', json={'title': 'Task 2', 'priority': 3})
    client.post('/tasks', json={'title': 'Task 3', 'priority': 2})
    
    response = client.get('/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 3


def test_task_sorting(client):
    """
    TEST THAT EXPOSES BUG #4: Broken sorting
    
    This test WILL FAIL because tasks are sorted ASC instead of DESC!
    Expected: High priority tasks first
    Actual: Low priority tasks first
    """
    # Create tasks with different priorities
    client.post('/tasks', json={'title': 'Low Priority', 'priority': 1})
    client.post('/tasks', json={'title': 'High Priority', 'priority': 5})
    client.post('/tasks', json={'title': 'Medium Priority', 'priority': 3})
    
    response = client.get('/tasks')
    data = response.get_json()
    tasks = data['tasks']
    
    # High priority should be first
    assert tasks[0]['priority'] == 5  # ❌ THIS TEST WILL FAIL!
    assert tasks[0]['title'] == 'High Priority'


def test_stats_with_no_tasks(client):
    """
    TEST THAT EXPOSES BUG #1: Division by zero
    
    This test WILL FAIL because app crashes when no tasks exist!
    Expected: Returns 0% completion rate
    Actual: ZeroDivisionError
    """
    response = client.get('/tasks/stats')
    # Should work, but crashes with division by zero
    assert response.status_code == 200  # ❌ THIS TEST WILL FAIL!
    data = response.get_json()
    assert data['completion_rate'] == 0


def test_stats_with_tasks(client):
    """Test statistics with some tasks."""
    client.post('/tasks', json={'title': 'Task 1'})
    client.post('/tasks', json={'title': 'Task 2'})
    
    response = client.get('/tasks/stats')
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] == 2
    assert data['completed'] == 0
    assert data['pending'] == 2


def test_get_task(client):
    """Test getting a specific task."""
    # Create a task
    create_response = client.post('/tasks', json={'title': 'Test Task'})
    task_id = create_response.get_json()['id']
    
    # Get the task
    response = client.get(f'/tasks/{task_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Test Task'


def test_update_task(client):
    """Test updating a task."""
    # Create a task
    create_response = client.post('/tasks', json={'title': 'Original Title'})
    task_id = create_response.get_json()['id']
    
    # Update the task
    response = client.put(f'/tasks/{task_id}', json={
        'title': 'Updated Title',
        'done': True
    })
    assert response.status_code == 200
    
    # Verify update
    get_response = client.get(f'/tasks/{task_id}')
    data = get_response.get_json()
    assert data['title'] == 'Updated Title'
    assert data['done'] == 1


def test_delete_task(client):
    """
    Test deleting a task.
    
    BUG #5 exists here (auth bypass) but hard to test without auth system.
    """
    # Create a task
    create_response = client.post('/tasks', json={'title': 'To Delete'})
    task_id = create_response.get_json()['id']
    
    # Delete the task
    response = client.delete(f'/tasks/{task_id}')
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f'/tasks/{task_id}')
    assert get_response.status_code == 404


def test_search_tasks(client):
    """
    Test searching tasks.
    
    BUG #6 (SQL injection) exists but hard to exploit in tests.
    """
    # Create some tasks
    client.post('/tasks', json={'title': 'Python Tutorial'})
    client.post('/tasks', json={'title': 'JavaScript Guide'})
    client.post('/tasks', json={'title': 'Python Advanced'})
    
    # Search for Python tasks
    response = client.get('/tasks/search?q=Python')
    assert response.status_code == 200
    data = response.get_json()
    assert data['count'] == 2


def test_cache_grows(client):
    """
    TEST THAT EXPOSES BUG #3: Memory leak
    
    This test demonstrates the cache grows indefinitely.
    """
    # Create many tasks
    for i in range(10):
        client.post('/tasks', json={'title': f'Task {i}'})
    
    # Check cache size
    response = client.get('/tasks/cache')
    data = response.get_json()
    
    # Cache should have all tasks (this is the bug!)
    assert data['cache_size'] == 10  # This passes, showing the leak


def test_clear_cache(client):
    """Test cache clearing functionality."""
    # Create tasks to fill cache
    for i in range(5):
        client.post('/tasks', json={'title': f'Task {i}'})
    
    # Clear cache
    response = client.post('/tasks/clear-cache')
    assert response.status_code == 200
    data = response.get_json()
    assert data['items_cleared'] == 5
    
    # Verify cache is empty
    cache_response = client.get('/tasks/cache')
    cache_data = cache_response.get_json()
    assert cache_data['cache_size'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
