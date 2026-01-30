from flask import Flask, jsonify

app = Flask(__name__)

tasks = []  # Example task list

@app.route('/tasks/stats', methods=['GET'])
def get_task_stats():
    total = len(tasks)
    done = sum(1 for task in tasks if task['status'] == 'done')
    
    if total == 0:
        completion_rate = 0  # Set completion rate to 0 when there are no tasks
    else:
        completion_rate = (done / total) * 100  # Calculate completion rate
    
    return jsonify({'total': total, 'done': done, 'completion_rate': completion_rate})

if __name__ == '__main__':
    app.run(debug=True)