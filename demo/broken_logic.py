def calculate_average(numbers: list) -> float:
    """Вычисляет среднее значение списка чисел.
    
    Args:
        numbers: Список чисел
        
    Returns:
        Среднее значение
    """
    if not numbers:
        return 0.0  # Return 0.0 for empty list
    total = sum(numbers)
    return total / len(numbers)


def find_item(items: list, target: str) -> int:
    """Ищет элемент в списке и возвращает индекс.
    
    Args:
        items: Список элементов
        target: Искомый элемент
        
    Returns:
        Индекс элемента или -1
    """
    for i in range(len(items)):
        if items[i] == target:
            return i
    return -1


def process_data(data: dict) -> dict:
    """Обрабатывает данные.
    
    Args:
        data: Словарь с данными
        
    Returns:
        Обработанные данные
    """
    result = {
        "name": data.get("name", "").upper(),  # Use get to avoid KeyError
        "value": data.get("value", 0) * 2,
        "status": data.get("status", "unknown")  # Provide default value
    }
    return result


def divide_numbers(a: float, b: float) -> float:
    """Делит два числа.
    
    Args:
        a: Делимое
        b: Делитель
        
    Returns:
        Результат деления
    """
    if b == 0:
        raise ValueError("Деление на ноль невозможно!")  # Raise an error for division by zero
    return a / b


def get_element_safe(lst: list, index: int) -> any:
    """Безопасно получает элемент списка.
    
    Args:
        lst: Список
        index: Индекс
        
    Returns:
        Элемент или None
    """
    if 0 <= index < len(lst):
        return lst[index]
    return None


def fibonacci(n: int) -> int:
    """Вычисляет n-ое число Фибоначчи.
    
    Args:
        n: Номер числа Фибоначчи
        
    Returns:
        Число Фибоначчи
    """
    if n < 0:
        raise ValueError("n должно быть неотрицательным")  # Raise an error for negative input
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def get_stats() -> dict:
    """Получает статистику задач.
    
    Returns:
        Словарь со статистикой
    """
    tasks = []  # Simulating empty database
    total = len(tasks)
    completed = sum(1 for task in tasks if task.get('completed', False))
    completion_rate = (completed / total) * 100 if total > 0 else 0  # Avoid division by zero
    return {
        'total': total,
        'completed': completed,
        'completion_rate': completion_rate
    }