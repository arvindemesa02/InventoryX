from django.test import TestCase
from inventory.models import Product, InventoryEntry, Customer, Order, OrderItem


class ModelTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name="Widget", sku="W-001", price_cents=500)

    def test_inventory_and_order_total(self):
        InventoryEntry.objects.create(product=self.product, delta=10, note="Initial")
        c = Customer.objects.create(email="c@example.com", full_name="C")
        order = Order.objects.create(customer=c)
        OrderItem.objects.create(
            order=order, product=self.product, quantity=2, unit_price_cents=self.product.price_cents
        )
        InventoryEntry.objects.create(product=self.product, delta=-2, note="Order")
        self.assertEqual(order.total_cents, 1000)
        stock = sum(e.delta for e in self.product.inventory_entries.all())
        self.assertEqual(stock, 8)
