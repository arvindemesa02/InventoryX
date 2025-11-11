import graphene
from .schemas import queries


class Query(
    queries.Products,
    queries.Customers,
    queries.InventoryEntries,
    queries.Orders,
    queries.OrderItems,
    graphene.ObjectType,
):
    pass
