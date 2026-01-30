import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

# Assuming you have a function to get tasks from the database

def get_tasks():
    # This function should return a list of tasks from the database
    pass

@app.route('/tasks/stats', methods=['GET'])
def get_task_stats():
    tasks = get_tasks()
    total = len(tasks)
    done = sum(1 for task in tasks if task['status'] == 'done')

    if total == 0:
        completion_rate = 0
    else:
        completion_rate = (done / total) * 100  # Safe division now

    return jsonify({'total': total, 'done': done, 'completion_rate': completion_rate})

if __name__ == '__main__':
    app.run(debug=True)