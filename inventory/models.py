from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Product(TimeStampedModel):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=64, unique=True)
    price_cents = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.sku} - {self.name}"

class InventoryEntry(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="inventory_entries")
    delta = models.IntegerField(help_text="Positive or negative stock change")
    note = models.CharField(max_length=255, blank=True, default="")
    class Meta:
        ordering = ["-created_at"]

class Customer(TimeStampedModel):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)

class Order(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(max_length=20, default="PENDING", choices=[("PENDING","PENDING"),("PAID","PAID"),("CANCELLED","CANCELLED")])
    @property
    def total_cents(self):
        return sum(item.total_cents for item in self.items.all())

class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_cents = models.PositiveIntegerField()
    @property
    def total_cents(self):
        return self.quantity * self.unit_price_cents

class AnalyticsEvent(TimeStampedModel):
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.CASCADE, related_name="analytics_events")
    kind = models.CharField(max_length=50)
    payload = models.JSONField(default=dict)
