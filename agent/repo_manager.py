from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo/tasks.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    done = db.Column(db.Boolean, default=False)

@app.route('/tasks/stats', methods=['GET'])
def get_task_stats():
    total = Task.query.count()
    done = Task.query.filter_by(done=True).count()

    if total == 0:
        completion_rate = 0  # Set completion rate to 0 when there are no tasks
    else:
        completion_rate = (done / total) * 100  # Calculate completion rate

    return jsonify({'total_tasks': total, 'completed_tasks': done, 'completion_rate': completion_rate})

if __name__ == '__main__':
    app.run(debug=True)