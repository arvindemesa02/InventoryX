# Unit Testing

## Overview
Tests live under `/tests` and cover:
- **Models** (totals, inventory math)
- **GraphQL queries** (list & filter)
- **GraphQL mutations** (create order flow)

## Running
```bash
make test
# or
docker compose exec web python manage.py test -v 2
```

## What’s Included
- `tests/test_models.py` — creates products, inventory entries, a customer, an order and asserts `total_cents` & remaining stock.
- `tests/test_queries.py` — uses `GraphQLTestCase` to call the `/graphql` endpoint and validate the `products` result.
- `tests/test_mutations.py` — issues a `createOrder` mutation with variables and asserts the computed `totalCents`.

## Patterns to Follow
- Prefer **factory helpers** (Django fixtures or factories) as your test suite grows.
- Use `CELERY_TASK_ALWAYS_EAGER=1` to make async tasks run inline during tests when validating side-effects.
- Keep GraphQL strings small & focused; use variables for dynamic values.

## Extending
- Add coverage for:
  - Pagination or filtering for `products`.
  - `cancelOrder` path (inventory restock, idempotency on repeated cancels).
  - Error states: out-of-stock, invalid SKUs, etc.
