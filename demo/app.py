"""Demo Application - точка входа"""
from utils import greet, format_date
from broken_logic import calculate_average, find_item, process_data


def factorial(n):
    """Вычисляет факториал числа n."""
    if n < 0:
        raise ValueError("Факториал не определен для отрицательных чисел.")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def main():
    """Главная функция демо-приложения"""
    print("=" * 40)
    print("Demo Application")
    print("=" * 40)
    
    # Приветствие
    print(greet("World"))
    
    # Дата
    print(f"Today: {format_date()}")
    
    print("-" * 40)
    
    # Демонстрация функций (некоторые могут упасть!)
    try:
        numbers = [10, 20, 30, 40, 50]
        avg = calculate_average(numbers)
        print(f"Average of {numbers}: {avg}")
    except Exception as e:
        print(f"Error in calculate_average: {e}")
    
    try:
        items = ["apple", "banana", "cherry"]
        result = find_item(items, "banana")
        print(f"Found 'banana' at index: {result}")
    except Exception as e:
        print(f"Error in find_item: {e}")
    
    try:
        data = {"name": "Test", "value": 100}
        processed = process_data(data)
        print(f"Processed data: {processed}")
    except Exception as e:
        print(f"Error in process_data: {e}")

    # Тестирование функции факториала
    try:
        print(f"Факториал 5: {factorial(5)}")  # Ожидается 120
        print(f"Факториал -1: {factorial(-1)}")  # Ожидается ValueError
    except ValueError as ve:
        print(f"Ошибка: {ve}")

    print("=" * 40)


if __name__ == "__main__":
    main()