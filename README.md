# LMS System (Online Learning Platform)

Бэкенд для платформы онлайн-обучения. Предоставляет REST API для управления пользователями, курсами и уроками.

## Технологии

- Python 3.13+
- Django 6.0
- Django REST Framework
- PostgreSQL
- Redis / Celery
- Docker, Docker Compose

## Запуск через Docker (рекомендуется)

Весь проект (БД, Redis, Django, Celery worker и beat) поднимается одной командой.

1. **Установить Docker Desktop** и убедиться, что он запущен.

2. **Создать файл `.env`** из шаблона и при необходимости поправить значения:

   ```bash
   cp .env.example .env
   ```

   Укажите реальные `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` и `STRIPE_API_KEY`,
   чтобы работали уведомления на почту и оплата.

3. **Запустить все сервисы:**

   ```bash
   docker compose up --build -d
   ```

   При первом старте выполнятся сборка образа и миграции БД.

4. **Проверить статус:**

   ```bash
   docker compose ps
   ```

5. **Создать суперпользователя** (для админки и доступа к API):

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

Приложение будет доступно по адресу `http://127.0.0.1:8000/`.

Полезные команды:

- `docker compose logs -f web` — логи приложения
- `docker compose down` — остановить сервисы (данные сохраняются)
- `docker compose down -v` — остановить и удалить данные (volumes)

### Сервисы

| Сервис          | Описание                                    | Доступ с хоста |
|-----------------|---------------------------------------------|----------------|
| `db`            | PostgreSQL, данные в volume `pg_data`        | нет (`expose`) |
| `redis`         | Redis для Celery, данные в volume `redis_data` | нет (`expose`) |
| `web`           | Django (миграции + runserver)               | `localhost:8000` |
| `celery_worker` | Celery worker (фоновые задачи)              | нет            |
| `celery_beat`   | Celery beat (периодические задачи)          | нет            |

Данные БД, Redis и загруженных медиа-файлов хранятся в Docker volumes,
поэтому переживают перезапуск контейнеров.

## Запуск без Docker (локальная разработка)

> Для запуска без Docker отключите в `.env` переменные PostgreSQL
> (закомментируйте `DB_ENGINE`, `DB_HOST`, `DB_PORT`, `POSTGRES_*`) —
> тогда приложение автоматически вернётся к SQLite.

### Установка и запуск

1. **Клонировать репозиторий**

```bash
git clone <url-репозитория>
cd lms_system
```

2. **Создать виртуальное окружение**

   *Windows:*
   ```bash
   python -m venv venv
   ```

   *Mac / Linux:*
   ```bash
   python3 -m venv venv
   ```

3. **Активировать виртуальное окружение**

   *Windows:*
   ```bash
   venv\Scripts\activate
   ```

   *Mac / Linux:*
   ```bash
   source venv/bin/activate
   ```

4. **Установить зависимости**

```bash
pip install -r requirements.txt
```

5. **Применить миграции**

```bash
python manage.py migrate
```

6. **Создать суперпользователя**

```bash
python manage.py createsuperuser
```

7. **Запустить сервер**

```bash
python manage.py runserver
```

Сервер будет доступен по адресу `http://127.0.0.1:8000/`.

## Запуск Celery и celery-beat

Для работы фоновых и периодических задач нужен запущенный Redis
(настройки подключения задаются через переменную `REDIS_URL` в `.env`).

> В Docker Celery уже запущен и настраивается автоматически — этот раздел
> нужен только при запуске без Docker. Для локального запуска укажите
> в `.env` значение `REDIS_URL=redis://localhost:6379/0` и убедитесь, что
> Redis доступен на хосте (запустите `redis-server` или добавьте в
> `docker-compose.yml` для сервиса `redis` блок `ports: - "6379:6379"`).

1. **Запустить воркер** (обрабатывает отложенные задачи):

```bash
celery -A config worker -l info
```

2. **Запустить бит** (выполняет периодические задачи по расписанию):

```bash
celery -A config beat -l info
```

Периодическая задача `users.tasks.block_inactive_users` блокирует
пользователей, не заходивших более 30 дней, каждый день в 00:00 (Europe/Moscow).

При обновлении курса или урока подписчикам курса отправляется письмо,
но не чаще одного раза в 4 часа.

## API Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/users/` | Список пользователей |
| POST | `/api/users/` | Создать пользователя |
| GET | `/api/courses/` | Список курсов |
| POST | `/api/courses/` | Создать курс |
| GET | `/api/lessons/` | Список уроков |
| POST | `/api/lessons/` | Создать урок |

Полный список эндпоинтов доступен на главной странице (`/`).

## Пример запроса

Создание нового курса:

```bash
curl -X POST http://127.0.0.1:8000/api/courses/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Python-разработчик", "description": "Полный курс по Python"}'
```

Успешный ответ (HTTP 201):

```json
{
  "id": 1,
  "lessons": [],
  "name": "Python-разработчик",
  "preview": null,
  "description": "Полный курс по Python"
}
```

## Структура проекта

```
lms_system/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── materials/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── users/
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## Автор

Никита
