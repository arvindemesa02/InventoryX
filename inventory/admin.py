from django.contrib import admin
from .models import Product, InventoryEntry, Customer, Order, OrderItem, AnalyticsEvent
admin.site.register([Product, InventoryEntry, Customer, Order, OrderItem, AnalyticsEvent])
