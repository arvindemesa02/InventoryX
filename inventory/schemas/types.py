import graphene
from graphene_django import DjangoObjectType
from ..models import Product, Customer, OrderItem, Order

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id","name","sku","price_cents","is_active")

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id","email","full_name")

class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        fields = ("id","product","quantity","unit_price_cents","total_cents")

class OrderType(DjangoObjectType):
    total_cents = graphene.Int()

    class Meta:
        model = Order
        fields = ("id","customer","status","items","total_cents")

    def resolve_total_cents(self, info):
        return self.total_cents
