# LMS System (Online Learning Platform)

Бэкенд для платформы онлайн-обучения. Предоставляет REST API для управления пользователями, курсами и уроками.

## Технологии

- Python 3.10+
- Django 6.0
- Django REST Framework
- SQLite

## Установка и запуск

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
