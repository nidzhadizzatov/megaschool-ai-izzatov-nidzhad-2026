# Demo Application

Демонстрационное приложение с намеренными ошибками для тестирования Coding Agent.

## Структура

```
demo/
├── app.py              # Основное приложение
├── utils.py            # Утилиты
├── broken_logic.py     # Файл с ошибками (для тестирования агента)
├── tests/
│   └── test_broken_logic.py
└── README.md
```

## Как использовать

### 1. Запуск приложения

```bash
cd demo
python app.py
```

### 2. Тестирование ошибок

В файле `broken_logic.py` есть намеренные ошибки:
- Деление на ноль
- Off-by-one ошибки
- Неправильная логика

### 3. Запуск тестов

```bash
cd demo
pytest tests/ -v
```

## Тестирование Coding Agent

1. Создайте issue в репозитории:
   - Заголовок: "Fix division by zero in broken_logic.py"
   - Описание: "The calculate_average function crashes when given an empty list"

2. Coding Agent автоматически:
   - Проанализирует код
   - Найдёт проблему
   - Создаст PR с исправлением

3. PR Reviewer проверит исправление
