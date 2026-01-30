"""Утилиты для демо-приложения"""
from datetime import datetime


def greet(name: str) -> str:
    """Возвращает приветствие.
    
    Args:
        name: Имя для приветствия
        
    Returns:
        Строка приветствия
    """
    return f"Hello, {name}!"


def format_date(date: datetime = None) -> str:
    """Форматирует дату.
    
    Args:
        date: Дата для форматирования (по умолчанию - сегодня)
        
    Returns:
        Отформатированная дата
    """
    if date is None:
        date = datetime.now()
    return date.strftime("%Y-%m-%d")


def validate_email(email: str) -> bool:
    """Простая валидация email.
    
    Args:
        email: Email для проверки
        
    Returns:
        True если email валидный
    """
    return "@" in email and "." in email.split("@")[-1]


def clamp(value: int | float, min_val: int | float, max_val: int | float) -> int | float:
    """Ограничивает значение в диапазоне.
    
    Args:
        value: Значение
        min_val: Минимум
        max_val: Максимум
        
    Returns:
        Ограниченное значение
    """
    return max(min_val, min(value, max_val))


def factorial(n: int) -> int:
    """Вычисляет факториал числа.
    
    Args:
        n: Целое число для вычисления факториала
    
    Returns:
        Факториал числа n
    
    Raises:
        ValueError: Если n < 0
    """
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


# Тесты для проверки функции factorial

def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    try:
        factorial(-1)
    except ValueError:
        pass  # Ожидаем, что будет выброшено исключение
    else:
        raise AssertionError("ValueError не был выброшен для n = -1")

    print("Все тесты пройдены!")