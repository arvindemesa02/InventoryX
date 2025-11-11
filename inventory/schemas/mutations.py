import graphene
from django.db import transaction
from ..models import Product, InventoryEntry, Order, OrderItem
from .types import ProductType, OrderType
from ..tasks import recalc_inventory_async, post_order_analytics_async

class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        sku = graphene.String(required=True)
        price_cents = graphene.Int(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, sku, price_cents):
        product = Product.objects.create(name=name, sku=sku, price_cents=price_cents)
        recalc_inventory_async.delay(product.id)
        return CreateProduct(product=product)

class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        items = graphene.List(graphene.NonNull(graphene.JSONString), required=True)

    order = graphene.Field(OrderType)

    @transaction.atomic
    def mutate(self, info, customer_id, items):
        order = Order.objects.create(customer_id=customer_id)
        for item in items:
            pid = int(item["product_id"])
            qty = int(item.get("quantity", 1))
            product = Product.objects.get(id=pid)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                unit_price_cents=product.price_cents,
            )
            InventoryEntry.objects.create(product=product, delta=-qty, note=f"Order #{order.id}")
        post_order_analytics_async.delay(order.id)
        return CreateOrder(order=order)

class CancelOrder(graphene.Mutation):
    class Arguments:
        order_id = graphene.ID(required=True)

    ok = graphene.Boolean()

    @transaction.atomic
    def mutate(self, info, order_id):
        order = Order.objects.get(id=order_id)
        if order.status == "CANCELLED":
            return CancelOrder(ok=True)
        order.status = "CANCELLED"
        order.save()
        for item in order.items.all():
            InventoryEntry.objects.create(product=item.product, delta=item.quantity, note=f"Cancel order #{order.id}")
        return CancelOrder(ok=True)

class Mutation(graphene.ObjectType):
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    cancel_order = CancelOrder.Field()
