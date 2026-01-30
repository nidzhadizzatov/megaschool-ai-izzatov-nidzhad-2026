"""Broken Logic - файл с намеренными ошибками для тестирования Coding Agent.

ВНИМАНИЕ: Этот файл содержит намеренные баги!
Используется для демонстрации работы Coding Agent.
"""


def calculate_average(numbers: list) -> float:
    """Вычисляет среднее значение списка чисел.
    
    BUG: Деление на ноль при пустом списке!
    
    Args:
        numbers: Список чисел
        
    Returns:
        Среднее значение
    """
    # Проверка на пустой список
    if not numbers:
        return 0.0
    total = sum(numbers)
    return total / len(numbers)


def find_item(items: list, target: str) -> int:
    """Ищет элемент в списке и возвращает индекс.
    
    BUG: Off-by-one ошибка!
    
    Args:
        items: Список элементов
        target: Искомый элемент
        
    Returns:
        Индекс элемента или -1
    """
    # Исправленный диапазон
    for i in range(len(items)):
        if items[i] == target:
            return i
    return -1


def process_data(data: dict) -> dict:
    """Обрабатывает данные.
    
    BUG: Не проверяет наличие ключей!
    
    Args:
        data: Словарь с данными
        
    Returns:
        Обработанные данные
    """
    # Проверка наличия ключей
    result = {
        "name": data.get("name", "").upper(),
        "value": data.get("value", 0) * 2,
        "status": data.get("status", "unknown")  # Обработка отсутствующего ключа
    }
    return result


def divide_numbers(a: float, b: float) -> float:
    """Делит два числа.
    
    BUG: Нет проверки деления на ноль!
    
    Args:
        a: Делимое
        b: Делитель
        
    Returns:
        Результат деления
    """
    # Проверка деления на ноль
    if b == 0:
        raise ValueError("Деление на ноль невозможно")
    return a / b


def get_element_safe(lst: list, index: int) -> any:
    """Безопасно получает элемент списка.
    
    BUG: На самом деле не безопасно!
    
    Args:
        lst: Список
        index: Индекс
        
    Returns:
        Элемент или None
    """
    # Проверка на допустимый индекс
    if 0 <= index < len(lst):
        return lst[index]
    return None


def fibonacci(n: int) -> int:
    """Вычисляет n-ое число Фибоначчи.
    
    BUG: Неэффективная рекурсия без мемоизации!
    BUG: Нет проверки на отрицательные числа!
    
    Args:
        n: Номер числа Фибоначчи
        
    Returns:
        Число Фибоначчи
    """
    # Проверка на отрицательные числа
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
