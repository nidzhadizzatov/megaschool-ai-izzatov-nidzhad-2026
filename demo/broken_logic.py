"""Broken Logic - файл с намеренными ошибками для тестирования Coding Agent.

ВНИМАНИЕ: Этот файл содержит намеренные баги!
Используется для демонстрации работы Coding Agent.
"""

def calculate_average(numbers: list) -> float:
    """Вычисляет среднее значение списка чисел.
    
    Args:
        numbers: Список чисел
        
    Returns:
        Среднее значение
    """
    # FIX: Проверяем пустой список
    if not numbers:
        return 0.0
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
    # FIX: Правильный диапазон (должен быть range(len(items)))
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
    # FIX: Проверяем наличие ключей
    result = {
        "name": data.get("name", "").upper(),
        "value": data.get("value", 0) * 2,
        "status": data.get("status", "unknown")  # FIX: Проверяем наличие ключа
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
    # FIX: Проверка b != 0
    if b == 0:
        raise ValueError("Деление на ноль невозможно")
    return a / b


def get_element_safe(lst: list, index: int) -> any:
    """Безопасно получает элемент списка.
    
    Args:
        lst: Список
        index: Индекс
        
    Returns:
        Элемент или None
    """
    # FIX: Проверяем нижнюю и верхнюю границы
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
    # FIX: Проверка n < 0
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    if n <= 1:
        return n
    # FIX: Используем мемоизацию для повышения производительности
    memo = {0: 0, 1: 1}
    def fib_helper(n):
        if n not in memo:
            memo[n] = fib_helper(n - 1) + fib_helper(n - 2)
        return memo[n]
    return fib_helper(n)
