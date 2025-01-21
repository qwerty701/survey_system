# Survey System

Survey System — это RESTful API для создания, управления и прохождения опросов. Проект разработан с использованием Django и Django REST Framework.

---

## Основные возможности

- Создание, редактирование и удаление опросов.
- Добавление вопросов к опросам.
- Прохождение опросов пользователями.
- Обусуждение опроса в чате
- Аутентификация, регистрация и авторизация пользователей.

---

## Технологии

- **Python 3.13**
- **Django 5.1**
- **Django REST Framework (DRF)**
- **SQLite** (так же поддерживается PostgreSQL)
- **Redis** (для уведомлений и чатов)

---

## Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/qwerty701/survey_system.git
cd survey_api
```

### 2. Создание виртуального пространства

```bash
python -m venv venv
source venv/bin/activate  # Для Linux/MacOS
venv\Scripts\activate    # Для Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных

Если у вас есть своя база данных посмотрите в инетернете
как её подключить

*4.1 Добавление данных в базу*

```bash
python manage.py migrate
```

### 5. Запуск сервера

*в cmd redis*
```bash
brew services start redis
```

*в терминале*

```bash
daphne survey_api.asgi:application
```
