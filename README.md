# README.md
**This project was designed and implemented end-to-end to demonstrate modern backend engineering skills, including system architecture, Django ORM modeling, GraphQL schema design, Celery task orchestration, containerized local development, and automated pipelines. I built the full API layer, database models, tests, Celery workers, and documentation, as well as all CI/CD and development tooling. All commits and contributions in this repository are my own work.**

A production-leaning Django + GraphQL API for inventory & order management.

## Contents
- [Quick Start](#quick-start)
- [Project Layout](#project-layout)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Docker Compose](#docker-compose)
- [Database & Migrations](#database--migrations)
- [Seeding Demo Data](#seeding-demo-data)
- [GraphQL](#graphql)
- [Unit Tests](#unit-tests)
- [Style, Lint & Hooks](#style-lint--hooks)
- [Celery Tasks](#celery-tasks)
- [Azure Pipelines](#azure-pipelines)

---

## Quick Start

```bash
# 1) Setup environment
cp .env.example .env

# 2) Bring everything up (Postgres, Redis, app, celery, beat)
docker compose up --build -d

# 3) Apply migrations & load sample data
make migrate
make seed

# 4) Open GraphiQL
open http://localhost:8000/graphql/

# 5) Run tests
make test
```

 Admin is at `http://localhost:8000/admin/` — create a superuser with:
```bash
docker compose exec web python manage.py createsuperuser
```
---

## Project Layout
```
.
├─ config/                  # Django settings, URLs, WSGI, Celery app
├─ inventory/               # App: models, GraphQL schema (queries & mutations), tasks
│  ├─ management/commands/  # seed_demo
│  └─ schemas/              # GraphQL types, queries, mutations
├─ tests/                   # Unit tests for models, queries, mutations
├─ templates/               # (reserved)
├─ pipelines/               # CI (Azure Pipelines)
├─ Dockerfile               # Gunicorn container image
├─ docker-compose.yml       # Web + DB + Redis + Celery + Beat
├─ Makefile                 # Handy shortcuts (migrate/test/lint/etc.)
├─ pyproject.toml           # black configuration
├─ requirements*.txt        # runtime/dev deps
└─ README.md                # this file
```

---

## Configuration
Settings come from environment variables (see `config/settings.py`). Copy `.env.example` to `.env` and adjust as needed.

**Common variables**
```
DJANGO_SECRET_KEY=dev-secret
DJANGO_DEBUG=1                    # 1=on (dev), 0=off (prod)
ALLOWED_HOSTS=*

POSTGRES_DB=inventorydb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0
CELERY_TASK_ALWAYS_EAGER=0        # 1 to run tasks synchronously (tests/local-only)
```

---

## Running Locally
Without Docker:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=config.settings
export DJANGO_DEBUG=1
# Set DB env vars (or use a local Postgres).
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
With Docker (recommended):
```bash
docker compose up --build -d
make migrate
```

---

## Docker Compose
Services:
- **web** — Django dev server at `:8000`
- **db** — Postgres 15
- **redis** — Redis 7 (Celery broker & backend)
- **celery** — Celery worker (`inventory.recalculate_inventory`, `inventory.post_order_analytics`)
- **beat** — Celery beat scheduler (for periodic tasks later)

Useful commands:
```bash
make up            # build & start
make down          # stop & remove volumes
make logs          # tail logs for all services
make shell         # Django shell inside the web container
```

---

## Database & Migrations
```bash
# Create new migrations after model changes
docker compose exec web python manage.py makemigrations
# Apply migrations
make migrate
```

Models live in `inventory/models.py`:
- `Product(name, sku, price_cents, is_active)`
- `InventoryEntry(product, delta, note)` (ordered descending by `created_at`)
- `Customer(email, full_name)`
- `Order(customer, status)` with `items` and `total_cents` property
- `OrderItem(order, product, quantity, unit_price_cents)` with `total_cents`
- `AnalyticsEvent(order?, kind, payload)` for audit/analytics trail

---

## Seeding Demo Data
```bash
make seed
# Creates 3 products with stock & one demo customer (c@example.com)
```
Seed command source: `inventory/management/commands/seed_demo.py`.

---

## GraphQL
GraphQL endpoint is **`/graphql/`** with GraphiQL enabled. The schema is defined in `inventory/schema.py` → `inventory/schemas/*`.

- **Queries**: `products(search?), product(id), orders_by_customer(customer_id)`
- **Mutations**: `createProduct`, `createOrder`, `cancelOrder`
- Types are in `inventory/schemas/types.py`.
- Field names are **camelCased** in GraphQL (e.g. `priceCents`), even if the Django model uses `price_cents`.

> See the separate **`docs/GraphQL.md`** for full examples of queries, variables, and curl/httpie snippets.

---

## Unit Tests
Tests use Django’s `TestCase` and Graphene-Django’s `GraphQLTestCase`.

- Run: `make test` (or `docker compose exec web python manage.py test`)
- Files: `inventory/tests/mutations/*`, `inventory/tests/queries/*`, `inventory/tests/test_models.py`

> See **`docs/Testing.md`** for test structure, fixtures, and extension tips.

---

## Style, Lint & Hooks
- **black** (configured in `pyproject.toml`): `make format`
- **flake8**: `make lint`
- **pre-commit** (optional):
  ```bash
  pip install -r requirements-dev.txt
  pre-commit install
  ```

---

## Celery Tasks
Celery is wired in `config/celery.py`. Redis is used as broker & result backend.

Tasks in `inventory/tasks.py`:
- `recalc_inventory_async(product_id)` — recomputes stock from `InventoryEntry` and records an `AnalyticsEvent`.
- `post_order_analytics_async(order_id)` — records an `AnalyticsEvent` with the order’s total.

Set `CELERY_TASK_ALWAYS_EAGER=1` in `.env` to execute tasks synchronously (useful in local dev or tests).

---

## Azure Pipelines
A sample pipeline is included at `pipelines/azure-pipelines.yml`. Customize to run `make test`, build/push images, and optionally apply migrations.
