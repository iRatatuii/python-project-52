install:
	uv sync

dev:
	uv run manage.py runserver

migrations:
	uv run manage.py makemigrations

migrate:
	uv run manage.py migrate

lint:
	uv run ruff check
	
lint-fix:
	uv run ruff check --fix

render-start:
	uv run gunicorn hexlet_code.wsgi

build:
	./build.sh

create-admin:
	python manage.py createsuperuser

collectstatic:
	uv run python manage.py collectstatic --noinput

test:
	uv run pytest --ds=hexlet_code.settings --reuse-db

test-verbose:
	uv run pytest --ds=hexlet_code.settings --reuse-db -v

test-coverage:
	uv run pytest --ds=hexlet_code.settings --reuse-db --cov=task_manager --cov-report=term --cov-report=html