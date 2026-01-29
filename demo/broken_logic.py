def get_tasks():
    """Получает список задач.
    
    Returns:
        Список задач, отсортированных по приоритету
    """
    tasks = fetch_tasks_from_database()  # Предполагаем, что эта функция получает задачи из БД
    # Сортируем задачи по приоритету в порядке убывания
    tasks.sort(key=lambda task: task['priority'], reverse=True)
    return tasks
