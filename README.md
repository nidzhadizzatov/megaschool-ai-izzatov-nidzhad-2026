# GitHub SDLC Coding Agent System

Автоматизированная агентная система для полного цикла разработки (SDLC) внутри GitHub.

## 📋 Описание

Двух-агентная система для автоматизации GitHub workflow:

### Part I: Issue Solver Agent
1. **Webhook** → Issue создан → запись в TinyDB
2. **Worker** (каждые 5 сек) → обрабатывает pending issues
3. **Клонирование** → репозиторий клонируется в уникальную папку `repos/{UUID}/`
4. **Анализ кода** → проходит по всем файлам (с учётом `.github/agent_ignore.txt`), спрашивает ChatGPT: "Есть ли проблема в этом файле?"
5. **Цикл fix-анализ** → до 3 раз на файл: анализ → фикс → анализ → фикс
6. **Pull Request** → создаёт PR с исправлениями
7. **Cleanup** → удаляет локальную копию репозитория

### Part II: PR Review Agent
1. **Webhook** → PR создан → запись в TinyDB
2. **PR Review Worker** (каждые 5 сек) → обрабатывает pending PR reviews
3. **Review файлов** → ТОЛЬКО изменённые файлы (экономия ресурсов)
4. **Формат ответа** → `{ issue_solved: boolean, notes: string }` для каждого файла
5. **GitHub Comment** → сводка всех результатов review

**Все действия выполняются через GitHub: Issues, Pull Requests и GitHub Actions.**

## 🎯 Ключевые особенности

- ✅ **Изоляция репозиториев** - каждое клонирование в `repos/{UUID}/` для избежания конфликтов
- ✅ **Agent Ignore** - поддержка `.github/agent_ignore.txt` для контроля, какие файлы агент может изменять
- ✅ **Автоматическая очистка** - удаление клонированных репозиториев после обработки
- ✅ **Экономия ресурсов** - PR reviewer обрабатывает только изменённые файлы
- ✅ **Supervisor** - автоматический перезапуск при падении процессов

## 📁 Структура проекта

```
.
├── .github/                      # GitHub App конфигурация
│   ├── agent_config.yml         # Конфигурация агента
│   ├── agent_ignore.txt         # Файлы, которые агент НЕ должен изменять
│   └── workflows/
│       ├── code_agent.yml       # CI: обработка Issues
│       └── reviewer.yml         # CI: ревью PR
│
├── agent/                        # 🤖 Coding Agent (основная система)
│   ├── server.py                # FastAPI webhook сервер
│   ├── worker.py                # Issue solver worker (каждые 5 сек)
│   ├── pr_review_worker.py      # PR review worker (каждые 5 сек)
│   ├── issue_solver.py          # Логика решения issues → PR
│   ├── pr_reviewer.py           # Логика AI ревью PR
│   ├── ai_client.py             # OpenAI API клиент
│   ├── repo_manager.py          # Git/GitHub операции + agent_ignore
│   ├── database.py              # TinyDB wrapper
│   ├── Dockerfile               # Container definition
│   ├── docker-compose.yml       # Запуск всей системы
│   ├── supervisord.conf         # Process management (auto-restart)
│   ├── requirements.txt         # Python dependencies
│   ├── README.md                # Техническая документация агента
│   ├── .env                     # ⚠️ Environment vars (создайте из .env.example)
│   ├── db.json                  # ⚠️ База данных (auto-created, gitignored)
│   └── repos/                   # ⚠️ Клонированные репо (repos/{UUID}/, gitignored)
│
├── demo/                         # 🎯 Демо-приложение для тестирования
│   ├── app.py                   # Главный файл приложения
│   ├── broken_logic.py          # Файл с намеренными багами
│   ├── utils.py                 # Вспомогательные функции
│   ├── README.md                # Инструкция по тестированию
│   └── tests/
│       └── test_broken_logic.py # Тесты (падают до фикса)
│
├── tests/                        # 🧪 Интеграционные тесты агента
│   └── test_agent.py            # Тесты для самого агента
│
├── .env.example                  # 📝 Шаблон для настроек (скопируйте в agent/.env)
├── .gitignore                    # Git ignore (repos/, db.json, .env)
├── README.md                     # 📖 Главная документация (этот файл)
├── QUICKSTART.md                 # ⚡ Быстрый старт для проверяющих
├── DEPLOYMENT.md                 # 🚀 Руководство по развёртыванию
└── STRUCTURE.md                  # 📁 Объяснение структуры проекта
```

> **📌 Важно**: Файл `.env` должен находиться в `agent/.env`, а не в корне проекта!
> 
> ```bash
> cp .env.example agent/.env
> # Затем отредактируйте agent/.env
> ```

> **📁 О папке `repos/`**: Клонированные репозитории сохраняются в `agent/repos/{UUID}/` для изоляции. После обработки они автоматически удаляются.

Полное объяснение структуры: [STRUCTURE.md](STRUCTURE.md)

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

### Шаг 1: Клонирование и настройка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/izzatov-nidzhad/megaschool-ai-izzatov-nidzhad-2026.git
cd megaschool-ai-izzatov-nidzhad-2026

# 2. Создайте .env файл В ПАПКЕ agent/
cp .env.example agent/.env

# 3. Отредактируйте agent/.env (см. раздел "Настройка" ниже)
nano agent/.env  # или используйте любой редактор
```

> **⚠️ Важно**: `.env` файл должен быть в `agent/.env`, не в корне!

### Шаг 2: Настройка GitHub App

**Это необходимо для получения webhooks от GitHub!**

1. Перейдите: https://github.com/settings/apps
2. Нажмите **"New GitHub App"**
3. Заполните форму:
   - **App name**: `megaschool-coding-agent` (или любое уникальное имя)
   - **Homepage URL**: `https://github.com/ваш-username/ваш-repo`
   - **Webhook URL**: `http://ВАШ_IP:8000/webhook` (например: `http://31.187.64.94:8000/webhook`)
   - **Webhook secret**: придумайте сложный пароль (сохраните в `.env` как `GITHUB_WEBHOOK_SECRET`)
   
4. **Permissions** (Repository permissions):
   - Issues: **Read & write**
   - Pull requests: **Read & write**
   - Contents: **Read & write**
   
5. **Subscribe to events**:
   - ✅ Issues
   - ✅ Issue comment
   - ✅ Pull request
   
6. Нажмите **"Create GitHub App"**

7. После создания:
   - Скачайте **private key** (.pem файл)
   - Сохраните его в папку проекта
   - Скопируйте **App ID** (добавьте в `.env`)

8. **Install App**:
   - Перейдите в раздел "Install App" (слева в меню)
   - Выберите ваш репозиторий
   - Нажмите "Install"

### Шаг 3: Запуск на сервере

#### Вариант A: На VPS сервере (рекомендуется)

```bash
# SSH в сервер
ssh root@31.187.64.94
# Пароль: 9GE3drxNOHoDR

# Установите Docker (если ещё не установлен)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Установите docker-compose
apt install docker-compose -y

# Клонируйте проект и настройте
git clone https://github.com/ваш-username/ваш-repo.git
cd ваш-repo

# Настройте .env (вставьте ваши ключи)
nano .env

# Запустите!
cd agent
docker-compose up -d

# Проверьте статус
docker-compose ps
docker-compose logs -f

# Откройте порт 8000 в firewall (если нужно)
ufw allow 8000/tcp
```

#### Вариант B: Локально (для разработки)

```bash
cd agent
pip install -r requirements.txt

# Запуск всех сервисов через supervisor
docker-compose up -d

# Или запуск вручную (в разных терминалах)
python server.py            # Terminal 1: Webhook server
python worker.py            # Terminal 2: Issue solver worker
python pr_review_worker.py  # Terminal 3: PR review worker
```

### Шаг 4: Проверка работы

```bash
# Проверьте health endpoint
curl http://ВАШ_IP:8000/

# Должен вернуть:
# {"status":"ok","pending_issues":0,"stats":{...}}
```

### Шаг 5: Тестирование

1. **Создайте Issue** в своём репозитории:
   ```
   Title: Fix division by zero in demo/broken_logic.py
   
   Body:
   The calculate_average function crashes when passed an empty list.
   Please add a check for empty lists.
   ```

2. **Агент автоматически**:
   - Получит webhook
   - Клонирует репозиторий в `agent/repos/{UUID}/`
   - Проанализирует код
   - Создаст PR с исправлениями
   - Удалит локальную копию

3. **PR Reviewer автоматически**:
   - Получит webhook от PR
   - Проанализирует изменённые файлы
   - Добавит комментарий с результатами review

## ⚙️ Настройка

### Переменные окружения (.env)

**Создайте файл `agent/.env` на основе `.env.example` и заполните следующие переменные:**

```bash
# В корне проекта выполните:
cp .env.example agent/.env

# Затем отредактируйте agent/.env:
nano agent/.env
```

**Содержимое agent/.env:**

```bash
# ============================================
# OpenAI API (ОБЯЗАТЕЛЬНО)
# ============================================
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# ============================================
# GitHub (ОБЯЗАТЕЛЬНО)
# ============================================
# Personal Access Token для работы с GitHub API
# Создайте здесь: https://github.com/settings/tokens
# Права: repo, workflow
GITHUB_TOKEN=ghp_ваш_токен_здесь

# Формат: owner/repo
GITHUB_REPO=izzatov-nidzhad/megaschool-ai-izzatov-nidzhad-2026

# ============================================
# GitHub App (для webhooks)
# ============================================
GITHUB_APP_ID=ваш_app_id
GITHUB_PRIVATE_KEY_PATH=./megaschool-coding-agent.pem
GITHUB_WEBHOOK_SECRET=ваш_webhook_secret

# ============================================
# Server
# ============================================
SERVER_PORT=8000

# ============================================
# Worker Settings
# ============================================
WORKER_INTERVAL=5           # Интервал опроса БД (секунды)
MAX_ATTEMPTS=3              # Максимум попыток на issue/PR
MAX_FIX_ITERATIONS=3        # Максимум циклов fix-analyze на файл

# ============================================
# Paths
# ============================================
DB_PATH=./db.json
REPOS_DIR=./repos            # Папка для клонированных репо (repos/{UUID}/)
```

### Настройка `.github/agent_ignore.txt`

**Этот файл контролирует, какие файлы агент НЕ должен изменять:**

```txt
# Dependencies
node_modules/
.venv/
venv/
__pycache__/
*.pyc

# Build artifacts
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/

# Environment & secrets
.env
.env.*
*.pem
*.key

# Configuration files (should be changed manually)
.github/
*.yml
*.yaml

# Lock files
package-lock.json
yarn.lock
poetry.lock

# Database & data
*.db
*.sqlite
*.json
data/

# Logs
*.log
```

**Агент будет автоматически пропускать эти файлы при анализе!**

### Получение GitHub Token

1. Перейдите: https://github.com/settings/tokens
2. Нажмите **"Generate new token (classic)"**
3. Выберите права:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
4. Нажмите **"Generate token"**
5. Скопируйте токен и добавьте в `.env` как `GITHUB_TOKEN`

### Webhook URL и Firewall

**ВАЖНО:** Ваш сервер должен быть доступен из интернета для получения webhooks от GitHub.

```bash
# Проверьте, открыт ли порт 8000
curl http://ВАШ_IP:8000/

# Если нужно, откройте порт в firewall
ufw allow 8000/tcp

# Или используйте ngrok для локальной разработки
ngrok http 8000
# Webhook URL: https://xxxx.ngrok.io/webhook
```
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

В папке `demo/` находится простое приложение с намеренными багами для тестирования агента.

**Файл `demo/broken_logic.py` содержит:**
- ❌ Деление на ноль в `calculate_average()`
- ❌ Off-by-one ошибки в циклах
- ❌ Отсутствующие проверки входных данных

### Тестовый сценарий

**1. Создайте Issue в своём репозитории:**

```markdown
Title: Fix division by zero in demo/broken_logic.py

Body:
The calculate_average function crashes when passed an empty list.

Steps to reproduce:
1. Call calculate_average([])
2. ZeroDivisionError is raised

Expected:
Function should return 0 or None for empty lists.

Please fix this bug.
```

**2. Code Agent автоматически:**
- ✅ Получит webhook
- ✅ Клонирует репо в `agent/repos/{UUID}/`
- ✅ Проанализирует `demo/broken_logic.py`
- ✅ Найдёт проблему
- ✅ Исправит код (добавит проверку на пустой список)
- ✅ Создаст PR: `fix: resolve issue #1`
- ✅ Удалит локальную копию репозитория
- ✅ Добавит комментарий в Issue со ссылкой на PR

**3. PR Reviewer автоматически:**
- ✅ Получит webhook от созданного PR
- ✅ Проанализирует изменённые файлы
- ✅ Вернёт для каждого файла: `{ issue_solved: true, notes: "Added check for empty list..." }`
- ✅ Добавит комментарий в PR с результатами review

**4. Вы можете:**
- Посмотреть PR
- Одобрить и смержить
- Issue автоматически закроется (если в PR есть `Fixes #N`)

### Ручной запуск (для отладки)

```bash
cd agent

# Обработать конкретный issue
python -c "
from issue_solver import IssueSolver
solver = IssueSolver('izzatov-nidzhad/megaschool-ai-izzatov-nidzhad-2026')
solver.solve_issue(1)
"

# Проверить PR review
python -c "
from pr_reviewer import review_pr_files
result = review_pr_files(pr_number=1, repo_name='owner/repo')
print(result)
"
```

## 📊 API Endpoints

| Endpoint | Method | Описание | Пример ответа |
|----------|--------|----------|---------------|
| `/` | GET | Health check + статистика | `{"status":"ok","pending_issues":0,"stats":{...}}` |
| `/issues` | GET | Список всех issues в БД | `{"issues":[...],"stats":{...}}` |
| `/issues/pending` | GET | Pending issues | `[{doc_id:1,repo:"owner/repo",...}]` |
| `/webhook` | POST | GitHub webhook endpoint | `{"status":"queued","doc_id":1,...}` |

### Примеры запросов

```bash
# Health check
curl http://localhost:8000/

# Список issues
curl http://localhost:8000/issues

# Pending issues
curl http://localhost:8000/issues/pending
```

## 📁 База данных (TinyDB)

Все данные хранятся в `agent/db.json`:

```json
{
  "issues": [
    {
      "doc_id": 1,
      "repo_full_name": "owner/repo",
      "issue_number": 1,
      "title": "Fix bug in demo",
      "status": "pending",
      "created_at": "2026-01-29T20:00:00",
      "pr_number": null
    }
  ],
  "pr_reviews": [
    {
      "doc_id": 1,
      "repo_full_name": "owner/repo",
      "pr_number": 2,
      "status": "pending",
      "created_at": "2026-01-29T20:05:00"
    }
  ]
}
```

**Статусы:**
- `pending` - ожидает обработки
- `processing` - обрабатывается сейчас
- `completed` - успешно обработан
- `failed` - ошибка при обработке

## 🔍 Мониторинг и логи

### Docker logs

```bash
# Все логи
docker-compose logs -f

# Только webhook сервер
docker-compose logs -f server

# Только workers
docker-compose logs -f worker
docker-compose logs -f pr-review-worker
```

### Supervisor status

```bash
# Зайти в контейнер
docker-compose exec agent bash

# Статус всех процессов
supervisorctl status

# Перезапустить процесс
supervisorctl restart server
supervisorctl restart issue_worker
supervisorctl restart pr_review_worker
```

### Типичные логи

```
🔍 Received webhook: issues
📋 New issue: owner/repo#1 - Fix division by zero
✅ Queued issue #1

📥 Cloning owner/repo...
✅ Cloned owner/repo
🌿 Creating branch fix/issue-1
📁 Found 3 files to analyze
📋 Loaded 15 ignore patterns from agent_ignore.txt

📄 Analyzing: demo/broken_logic.py
🔍 Analyzing broken_logic.py...
  [1/3] 🔧 Issue found, applying fix...
  💡 Added check for empty list in calculate_average
  ✅ Fix verified after 1 iteration(s)
✅ Written: demo/broken_logic.py

📝 Fixed 1 file(s):
  - demo/broken_logic.py
⬆️ Pushing fix/issue-1...
✅ Pushed fix/issue-1
✅ Created PR #2
🧹 Cleaning up repos/abc123de
✅ Cleaned up abc123de
```

## 🛠️ Технологии

- **Python 3.11+**
- **FastAPI** - webhook сервер
- **OpenAI GPT-4o-mini** - анализ кода
- **PyGithub** - GitHub API
- **GitPython** - Git операции
- **TinyDB** - локальная база
- **Docker + Docker Compose** - контейнеризация
- **Supervisor** - управление процессами
- **fnmatch** - pattern matching для agent_ignore.txt

## 🎓 Для проверяющих

### Демонстрация работы

1. **Откройте репозиторий**: https://github.com/izzatov-nidzhad/megaschool-ai-izzatov-nidzhad-2026

2. **Создайте Issue** (кнопка "New Issue"):
   ```
   Title: Fix bug in demo/broken_logic.py
   Body: Please fix the division by zero error
   ```

3. **Подождите ~10-15 секунд**:
   - Webhook → агент получит задачу
   - Worker обработает issue
   - Создастся PR с исправлениями
   - PR Review добавит комментарий

4. **Проверьте результат**:
   - Pull Requests → увидите новый PR
   - Issue → увидите комментарий от бота
   - PR → увидите AI review комментарий

### Важные файлы для проверки

- [agent/repo_manager.py](agent/repo_manager.py) - поддержка `.github/agent_ignore.txt` (строки 93-140)
- [agent/issue_solver.py](agent/issue_solver.py) - использование `repos/{UUID}/` (строка 31)
- [.github/agent_ignore.txt](.github/agent_ignore.txt) - конфигурация ignore patterns
- [.gitignore](.gitignore) - исключение `repos/` и `db.json`
- [agent/docker-compose.yml](agent/docker-compose.yml) - запуск одной командой

### Архитектура

```
GitHub Webhook
      ↓
FastAPI Server (:8000)
      ↓
   TinyDB (db.json)
      ↓
  Workers (polling every 5s)
      ↓
┌─────────────────┬──────────────────┐
│  Issue Solver   │   PR Reviewer    │
│  - Clone repo   │   - Get changed  │
│    to repos/    │     files only   │
│    {UUID}/      │   - Review each  │
│  - Analyze all  │     file         │
│    (+ ignore)   │   - Post comment │
│  - Fix × 3      │                  │
│  - Create PR    │                  │
│  - Cleanup      │                  │
└─────────────────┴──────────────────┘
```

## 📋 Соответствие требованиям ТЗ

| Требование | Статус | Реализация |
|------------|--------|------------|
| GitHub Actions workflow | ✅ | `.github/workflows/code_agent.yml` и `reviewer.yml` |
| Code Agent (CLI) | ✅ | `agent/issue_solver.py` + `agent/server.py` |
| AI Reviewer Agent | ✅ | `agent/pr_reviewer.py` + `agent/pr_review_worker.py` |
| Несколько итераций правок | ✅ | До 3 итераций на файл (настраивается) |
| Финальный PR | ✅ | Создаётся автоматически с описанием |
| Python 3.11+ | ✅ | Используется 3.11 |
| GPT-4o-mini | ✅ | Настраивается в `.env` |
| GitPython/PyGithub | ✅ | Используются обе библиотеки |
| ruff, pytest | ✅ | Настроены в workflows |
| Dockerfile | ✅ | `agent/Dockerfile` |
| docker-compose up -d | ✅ | Работает из коробки |
| **Repos isolation** | ✅ | **`repos/{UUID}/` для каждого клона** |
| **Agent ignore** | ✅ | **`.github/agent_ignore.txt` поддержка** |
| **Auto cleanup** | ✅ | **Удаление после обработки** |

## 🚨 Важные замечания

### Безопасность

- ⚠️ **НЕ коммитьте `.env` файл!** (уже в `.gitignore`)
- ⚠️ **НЕ коммитьте `.pem` ключи!** (уже в `.gitignore`)
- ✅ Используйте GitHub Secrets для CI/CD
- ✅ Webhook secret защищает от поддельных запросов

### Производительность

- Агент обрабатывает файлы до 50KB (настраивается)
- PR Reviewer проверяет **только изменённые файлы**
- Workers опрашивают БД каждые 5 секунд (настраивается)
- Клонированные репозитории автоматически удаляются

### Стоимость OpenAI API

- Модель `gpt-4o-mini` - самая дешёвая (~$0.15 / 1M tokens)
- Средний файл: ~500-1000 tokens
- 1 issue с 5 файлами ≈ 0.01-0.02 USD
- Для демонстрации вполне подходит

## 📞 Контакты

- **GitHub**: https://github.com/izzatov-nidzhad
- **Репозиторий**: https://github.com/izzatov-nidzhad/megaschool-ai-izzatov-nidzhad-2026

---

**Bro, if you deliver this in this format, with the app running live, it's going to be perfect** 🚀
