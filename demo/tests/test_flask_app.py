from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE = 'demo/tasks.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done INTEGER DEFAULT 0,
            priority INTEGER DEFAULT 1
        )''')

@app.route('/tasks/stats', methods=['GET'])
def get_stats():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*), SUM(done) FROM tasks')
        total, done = cursor.fetchone()

    # Check for division by zero
    if total == 0:
        completion_rate = 0
    else:
        completion_rate = (done / total) * 100

    return jsonify({
        'total': total,
        'completed': done,
        'completion_rate': completion_rate
    })

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority', 1)

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)',
                       (title, description, priority))
        conn.commit()
        task_id = cursor.lastrowid

    return jsonify({'id': task_id, 'title': title}), 201

@app.route('/tasks', methods=['GET'])
def get_tasks():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks')
        tasks = cursor.fetchall()

    return jsonify({'tasks': tasks, 'count': len(tasks)})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)