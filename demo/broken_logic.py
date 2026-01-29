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
    # BUG: Не проверяем пустой список
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
    # BUG: Неправильный диапазон (должен быть range(len(items)))
    for i in range(len(items) - 1):
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
    # BUG: Предполагаем что все ключи существуют
    result = {
        "name": data["name"].upper(),
        "value": data["value"] * 2,
        "status": data["status"]  # BUG: этого ключа может не быть
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
    # BUG: Нет проверки b != 0
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
    # BUG: Проверяем только верхнюю границу
    if index < len(lst):
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
    # BUG: Нет проверки n < 0
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
