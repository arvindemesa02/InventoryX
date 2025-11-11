from django.core.management.base import BaseCommand
from inventory.models import Product, InventoryEntry, Customer

class Command(BaseCommand):
    help = "Seed demo products and a sample customer for InventoryX"

    def handle(self, *args, **options):
        products = [
            {"name": "Wireless Mouse", "sku": "WM-001", "price_cents": 800},
            {"name": "Mechanical Keyboard", "sku": "KB-101", "price_cents": 2500},
            {"name": "USB-C Cable", "sku": "CB-050", "price_cents": 300},
        ]
        for p in products:
            obj, created = Product.objects.get_or_create(sku=p["sku"], defaults=p)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created product {obj}"))
                InventoryEntry.objects.create(product=obj, delta=100, note="Initial stock")
            else:
                self.stdout.write(self.style.WARNING(f"Product exists: {obj}"))
        cust, _ = Customer.objects.get_or_create(email="c@example.com", defaults={"full_name":"Customer Demo"})
        self.stdout.write(self.style.SUCCESS(f"Customer ready: {cust.email}"))
        self.stdout.write(self.style.SUCCESS("Seeding complete."))
