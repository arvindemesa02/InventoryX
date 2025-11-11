import graphene
from .schemas.queries import Query
from .schemas.mutations import Mutation

schema = graphene.Schema(query=Query, mutation=Mutation)
