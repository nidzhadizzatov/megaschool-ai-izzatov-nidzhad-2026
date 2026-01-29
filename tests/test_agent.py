from flask import Flask, jsonify
from database import IssueDB

app = Flask(__name__)

# Initialize the database
issue_db = IssueDB('path_to_db.json')

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks sorted by priority in descending order"""
    tasks = issue_db.get_all_tasks()
    sorted_tasks = sorted(tasks, key=lambda x: x['priority'], reverse=True)  # Sort by priority descending
    return jsonify(sorted_tasks)

if __name__ == '__main__':
    app.run(debug=True)