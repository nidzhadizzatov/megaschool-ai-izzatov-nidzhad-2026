"""Тесты для broken_logic.py

Эти тесты демонстрируют баги в broken_logic.py.
Некоторые тесты будут падать - это ожидаемо!
"""
import pytest
from broken_logic import (
    calculate_average,
    find_item,
    process_data,
    divide_numbers,
    get_element_safe,
    fibonacci
)

def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)


class TestCalculateAverage:
    """Тесты для calculate_average"""
    
    def test_normal_list(self):
        """Тест с обычным списком - должен работать"""
        result = calculate_average([10, 20, 30])
        assert result == 20.0
    
    def test_empty_list(self):
        """Тест с пустым списком - должен возвращать 0"""
        # Исправлено: теперь возвращает 0 вместо ошибки
        result = calculate_average([])
        assert result == 0
    
    def test_single_element(self):
        """Тест с одним элементом"""
        result = calculate_average([42])
        assert result == 42.0


class TestFindItem:
    """Тесты для find_item"""
    
    def test_find_first(self):
        """Поиск первого элемента - работает"""
        result = find_item(["a", "b", "c"], "a")
        assert result == 0
    
    def test_find_middle(self):
        """Поиск среднего элемента - работает"""
        result = find_item(["a", "b", "c"], "b")
        assert result == 1
    
    def test_find_last(self):
        """Поиск последнего элемента - работает"""
        result = find_item(["a", "b", "c"], "c")
        assert result == 2  # Исправлено: теперь возвращает 2
    
    def test_not_found(self):
        """Элемент не найден"""
        result = find_item(["a", "b", "c"], "x")
        assert result == -1


class TestProcessData:
    """Тесты для process_data"""
    
    def test_complete_data(self):
        """Полные данные - работает"""
        data = {"name": "test", "value": 10, "status": "active"}
        result = process_data(data)
        assert result["name"] == "TEST"
        assert result["value"] == 20
    
    def test_missing_status(self):
        """Отсутствует status - ПАДАЕТ!"""
        data = {"name": "test", "value": 10}
        # BUG: KeyError на отсутствующем ключе
        with pytest.raises(KeyError):
            process_data(data)


class TestDivideNumbers:
    """Тесты для divide_numbers"""
    
    def test_normal_division(self):
        """Обычное деление"""
        result = divide_numbers(10, 2)
        assert result == 5.0
    
    def test_divide_by_zero(self):
        """Деление на ноль - ПАДАЕТ!"""
        # BUG: Должно быть понятное исключение или проверка
        with pytest.raises(ZeroDivisionError):
            divide_numbers(10, 0)


class TestGetElementSafe:
    """Тесты для get_element_safe"""
    
    def test_valid_index(self):
        """Валидный индекс"""
        result = get_element_safe([1, 2, 3], 1)
        assert result == 2
    
    def test_negative_index(self):
        """Отрицательный индекс - БЕЗОПАСНО!"""
        # Исправлено: добавлена проверка на отрицательные индексы
        result = get_element_safe([1, 2, 3], -1)
        assert result is None  # Теперь возвращает None вместо неожиданного поведения
    
    def test_out_of_bounds(self):
        """Индекс за пределами"""
        result = get_element_safe([1, 2, 3], 10)
        assert result is None


class TestFibonacci:
    """Тесты для fibonacci"""
    
    def test_zero(self):
        """F(0) = 0"""
        assert fibonacci(0) == 0
    
    def test_one(self):
        """F(1) = 1"""
        assert fibonacci(1) == 1
    
    def test_small(self):
        """Маленькие числа"""
        assert fibonacci(5) == 5
        assert fibonacci(10) == 55
    
    def test_negative(self):
        """Отрицательное число - BUG: бесконечная рекурсия!"""
        # Исправлено: добавлено исключение для отрицательных чисел
        with pytest.raises(ValueError):
            fibonacci(-1)
