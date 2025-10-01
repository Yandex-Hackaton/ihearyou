# ihearyou

## Описание

Проект IHearYou - это Telegram-бот с админ-панелью для предоставления информации о нарушениях слуха. Система состоит из Telegram-бота на базе Aiogram, веб-админки на FastAPI с SQLAdmin и PostgreSQL базы данных.

## Системные требования

- Docker Engine 20.10+
- Docker Compose 2.0+
- Git
- Минимум 2GB RAM
- 5GB свободного места на диске

## Развертывание через Docker Compose

### 1. Клонирование репозитория

```bash
# HTTPS
git clone https://github.com/Yandex-Hackaton/ihearyou.git
cd ihearyou/backend

# SSH
git clone git@github.com:Yandex-Hackaton/ihearyou.git
cd ihearyou/backend
```

### 2. Настройка переменных окружения

Создайте файл `.env` в директории `backend/` со следующим содержимым:

```bash
# PostgreSQL настройки
POSTGRES_DB=ihearyou
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_PORT=5432
POSTGRES_HOST=postgres

# Строка подключения к БД
POSTGRES_CONN_STRING=postgresql+asyncpg://postgres:your_secure_password@postgres:5432/ihearyou

# Telegram Bot настройки
BOT_TOKEN=your_telegram_bot_token
ADMINS=123456789

# Админ-панель настройки
SESSION_SECRET_KEY=your_secret_key_here
SESSION_COOKIE_NAME=admin_session

# Логирование
LOG_LEVEL=INFO
```

**Обязательно измените следующие параметры:**
- `POSTGRES_PASSWORD` - установите надежный пароль
- `BOT_TOKEN` - получите токен у @BotFather в Telegram
- `SESSION_SECRET_KEY` - сгенерируйте случайную строку

### 3. Запуск системы

```bash
# Запуск всех сервисов
docker compose up -d

# Просмотр логов
docker compose logs -f

# Остановка сервисов
docker compose down
```

### 4. Проверка работоспособности

После успешного запуска проверьте доступность сервисов:

```bash
# Проверка статуса контейнеров
docker compose ps

# Проверка логов PostgreSQL
docker compose logs postgres

# Проверка логов админ-панели
docker compose logs admin

# Проверка логов бота
docker compose logs bot
```

**Ожидаемый результат:**
- PostgreSQL: контейнер `ihearyou_postgres` в состоянии `Up (healthy)`
- Админ-панель: контейнер `ihearyou_admin` в состоянии `Up`
- Бот: контейнер `ihearyou_bot` в состоянии `Up`

### 5. Доступ к сервисам

- **Админ-панель**: http://localhost:8000
- **PostgreSQL**: localhost:5432 (внешний доступ)
- **Telegram-бот**: активируется автоматически после запуска

### 6. Первоначальная настройка

1. Откройте админ-панель по адресу http://localhost:8000
2. Войдите с учетными данными по умолчанию:
   - Username: `admin`
   - Password: `admin`
3. Смените пароль администратора в разделе "Пользователи"
4. Добавьте категории и контент через интерфейс админки

## Архитектура системы

### Сервисы Docker Compose

- **postgres**: PostgreSQL 15-alpine
  - Порт: 5432
  - Данные: volume `postgres_data`
  - Health check: каждые 10 секунд

- **admin**: FastAPI + SQLAdmin
  - Порт: 8000
  - Автоперезапуск: unless-stopped
  - Зависимость: postgres (healthy)

- **bot**: Aiogram Telegram Bot
  - Автоперезапуск: unless-stopped
  - Зависимость: postgres (healthy)

### Сетевая конфигурация

- Изолированная сеть: `ihearyou_network`
- Тип сети: bridge
- Внутренние имена хостов совпадают с именами сервисов

### Volumes

- `postgres_data`: постоянное хранение данных PostgreSQL

## Управление системой

### Полезные команды Docker Compose

```bash
# Пересборка образов
docker compose build

# Перезапуск конкретного сервиса
docker compose restart admin

# Просмотр логов конкретного сервиса
docker compose logs bot

# Выполнение команд в контейнере
docker compose exec postgres psql -U postgres -d ihearyou

# Остановка с удалением volumes (ВНИМАНИЕ: удалит данные БД)
docker compose down -v
```

### Бэкап базы данных

```bash
# Создание бэкапа
docker compose exec postgres pg_dump -U postgres ihearyou > backup.sql

# Восстановление из бэкапа
docker compose exec -T postgres psql -U postgres ihearyou < backup.sql
```

## Мониторинг и отладка

### Логи системы

Логи сохраняются в контейнерах и доступны через:

```bash
# Все логи
docker compose logs

# Последние 100 строк
docker compose logs --tail=100

# Логи с временными метками
docker compose logs -t
```


## Устранение неполадок

### Частые проблемы

**Проблема**: Контейнеры не запускаются
```bash
# Проверьте логи
docker compose logs

# Проверьте доступность портов
netstat -tulpn | grep :8000
netstat -tulpn | grep :5432
```

**Проблема**: PostgreSQL не подключается
```bash
# Проверьте health check
docker compose ps postgres

# Проверьте логи PostgreSQL
docker compose logs postgres

# Перезапустите с очисткой
docker compose down
docker compose up -d postgres
```

**Проблема**: Бот не отвечает
```bash
# Проверьте токен бота
docker compose logs bot

# Проверьте подключение к БД из бота
docker compose exec bot poetry run python -c "
from data.db import engine
print('Bot DB connection test')
"
```

## Обновление системы

```bash
# Остановка сервисов
docker compose down

# Получение обновлений
git pull origin develop

# Пересборка и запуск
docker compose build
docker compose up -d
```
```