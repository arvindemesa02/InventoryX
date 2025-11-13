import graphene
from .schemas import queries, mutations


class Query(
    queries.Products,
    queries.Customers,
    queries.InventoryEntries,
    queries.Orders,
    queries.OrderItems,
    graphene.ObjectType,
):
    pass


class Mutation(
    mutations.Products,
    mutations.Customers,
    mutations.InventoryEntries,
    mutations.Orders,
    mutations.OrderItems,
    graphene.ObjectType,
):
    pass
