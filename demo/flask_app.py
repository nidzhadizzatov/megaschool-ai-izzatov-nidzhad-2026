"""
Task Manager API - Simple REST API for managing tasks
"""

from flask import Flask, request, jsonify, g
from datetime import datetime
import sqlite3
import json
import os

app = Flask(__name__)

# Configuration
DATABASE = 'tasks.db'
CACHE = {}  # TODO: implement cache eviction policy

def get_db():
    """Get database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Initialize the database."""
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 0,
                done BOOLEAN DEFAULT 0,
                user_id INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        db.commit()

# Initialize DB on startup
init_db()


@app.route('/')
def index():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'message': 'Task Manager API',
        'version': '1.0.0'
    })


@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks."""
    db = get_db()
    cursor = db.execute('SELECT * FROM tasks ORDER BY priority ASC')
    tasks = [dict(row) for row in cursor.fetchall()]
    return jsonify({'tasks': tasks, 'count': len(tasks)})


@app.route('/tasks/stats', methods=['GET'])
def get_stats():
    """Get task statistics."""
    db = get_db()
    cursor = db.execute('SELECT COUNT(*) as total FROM tasks')
    total = cursor.fetchone()['total']
    
    cursor = db.execute('SELECT COUNT(*) as done FROM tasks WHERE done = 1')
    done = cursor.fetchone()['done']
    
    # Check for division by zero
    if total == 0:
        completion_rate = 0
    else:
        completion_rate = (done / total) * 100
    
    return jsonify({
        'total': total,
        'completed': done,
        'pending': total - done,
        'completion_rate': completion_rate
    })


@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task."""
    data = request.get_json()
    title = data['title']
    description = data.get('description', '')
    priority = data.get('priority', 0)
    user_id = data.get('user_id', 1)
    
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO tasks (title, description, priority, user_id, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (title, description, priority, user_id, datetime.now().isoformat(), datetime.now().isoformat())
    )
    db.commit()
    
    task_id = cursor.lastrowid
    
    # Cache the task for quick access
    CACHE[task_id] = {
        'title': title,
        'description': description,
        'cached_at': datetime.now().isoformat()
    }
    
    return jsonify({
        'id': task_id,
        'title': title,
        'description': description,
        'priority': priority,
        'done': False,
        'user_id': user_id
    }), 201


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task."""
    db = get_db()
    cursor = db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    
    return jsonify(dict(task))


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task."""
    data = request.get_json()
    
    db = get_db()
    
    cursor = db.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    if cursor.fetchone() is None:
        return jsonify({'error': 'Task not found'}), 404
    
    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority')
    done = data.get('done')
    
    updated_at = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    
    updates = []
    params = []
    
    if title is not None:
        updates.append('title = ?')
        params.append(title)
    if description is not None:
        updates.append('description = ?')
        params.append(description)
    if priority is not None:
        updates.append('priority = ?')
        params.append(priority)
    if done is not None:
        updates.append('done = ?')
        params.append(1 if done else 0)
    
    updates.append('updated_at = ?')
    params.append(updated_at)
    params.append(task_id)
    
    db.execute(
        f'UPDATE tasks SET {', '.join(updates)} WHERE id = ?',
        params
    )
    db.commit()
    
    return jsonify({'message': 'Task updated', 'id': task_id})


@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task."""
    # TODO: add authentication check
    db = get_db()
    cursor = db.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    db.commit()
    
    if cursor.rowcount == 0:
        return jsonify({'error': 'Task not found'}), 404
    
    # Clear from cache if exists
    if task_id in CACHE:
        del CACHE[task_id]
    
    return '', 204


@app.route('/tasks/search', methods=['GET'])
def search_tasks():
    """Search tasks by keyword."""
    keyword = request.args.get('q', '')
    
    if not keyword:
        return jsonify({'tasks': [], 'count': 0})
    
    db = get_db()
    
    query = f"SELECT * FROM tasks WHERE title LIKE '%{keyword}%' OR description LIKE '%{keyword}%'"
    cursor = db.execute(query)
    
    tasks = [dict(row) for row in cursor.fetchall()]
    
    return jsonify({'tasks': tasks, 'count': len(tasks)})


@app.route('/tasks/cache', methods=['GET'])
def get_cache_stats():
    """Get cache statistics (for debugging memory leak)."""
    return jsonify({
        'cache_size': len(CACHE),
        'cached_tasks': list(CACHE.keys())
    })


@app.route('/tasks/clear-cache', methods=['POST'])
def clear_cache():
    """Clear the task cache (workaround for memory leak)."""
    global CACHE
    old_size = len(CACHE)
    CACHE = {}
    return jsonify({
        'message': 'Cache cleared',
        'items_cleared': old_size
    })


if __name__ == '__main__':
    print("Starting Task Manager API...")
    app.run(debug=True, host='0.0.0.0', port=5000)
