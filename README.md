### Hexlet tests and linter status:
[![Actions Status](https://github.com/iRatatuii/python-project-52/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/iRatatuii/python-project-52/actions)


# Task Manager

Учебный проект на Django - менеджер задач

## Требования

- Python 3.10 или выше
- uv (менеджер пакетов)

## Установка

```bash
# Клонирование репозитория
git clone https://github.com/your-username/python-project-52.git
cd python-project-52

# Установка зависимостей с помощью uv
uv sync

# Активация виртуального окружения
source .venv/bin/activate  # для Linux/Mac
# .venv\Scripts\activate  # для Windows

# Применение миграций
python manage.py migrate

# Запуск сервера разработки
python manage.py runserver
```
## Использование

После запуска сервера перейдите по адресу http://127.0.0.1:8000/