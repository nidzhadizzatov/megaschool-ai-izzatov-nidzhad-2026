# Деплой на VPS (31.187.64.94)

## Подключение

```bash
ssh root@31.187.64.94
# Пароль: 9GE3drxNOHoDR
```

## Установка

```bash
# 1. Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 2. Клонирование репозитория
cd /root
git clone https://github.com/izzatov-nidzhad/megaschool-ai-izzatov-nidzhad-2026.git
cd megaschool-ai-izzatov-nidzhad-2026

# 3. Настройка .env
nano .env
# Вставьте все переменные из локального .env
# Ctrl+O → Enter → Ctrl+X

# 4. Копирование private key
# (с локальной машины)
scp megaschool-coding-agent.2026-01-29.private-key.pem root@31.187.64.94:/root/megaschool-ai-izzatov-nidzhad-2026/

# 5. Открытие портов
ufw allow 8000/tcp
ufw allow 22/tcp
ufw enable

# 6. Запуск системы
docker-compose up -d

# 7. Проверка логов
docker-compose logs -f
```

## Проверка работы

```bash
# Статус контейнера
docker-compose ps

# Проверка webhook endpoint
curl http://localhost:8000/
# Должен вернуть: {"status":"ok","pending_issues":0,...}

# Логи в реальном времени
docker-compose logs -f coding_agent

# Статистика из БД
docker-compose exec coding_agent python cli.py list-issues
```

## Настройка GitHub App Webhook

После запуска на VPS:

1. Вернитесь в настройки GitHub App: https://github.com/settings/apps
2. Откройте вашу App → Edit
3. В поле **Webhook URL** введите: `http://31.187.64.94:8000/webhook`
4. Сохраните

## Тестирование

1. Откройте ваш репозиторий
2. Создайте новый Issue с описанием проблемы
3. Наблюдайте за логами:
   ```bash
   docker-compose logs -f
   ```
4. Через 5-15 секунд должен появиться PR с исправлением
5. PR автоматически вызовет PR review worker
6. В PR появится комментарий с результатами review

## Управление

```bash
# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Обновление кода
git pull
docker-compose down
docker-compose up -d --build

# Очистка всех данных
docker-compose down -v
```

## Мониторинг ресурсов

```bash
# Использование CPU/RAM
docker stats coding_agent

# Размер логов
du -sh /var/lib/docker/containers/*/

# Очистка старых логов (если разрастаются)
docker-compose logs --tail=1000 > logs_backup.txt
docker-compose down
docker-compose up -d
```

## Troubleshooting

### Проблема: контейнер падает

```bash
docker-compose logs coding_agent
# Смотрим последние ошибки
```

### Проблема: webhook не приходит

1. Проверьте, открыт ли порт 8000:
   ```bash
   curl http://31.187.64.94:8000/
   ```
2. Проверьте webhook secret в GitHub App и .env
3. Проверьте логи GitHub App: Settings → Developer settings → GitHub Apps → Advanced → Recent Deliveries

### Проблема: AI не работает

1. Проверьте OPENAI_API_KEY:
   ```bash
   docker-compose exec coding_agent printenv | grep OPENAI
   ```
2. Проверьте лимиты API на https://platform.openai.com/usage

### Проблема: нет доступа к GitHub

1. Проверьте GITHUB_TOKEN:
   ```bash
   docker-compose exec coding_agent python -c "from github import Github; g = Github('YOUR_TOKEN'); print(g.get_user().login)"
   ```

## Автоматический запуск при перезагрузке

```bash
# Добавить в crontab
crontab -e
# Вставить:
@reboot cd /root/megaschool-ai-izzatov-nidzhad-2026 && docker-compose up -d
```

## Полезные команды

```bash
# Войти в контейнер
docker-compose exec coding_agent bash

# Проверить Python окружение
docker-compose exec coding_agent python --version
docker-compose exec coding_agent pip list

# Проверить базу данных
docker-compose exec coding_agent cat /app/data/db.json | head -n 50
```
