# Coding Agent

Автономный AI-агент для решения GitHub Issues и создания Pull Requests.

## Архитектура

```
agent/
├── cli.py           # CLI инструмент (точка входа)
├── server.py        # FastAPI webhook сервер
├── worker.py        # Фоновый воркер (каждые 5 сек)
├── issue_solver.py  # Решение issues → PR
├── pr_reviewer.py   # AI ревью Pull Requests
├── ai_client.py     # OpenAI API клиент
├── repo_manager.py  # Git/GitHub операции
├── database.py      # TinyDB wrapper
├── db.json          # База данных (gitignored)
├── repos/           # Клонированные репозитории
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Как это работает

```
1. GitHub webhook → server.py → добавляет issue в db.json
2. worker.py каждые 5 сек проверяет pending issues
3. issue_solver.py:
   - Клонирует репо
   - Для каждого файла спрашивает ChatGPT:
     "Есть ли в этом файле описанная проблема?"
   - ChatGPT отвечает: { issue_found: bool, code_correction: string }
   - Цикл анализ-фикс до 3 раз на файл
   - Создаёт PR с исправлениями
4. pr_reviewer.py анализирует PR (lint, tests, AI review)
5. Если есть проблемы → повторный цикл исправлений
```

## Быстрый старт

### 1. Настройка переменных окружения

```bash
cd agent
cp .env.example .env
# Редактируем .env
```

Необходимые переменные:
```bash
OPENAI_API_KEY=sk-xxx          # Обязательно
GITHUB_TOKEN=ghp_xxx           # Обязательно (Personal Access Token)
GITHUB_WEBHOOK_SECRET=xxx      # Для верификации webhooks
```

### 2. Запуск через Docker (рекомендуется)

```bash
cd agent
docker-compose up -d
```

Это запустит:
- Webhook сервер на порту 8000
- Фоновый воркер

### 3. Локальный запуск

```bash
cd agent
pip install -r requirements.txt

# Запуск сервера и воркера вместе
python cli.py run

# Или по отдельности:
python cli.py start-server   # Webhook сервер
python cli.py start-worker   # Фоновый воркер
```

## CLI Команды

```bash
# Запуск полной системы (server + worker)
python cli.py run

# Только webhook сервер
python cli.py start-server

# Только фоновый воркер
python cli.py start-worker --interval 5

# Обработать конкретный issue
python cli.py process-issue owner/repo 1

# Ревью PR
python cli.py review-pr owner/repo 1

# Список issues в очереди
python cli.py list-issues

# Добавить issue вручную
python cli.py add-issue owner/repo 1 --title "Fix bug"
```

## API Endpoints

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/` | GET | Health check + статистика |
| `/issues` | GET | Список всех issues |
| `/issues/pending` | GET | Только pending issues |
| `/webhook` | POST | GitHub webhook endpoint |
| `/process/{owner}/{repo}/{issue}` | POST | Ручной запуск обработки |

## Формат ответа ChatGPT

Агент требует от ChatGPT отвечать в формате:

```json
{
    "issue_found": true,
    "code_correction": "полное содержимое исправленного файла",
    "explanation": "краткое объяснение что было исправлено"
}
```

## Цикл анализ-фикс

Для каждого файла выполняется до 3 итераций:

1. **Итерация 1**: Анализ → найдена проблема → исправление
2. **Итерация 2**: Проверка исправления → ещё проблемы → исправление
3. **Итерация 3**: Финальная проверка → OK или fail

## GitHub App Setup

1. Создайте GitHub App в Settings → Developer settings → GitHub Apps
2. Permissions:
   - Issues: Read & Write
   - Pull Requests: Read & Write
   - Contents: Read & Write
3. Subscribe to events:
   - Issues
   - Issue comment
   - Pull request
4. Установите Webhook URL: `https://your-server.com/webhook`
5. Установите Webhook Secret

## Переменные окружения

| Переменная | Обязательно | Описание |
|------------|-------------|----------|
| `OPENAI_API_KEY` | ✅ | API ключ OpenAI |
| `OPENAI_BASE_URL` | ❌ | Base URL (default: api.openai.com) |
| `OPENAI_MODEL` | ❌ | Модель (default: gpt-4o-mini) |
| `GITHUB_TOKEN` | ✅ | GitHub Personal Access Token |
| `GITHUB_WEBHOOK_SECRET` | ❌ | Секрет для webhook verification |
| `SERVER_PORT` | ❌ | Порт сервера (default: 8000) |
| `WORKER_INTERVAL` | ❌ | Интервал воркера в секундах (default: 5) |
| `MAX_FIX_ITERATIONS` | ❌ | Макс. итераций на файл (default: 3) |
| `MAX_ATTEMPTS` | ❌ | Макс. попыток на issue (default: 3) |
| `DEBUG` | ❌ | Debug режим (default: true) |
