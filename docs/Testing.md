# Unit Testing

This document describes how tests are organized in this project and how to extend them.

The test suite covers:
- Django model behaviour
- GraphQL queries
- GraphQL mutations

## Layout

All tests live under the inventory app:

```inventory/tests/
  test_models.py
  queries/
    test_product.py
    test_customer.py
    test_inventory_entry.py
    test_order.py
    test_order_item.py
  mutations/
    test_product.py
    test_customer.py
    test_inventory_entry.py
    test_order.py
    test_order_item.py
```

test_models.py:
- checks Order.total_cents
- checks inventory math via InventoryEntry.delta
- validates basic model behaviour

queries/:
- exercises GraphQL read paths (products, customers, orders, etc.)
- covers filters (where) and ordering (orderBy)
- tests nested relations like order.items

mutations/:
- exercises GraphQL write paths (productCreate, orderUpdate, orderDelete, etc.)
- validates payloads (ok, errors, result)
- asserts database side-effects.

## Running Tests

With Docker (recommended):

- Run all tests:
  make test
  or
  docker compose exec web python manage.py test

- Run a specific module:
  docker compose exec web python manage.py test inventory.tests.queries.test_product
  docker compose exec web python manage.py test inventory.tests.mutations.test_order

Without Docker (local virtualenv):

- Run all tests:
  python manage.py test

- Run a specific module:
  python manage.py test inventory.tests.test_models

## Model Tests

Use django.test.TestCase and the ORM.

Pattern (simplified):

- create Product, Customer, Order, OrderItem, InventoryEntry instances
- assert:
  - order.total_cents is the sum of item totals
  - inventory remaining stock is the sum of InventoryEntry.delta

When to add model tests:
- new computed fields (e.g., discounted_total)
- new business rules or signals
- anything that should hold at the model/ORM level regardless of GraphQL.

## GraphQL Tests

GraphQL tests subclass graphene_django.utils.testing.GraphQLTestCase.

Typical pattern:
1) Seed the DB in setUp using the ORM.
2) Call self.query(query_string, variables, operation_name).
3) Call self.assertResponseNoErrors(response).
4) Inspect response.json()["data"][...] and assert fields.
5) Optionally assert DB state with ORM queries.

### Query Tests

Keys:
- Use camelCase in GraphQL (priceCents, isActive, createdAt).
- Use where: <ModelWhereInput> for filters.
- Use orderBy: [<ModelOrderByInput!>] for ordering.

Example (conceptual):

- Query all active products, ordered by createdAt descending.
- Assert that priceCents and isActive match expectations.

### Mutation Tests

Keys:
- Assert payload.ok is True on success.
- Assert payload.errors is empty for successful paths.
- Assert payload.result fields are correct.
- Assert the database is in the expected state (e.g. Product.objects.filter(...).exists()).

Typical scenarios per entity:
- create (happy path + basic validation)
- update (change fields and assert result)
- delete (record is removed from DB)

## Adding Tests for a New Entity

If you add a new entity (e.g. Supplier) and expose it in GraphQL:

1) Model tests:
   - extend test_models.py or create a new module.
   - assert computed fields and business rules.

2) Query tests:
   - add inventory/tests/queries/test_supplier.py
   - add tests for:
     - simple list query
     - filtered query
     - ordered query
     - any important nested relations.

3) Mutation tests:
   - add inventory/tests/mutations/test_supplier.py
   - add tests for:
     - supplierCreate (success + basic validation error)
     - supplierUpdate
     - supplierDelete

## Notes on Celery / Async

If you later add behaviour that depends on Celery tasks:
- set CELERY_TASK_ALWAYS_EAGER = True in test settings, or
- mock the tasks.

This ensures asynchronous side-effects are executed synchronously in tests and are easy to assert.
