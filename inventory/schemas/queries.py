import graphene
from ..models import Product, Order
from .types import ProductType, OrderType

class Query(graphene.ObjectType):
    products = graphene.List(ProductType, search=graphene.String())
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    orders_by_customer = graphene.List(OrderType, customer_id=graphene.ID(required=True))

    def resolve_products(self, info, search=None):
        qs = Product.objects.all().order_by("name")
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def resolve_product(self, info, id):
        return Product.objects.get(pk=id)

    def resolve_orders_by_customer(self, info, customer_id):
        return Order.objects.filter(customer_id=customer_id).order_by("-created_at")
