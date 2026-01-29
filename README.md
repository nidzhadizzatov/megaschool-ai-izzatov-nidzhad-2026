# GitHub SDLC Coding Agent System

Автоматизированная агентная система для полного цикла разработки (SDLC) внутри GitHub.

## 📋 Описание

Двух-агентная система для автоматизации GitHub workflow:

### Part I: Issue Solver Agent
1. **Webhook** → Issue создан → запись в TinyDB
2. **Worker** (каждые 5 сек) → обрабатывает pending issues
3. **Анализ кода** → проходит по всем файлам, спрашивает ChatGPT: "Есть ли проблема в этом файле?"
4. **Цикл fix-анализ** → до 3 раз на файл: анализ → фикс → анализ → фикс
5. **Pull Request** → создаёт PR с исправлениями
6. **Закрытие Issue** → автоматически

### Part II: PR Review Agent
1. **Webhook** → PR создан → запись в TinyDB
2. **PR Review Worker** (каждые 5 сек) → обрабатывает pending PR reviews
3. **Review файлов** → ТОЛЬКО изменённые файлы (экономия ресурсов)
4. **Формат ответа** → `{ issue_solved: boolean, notes: string }` для каждого файла
5. **GitHub Comment** → сводка всех результатов review

**Все действия выполняются через GitHub: Issues, Pull Requests и GitHub Actions.**

## 📁 Структура проекта

```
.
├── agent/                        # Coding Agent (основная система)
│   ├── cli.py                   # CLI инструмент (точка входа)
│   ├── server.py                # FastAPI webhook сервер (Issues + PRs)
│   ├── worker.py                # Issue solver worker (каждые 5 сек)
│   ├── pr_review_worker.py      # PR review worker (каждые 5 сек)
│   ├── issue_solver.py          # Решение issues → PR
│   ├── pr_reviewer.py           # AI ревью PR (формат: issue_solved, notes)
│   ├── ai_client.py             # OpenAI клиент
│   ├── repo_manager.py          # Git/GitHub операции
│   ├── database.py              # TinyDB wrapper (issues + pr_reviews)
│   ├── supervisord.conf         # Supervisor config (auto-restart)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
│
├── demo/                         # Демо-приложение для тестирования
│   ├── app.py
│   ├── broken_logic.py          # Файл с намеренными багами
│   └── tests/
│
├── .github/
│   ├── workflows/
│   │   ├── code_agent.yml       # Триггер на Issues
│   │   └── reviewer.yml         # Триггер на PR
│   ├── agent_config.yml
│   └── agent_ignore.txt
│
├── .env                          # Environment variables
└── README.md
```

## 🔄 Как это работает

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User creates   │────▶│  Code Agent     │────▶│  Creates PR     │
│     Issue       │     │  analyzes &     │     │  with fixes     │
└─────────────────┘     │  fixes code     │     └────────┬────────┘
                        └─────────────────┘              │
                                                         ▼
### Part I: Issue → PR Flow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Issue opened │─────▶│  Webhook     │─────▶│   TinyDB     │
│  on GitHub   │      │  server.py   │      │  (pending)   │
└──────────────┘      └──────────────┘      └──────────────┘
                                                    │
                                                    ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  PR created  │◀─────│ Issue Solver │◀─────│   Worker     │
│   + Issue    │      │ (fix loop    │      │  (every 5s)  │
│   closed     │      │  up to 3x)   │      └──────────────┘
└──────────────┘      └──────────────┘
       │
       │ (triggers pull_request webhook)
       ▼
┌──────────────┐
│ PR Review    │
│  (Part II)   │
└──────────────┘
```

### Part II: PR → Review Flow

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ PR opened/   │─────▶│  Webhook     │─────▶│   TinyDB     │
│ synchronized │      │  server.py   │      │ pr_reviews   │
└──────────────┘      └──────────────┘      │  (pending)   │
                                             └──────────────┘
                                                    │
                                                    ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Comment to  │◀─────│ PR Reviewer  │◀─────│ PR Review    │
│  GitHub PR   │      │ (ONLY changed│      │  Worker      │
│ (all results)│      │   files)     │      │ (every 5s)   │
└──────────────┘      └──────────────┘      └──────────────┘
                            │
                            │ Format per file:
                            │ { issue_solved: bool, notes: string }
                            ▼
                      ✅ All passed → approve
                      ❌ Issues → comment with details
```

### Детальный процесс:

**Part I:**
1. **Webhook** → `server.py` добавляет issue в `db.json` (table: issues)
2. **Issue Worker** (`worker.py`) каждые 5 секунд проверяет pending issues
3. **Issue Solver** (`issue_solver.py`):
   - Клонирует репозиторий в `repos/{UUID}/`
   - Для каждого файла спрашивает ChatGPT: *"Есть ли в этом файле описанная проблема?"*
   - ChatGPT отвечает: `{ issue_found: bool, code_correction: string }`
   - Цикл анализ-фикс до 3 раз на файл (`MAX_FIX_ITERATIONS=3`)
   - Создаёт PR с исправлениями
   - Закрывает issue

**Part II:**
4. **PR Webhook** → `server.py` добавляет PR в `db.json` (table: pr_reviews)
5. **PR Review Worker** (`pr_review_worker.py`) каждые 5 секунд проверяет pending PR reviews
6. **PR Reviewer** (`pr_reviewer.py`):
   - Получает список изменённых файлов из PR
   - Reviewит **ТОЛЬКО эти файлы** (не весь репозиторий!)
   - Для каждого файла: `{ issue_solved: bool, notes: string }`
   - Добавляет комментарий в PR со всеми результатами

## 🚀 Быстрый старт

### Вариант 1: Docker (рекомендуется)

```bash
# 1. Настройте .env
cp .env.example .env
# Отредактируйте .env (см. раздел "Настройка")

# 2. Запустите систему
docker-compose up -d

# 3. Проверьте логи
docker-compose logs -f
```

**Сервис поднимается одной командой! Supervisor автоматически перезапустит процессы при падении.**

### Вариант 2: Локальный запуск

```bash
cd agent
pip install -r requirements.txt

# Запуск всех сервисов (server + 2 workers)
python cli.py run

# Или запуск отдельных компонентов
python cli.py start-server       # Webhook сервер
python cli.py start-worker       # Issue solver worker
python cli.py start-pr-worker    # PR review worker

# Или обработка конкретного issue
python cli.py process-issue owner/repo 1
```

## ⚙️ Настройка

### Переменные окружения (.env)

```bash
# OpenAI (обязательно)
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-3.5-turbo

# GitHub App (обязательно для webhooks)
GITHUB_APP_ID=2755354
GITHUB_PRIVATE_KEY_PATH=./megaschool-coding-agent.2026-01-29.private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
GITHUB_TOKEN=ghp_xxx  # Personal Access Token

# GitHub Repository (формат: owner/repo)
GITHUB_REPO=izzatov-nidzhad/megaschool-ai-izzatov-nidzhad-2026

# Server
SERVER_PORT=8000

# Database
DB_PATH=./agent/db.json

# Worker settings (VERY IMPORTANT - настройки производительности)
WORKER_INTERVAL=5           # Интервал опроса БД (секунды)
MAX_ATTEMPTS=3              # Максимум попыток на issue/PR
MAX_FIX_ITERATIONS=3        # Максимум циклов fix-analyze на файл

# Repositories storage
REPOS_DIR=./repos
```

### Как создать GitHub App

1. Перейдите: https://github.com/settings/apps
2. Нажмите "New GitHub App"
3. Заполните:
   - **App name**: megaschool-coding-agent
   - **Homepage URL**: https://github.com/izzatov-nidzhad/megaschool-ai-izzatov-nidzhad-2026
   - **Webhook URL**: http://31.187.64.94:8000/webhook (или ваш VPS)
   - **Webhook secret**: придумайте сложный пароль (добавьте в .env)
4. **Permissions**:
   - Repository permissions: Issues (Read & write), Pull requests (Read & write), Contents (Read & write)
5. **Subscribe to events**: Issues, Pull request
6. Нажмите "Create GitHub App"
7. Скачайте private key (.pem файл)
8. Установите App в свой репозиторий (Install App → выберите репозиторий)

### Как получить GitHub Token

1. Перейдите: https://github.com/settings/tokens
2. "Generate new token (classic)"
3. Выберите права: `repo`, `workflow`
4. Скопируйте токен → добавьте в .env
OPENAI_MODEL=gpt-4o-mini

# GitHub (обязательно)
GITHUB_TOKEN=ghp_xxx

# Опционально
GITHUB_WEBHOOK_SECRET=xxx
WORKER_INTERVAL=5
MAX_FIX_ITERATIONS=3
```

### GitHub Secrets

Добавьте в Settings → Secrets → Actions:
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` (опционально)
- `OPENAI_MODEL` (опционально)

## 📖 CLI Команды

```bash
# Полная система (server + worker)
python cli.py run

# Только webhook сервер
python cli.py start-server

# Только воркер
python cli.py start-worker --interval 5

# Обработать issue
python cli.py process-issue owner/repo 1

# Ревью PR
python cli.py review-pr owner/repo 1

# Список issues
python cli.py list-issues
```

## 🔧 GitHub Actions Workflows

### code_agent.yml
- **Триггер**: Issue opened/reopened, комментарий `@coding-agent`
- **Действие**: Анализ issue → генерация кода → создание PR

### reviewer.yml
- **Триггер**: PR opened/synchronize/reopened
- **Действие**: Lint → Tests → AI Review → комментарий в PR

## 🧪 Тестирование

### Демо-приложение

В `demo/` есть файл `broken_logic.py` с намеренными багами:
- Деление на ноль
- Off-by-one ошибки
- Отсутствующие проверки

### Тестовый сценарий

1. Создайте Issue:
   ```
   Title: Fix division by zero in demo/broken_logic.py
   Body: The calculate_average function crashes on empty list
   ```

2. Code Agent автоматически:
   - Проанализирует код
   - Исправит `broken_logic.py`
   - Создаст PR

3. AI Reviewer проверит PR

## 📊 API Endpoints

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/` | GET | Health check + статистика |
| `/issues` | GET | Список всех issues |
| `/issues/pending` | GET | Pending issues |
| `/webhook` | POST | GitHub webhook |
| `/process/{owner}/{repo}/{issue}` | POST | Ручной запуск |

## 🛠️ Технологии

- **Python 3.11+**
- **FastAPI** - webhook сервер
- **OpenAI GPT-4o-mini** - анализ кода
- **PyGithub** - GitHub API
- **GitPython** - Git операции
- **TinyDB** - локальная база
- **Docker** - контейнеризация
- **GitHub Actions** - CI/CD

## 📋 Требования ТЗ

| Требование | Статус |
|------------|--------|
| GitHub Actions workflow | ✅ |
| Code Agent (CLI) | ✅ |
| AI Reviewer Agent | ✅ |
| Несколько итераций правок | ✅ |
| Финальный PR | ✅ |
| Python 3.11+ | ✅ |
| GPT-4o-mini | ✅ |
| GitPython/PyGithub | ✅ |
| ruff, pytest | ✅ |
| Dockerfile | ✅ |
| docker-compose up -d | ✅ |

## 📁 Дополнительная документация

- [Agent README](agent/README.md) - детальная документация агента
- [Demo README](demo/README.md) - как работать с демо-приложением
