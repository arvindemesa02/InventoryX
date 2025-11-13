# GraphQL API

This document describes how the GraphQL layer in this project is structured and how to work with it when adding features or tests.

The implementation is based on:
- Django
- graphene-django
- graphene-django-crud
- modules/graphene_custom helpers

## Endpoint

- URL: POST /graphql/
- View: CustomGraphQLView (supports GraphiQL and file uploads)
- Configured in config/urls.py

CustomGraphQLView extends FileUploadGraphQLView and:
- wraps the view with csrf_exempt
- customizes error formatting to add extensions.exception.type with the original Python exception class name.

## Schema Layout

Top-level schema is in config/schema.py:
- Query and Mutation are composed from inventory.schema
- Adds a _debug field (DjangoDebug) when DEBUG=True

Inventory schema (inventory/schema.py) composes:
- Query from: Products, Customers, InventoryEntries, Orders, OrderItems
- Mutation from: Products, Customers, InventoryEntries, Orders, OrderItems

Each group is implemented in inventory/schemas/queries.py and inventory/schemas/mutations.py.

## Node Types

Nodes live in inventory/schemas/types.py:
- ProductNode
- CustomerNode
- InventoryEntryNode
- OrderNode
- OrderItemNode

All extend:
- CustomDjangoCRUDObjectType
- CustomNode (GraphQL ids are raw PKs, not Relay-encoded)
- use TotalCountConnection for nested relations so connections expose totalCount.

Field naming in GraphQL uses camelCase:
- price_cents -> priceCents
- is_active -> isActive
- created_at -> createdAt
- unit_price_cents -> unitPriceCents

## Queries

Each entity exposes:
- a single-object field via ReadField (e.g. product, order)
- a list field via BatchReadField (e.g. products, orders)

List fields:
- accept where: <Model>WhereInput
- accept orderBy: [<Model>OrderByInput!]
- return a plain list (not a Relay connection)

Examples:
- products(where: ProductWhereInput, orderBy: [ProductOrderByInput!])
- orders(where: OrderWhereInput, orderBy: [OrderOrderByInput!])

Nested relations (e.g. order.items) use TotalCountConnection:
- items { totalCount, edges { node { ... } } }

## Timezone-aware Filtering

CustomDjangoCRUDObjectType implements logic to:
- look for createdAt filters in GraphQL variables
- read a timezone cookie (minutes offset from UTC)
- convert that to a timezone name and apply a TimeZoneConversion DB function

Any model with created_at can benefit from this when queried via GraphQL.

## Mutations

Each entity exposes three CRUD mutations via <Node>.CreateField / UpdateField / DeleteField.

For example (Products group):
- productCreate(input: ProductCreateInput!): ProductCreatePayload
- productUpdate(where: ProductWhereInput!, input: ProductUpdateInput!): ProductUpdatePayload
- productDelete(where: ProductWhereInput!): ProductDeletePayload

Payloads share the same shape:
- ok: Boolean!
- errors: [ErrorType!] (field, messages)
- result: NodeType (for create/update; delete omits result)

## Error Handling

CustomGraphQLView.format_error adds:
- extensions.exception.type with the original Python exception class name

This is useful for debugging and can be asserted in tests.

## Adding a New Entity

To expose a new model (e.g. Supplier):

1) Create model in inventory/models.py.
2) Create SupplierNode in inventory/schemas/types.py extending CustomDjangoCRUDObjectType and CustomNode.
3) Add Suppliers query group in inventory/schemas/queries.py:
   - supplier = SupplierNode.ReadField()
   - suppliers = SupplierNode.BatchReadField()
   and include it in inventory/schema.py Query.
4) Add Suppliers mutation group in inventory/schemas/mutations.py:
   - supplier_create / supplier_update / supplier_delete
   and include it in inventory/schema.py Mutation.
5) Add query and mutation tests under inventory/tests/queries and inventory/tests/mutations.
