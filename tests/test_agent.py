from flask import Flask, jsonify
from database import IssueDB

app = Flask(__name__)
db = IssueDB('demo/tasks.db')

@app.route('/tasks/stats', methods=['GET'])
def get_stats():
    stats = db.get_stats()
    done = stats.get('completed', 0)
    total = stats.get('total', 0)
    
    # Check for division by zero
    if total == 0:
        completion_rate = 0
    else:
        completion_rate = (done / total) * 100
    
    return jsonify({
        'completion_rate': completion_rate,
        'total_tasks': total,
        'completed_tasks': done
    })

if __name__ == '__main__':
    app.run(debug=True)