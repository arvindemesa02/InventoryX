import graphene

from .types import ProductNode, CustomerNode, InventoryEntryNode, OrderNode, OrderItemNode


class Products(graphene.ObjectType):
    product_create = ProductNode.CreateField()
    product_update = ProductNode.UpdateField()
    product_delete = ProductNode.DeleteField()


class Customers(graphene.ObjectType):
    customer_create = CustomerNode.CreateField()
    customer_update = CustomerNode.UpdateField()
    customer_delete = CustomerNode.DeleteField()


class InventoryEntries(graphene.ObjectType):
    inventory_entry_create = InventoryEntryNode.CreateField()
    inventory_entry_update = InventoryEntryNode.UpdateField()
    inventory_entry_delete = InventoryEntryNode.DeleteField()


class Orders(graphene.ObjectType):
    order_create = OrderNode.CreateField()
    order_update = OrderNode.UpdateField()
    order_delete = OrderNode.DeleteField()


class OrderItems(graphene.ObjectType):
    order_item_create = OrderItemNode.CreateField()
    order_item_update = OrderItemNode.UpdateField()
    order_item_delete = OrderItemNode.DeleteField()
