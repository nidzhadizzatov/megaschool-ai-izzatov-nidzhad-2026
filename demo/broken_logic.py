from flask import Flask, jsonify

app = Flask(__name__)

db = []  # Simulating a database

@app.route('/tasks/stats', methods=['GET'])
def get_task_stats():
    total = len(db)
    done = sum(1 for task in db if task['status'] == 'done')
    if total == 0:
        completion_rate = 0  # Return 0 if no tasks exist
    else:
        completion_rate = (done / total) * 100  # Safe division
    return jsonify({'completion_rate': completion_rate})

if __name__ == '__main__':
    app.run(debug=True)