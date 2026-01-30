def get_stats():
    # Fetch tasks from the database
    tasks = fetch_tasks_from_db()
    total = len(tasks)
    completed = sum(1 for task in tasks if task['completed'])

    # Prevent division by zero
    if total == 0:
        return {'completion_rate': 0}

    completion_rate = (completed / total) * 100
    return {'completion_rate': completion_rate}
