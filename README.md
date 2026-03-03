### Hexlet tests and linter status:
[![Actions Status](https://github.com/iRatatuii/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/iRatatuii/python-project-52/actions)


# Task Manager

Учебный проект на Django - менеджер задач

## Демо

Проект запущен на сервисе Render:
[https://python-project-52-5itj.onrender.com/](https://python-project-52-5itj.onrender.com/)

## Описание

Task Manager - это система управления задачами, которая позволяет:
- Создавать, редактировать и удалять задачи
- Назначать исполнителей и статусы задач
- Создавать метки для группировки задач
- Фильтровать задачи по различным критериям
- Управлять пользователями

## Технологии

- Python 3.10+
- Django 4.2+
- PostgreSQL (продакшен) / SQLite (разработка)
- Bootstrap 5
- Ruff (линтер)
- Pytest (тестирование)
- Gunicorn (WSGI сервер)
- Rollbar (отслеживание ошибок)

## Требования

- Python 3.10 или выше
- uv (менеджер пакетов)

## 🚀 Установка и запуск

```bash
# Клонирование репозитория
git clone https://github.com/your-username/python-project-52.git
cd python-project-52

# Установка зависимостей с помощью uv
make install

# Применение миграций
make migrate

# Запуск сервера разработки (порт 8000 по умолчанию)
make dev

# Для запуска на другом порту:
# make dev PORT=8080
```
После запуска сервера перейдите по адресу [http://127.0.0.1:8080/](http://127.0.0.1:8080/)


## Тестирование

# Запуск всех тестов
```bash
make test
```
# Запуск с подробным выводом
```bash
make test-verbose
```
# Проверка покрытия
```bash
make test-coverage
```

## Переменные окружения

- SECRET_KEY - секретный ключ Django

- DEBUG - режим отладки (True/False)

- ALLOWED_HOSTS - разрешенные хосты

- DATABASE_URL - URL базы данных (для PostgreSQL)

- ROLLBAR_ACCESS_TOKEN - токен Rollbar

