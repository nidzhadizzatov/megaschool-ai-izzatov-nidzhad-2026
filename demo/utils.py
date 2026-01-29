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
