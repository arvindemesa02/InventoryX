# GraphQL

## Endpoint
- `POST http://localhost:8000/graphql/`
- GraphiQL UI enabled at the same path for interactive exploration.

## Types (selected)
- `Product { id, name, sku, priceCents, isActive }`
- `Customer { id, email, fullName }`
- `OrderItem { id, product, quantity, unitPriceCents, totalCents }`
- `Order { id, customer, status, items, totalCents }`

> Graphene-Django auto-camelcases fields by default. For example, `price_cents` → `priceCents`.

## Queries

### 1) List products (with optional search)
```graphql
{
  products(search: "mouse") {
    id
    name
    sku
    priceCents
    isActive
  }
}
```

### 2) Get a single product by ID
```graphql
{
  product(id: 1) {
    id
    name
    sku
    priceCents
  }
}
```

### 3) Orders by customer
```graphql
{
  ordersByCustomer(customerId: 1) {
    id
    status
    totalCents
    items { quantity unitPriceCents totalCents product { sku } }
  }
}
```

## Mutations

### 1) Create product
```graphql
mutation {
  createProduct(name: "USB-C Cable", sku: "CB-050", priceCents: 300) {
    product { id name sku priceCents }
  }
}
```

### 2) Create order (with variables)
```graphql
mutation CreateOrder($cust: ID!, $items: [JSONString!]!) {
  createOrder(customerId: $cust, items: $items) {
    order { id totalCents }
  }
}
```
**Variables**
```json
{
  "cust": "1",
  "items": [
    { "product_id": 1, "quantity": 3 }
  ]
}
```

> On success: the order is created, inventory is decremented, and an analytics task is queued.

### 3) Cancel order
```graphql
mutation {
  cancelOrder(orderId: 123) { ok }
}
```
> This marks the order as `CANCELLED` and **restocks** each item quantity.

## Curl / HTTPie
```bash
# Products list
http POST :8000/graphql query='{ products { id name sku priceCents } }'

# Create order
http POST :8000/graphql   query='mutation CreateOrder($cust: ID!, $items: [JSONString!]!) {\n  createOrder(customerId: $cust, items: $items) { order { id totalCents } }\n}'   variables:='{"cust":"1","items":[{"product_id":1,"quantity":2}]}'
```

## Common Gotchas
- Remember camelCase in GraphQL (`totalCents`, not `total_cents`).
- For JSON inputs (e.g., `items`), you can pass either:
  - Literal JSON objects in GraphiQL variables, or
  - Strings that serialize to JSON when using certain clients.
- Ensure Celery is running so `post_order_analytics_async` is executed asynchronously (or set `CELERY_TASK_ALWAYS_EAGER=1`).
