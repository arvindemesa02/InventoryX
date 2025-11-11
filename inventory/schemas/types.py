from modules.graphene_custom.custom_django_crud import CustomDjangoCRUDObjectType
from modules.shared.utils import CustomNode, TotalCountConnection

from ..models import Product, Customer, InventoryEntry, Order, OrderItem


class ProductNode(CustomDjangoCRUDObjectType):
    class Meta:
        model = Product
        interfaces = (CustomNode,)
        connection_class = TotalCountConnection


class CustomerNode(CustomDjangoCRUDObjectType):
    class Meta:
        model = Customer
        interfaces = (CustomNode,)
        connection_class = TotalCountConnection


class InventoryEntryNode(CustomDjangoCRUDObjectType):
    class Meta:
        model = InventoryEntry
        interfaces = (CustomNode,)
        connection_class = TotalCountConnection


class OrderItemNode(CustomDjangoCRUDObjectType):
    class Meta:
        model = OrderItem
        interfaces = (CustomNode,)
        connection_class = TotalCountConnection


class OrderNode(CustomDjangoCRUDObjectType):
    class Meta:
        model = Order
        interfaces = (CustomNode,)
        connection_class = TotalCountConnection
