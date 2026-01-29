from flask import Flask, jsonify

app = Flask(__name__)

tasks = [
    {'id': 1, 'name': 'Task 1', 'priority': 1},
    {'id': 2, 'name': 'Task 2', 'priority': 5},
    {'id': 3, 'name': 'Task 3', 'priority': 3}
]

@app.route('/tasks', methods=['GET'])
def get_tasks():
    sorted_tasks = sorted(tasks, key=lambda x: x['priority'], reverse=True)
    return jsonify(sorted_tasks)

if __name__ == '__main__':
    app.run(debug=True)