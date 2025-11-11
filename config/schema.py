import graphene
from graphene_django.debug import DjangoDebug
import inventory.schema as InventorySchema


class Query(
    # add more queries here
    InventorySchema.Query,
    graphene.ObjectType,
):
    debug = graphene.Field(DjangoDebug, name="_debug")


schema = graphene.Schema(query=Query)
