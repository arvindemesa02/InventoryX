.PHONY: up down logs migrate seed test lint format shell

up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

migrate:
	docker compose exec web python manage.py migrate

seed:
	docker compose exec web python manage.py seed_demo

test:
	docker compose exec web python manage.py test

lint:
	pip install -r requirements-dev.txt && flake8

format:
	pip install -r requirements-dev.txt && black .

shell:
	docker compose exec web python manage.py shell
