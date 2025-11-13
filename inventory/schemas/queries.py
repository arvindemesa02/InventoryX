import graphene

from .types import ProductNode, CustomerNode, InventoryEntryNode, OrderNode, OrderItemNode


class Products(graphene.ObjectType):
    product = ProductNode.ReadField()
    products = ProductNode.BatchReadField()


class Customers(graphene.ObjectType):
    customer = CustomerNode.ReadField()
    customers = CustomerNode.BatchReadField()


class InventoryEntries(graphene.ObjectType):
    inventory_entry = InventoryEntryNode.ReadField()
    inventory_entries = InventoryEntryNode.BatchReadField()


class Orders(graphene.ObjectType):
    order = OrderNode.ReadField()
    orders = OrderNode.BatchReadField()


class OrderItems(graphene.ObjectType):
    order_item = OrderItemNode.ReadField()
    order_items = OrderItemNode.BatchReadField()
