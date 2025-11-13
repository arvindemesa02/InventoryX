from functools import partial
from django.db.models.query import QuerySet
from graphene.relay.connection import connection_adapter, page_info_adapter
from graphene_django.utils import maybe_queryset
from graphql_relay.connection.array_connection import connection_from_array_slice
from graphene_django_crud.fields import DjangoConnectionField


class CustomDjangoConnectionField(DjangoConnectionField):
    """Calculates total length and preserves iterable on connection for totalCount."""

    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit=None):
        iterable = maybe_queryset(iterable)
        if isinstance(iterable, QuerySet):
            list_length = iterable.count()
        else:
            list_length = len(iterable)

        conn = connection_from_array_slice(
            iterable[:],
            args,
            slice_start=0,
            array_length=list_length,
            array_slice_length=list_length,
            connection_type=partial(connection_adapter, connection),
            edge_type=connection.Edge,
            page_info_type=page_info_adapter,
        )
        conn.iterable = iterable
        conn.length = list_length
        return conn


class CustomDjangoConnectionFieldWithOutPagination(DjangoConnectionField):
    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit=None):
        iterable = maybe_queryset(iterable)

        if isinstance(iterable, QuerySet):
            list_length = iterable.count()
        else:
            list_length = len(iterable)

        args["first"] = list_length

        connection = connection_from_array_slice(
            iterable[:],
            args,
            slice_start=0,
            array_length=list_length,
            array_slice_length=list_length,
            connection_type=partial(connection_adapter, connection),
            edge_type=connection.Edge,
            page_info_type=page_info_adapter,
        )
        connection.iterable = iterable
        connection.length = list_length
        return connection
