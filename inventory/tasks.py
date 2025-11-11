from celery import shared_task
from .models import Product, InventoryEntry, Order, AnalyticsEvent

def current_stock(product_id:int) -> int:
    return sum(InventoryEntry.objects.filter(product_id=product_id).values_list("delta", flat=True))

@shared_task(name="inventory.recalculate_inventory")
def recalc_inventory_async(product_id:int):
    total = current_stock(product_id)
    AnalyticsEvent.objects.create(order=None, kind="RECALC_PRODUCT", payload={"product_id": product_id, "stock": total})

@shared_task(name="inventory.post_order_analytics")
def post_order_analytics_async(order_id:int):
    order = Order.objects.get(id=order_id)
    AnalyticsEvent.objects.create(order=order, kind="ORDER_CREATED", payload={"total_cents": order.total_cents})
