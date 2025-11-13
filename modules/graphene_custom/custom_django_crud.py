from enum import Enum
import graphene
import pytz
from django.db.models import F
from django.db.models.functions import Extract
from graphene_django_crud.converter import convert_model_to_input_type
from graphene_django_crud.types import DjangoCRUDObjectType
from stringcase import snakecase
from collections import OrderedDict

from modules.shared.utils import TimeZoneConversion, convert_offset_to_timezone


class CustomDjangoCRUDObjectType(DjangoCRUDObjectType):
    """
    Class to add custom logic to the CRUD operations
    for all the models that inherit from this class

    Currently, it has the following logic:
        - get_queryset: to filter out the deleted records
        - batchread & BatchReadField: to add custom logic to the query for filtering and
            slicing to increase performance
        - mutate: to convert Enum values to their actual values
    """

    class Meta:
        abstract = True

    @classmethod
    def get_queryset(cls, parent, info, **kwargs):
        query = cls._meta.model.objects.all()

        # To filter out records by timezone from user
        # we'll add an extra column with the created_at field
        # converted in the timezone of the user
        if hasattr(cls._meta.model, "created_at"):
            timezone_from_cookie = convert_offset_to_timezone(
                int(info.context.COOKIES.get("timezone", 0))
            )
            query = query.annotate(
                created_at_in_timezone=TimeZoneConversion(timezone_from_cookie, F("created_at"))
            )

        return query

    @classmethod
    def filter(cls, parent, info, id, **kwargs):
        query = cls._meta.model.objects.filter(pk=id)

        # To filter out records by timezone from user
        # we'll add an extra column with the created_at field
        # converted in the timezone of the user
        if hasattr(cls._meta.model, "created_at"):
            timezone_from_cookie = convert_offset_to_timezone(
                int(info.context.COOKIES.get("timezone", 0))
            )
            query = query.annotate(
                created_at_in_timezone=TimeZoneConversion(timezone_from_cookie, F("created_at"))
            )

        return query

    @classmethod
    def _is_method_overridden(cls, method_name):
        """
        Check if the method with name `method_name` is overridden in the child class.
        """
        method = getattr(cls, method_name, None)
        if not method:
            return False
        return True

    @classmethod
    def filter_by_date_timezone(cls, queryset, date_variables, timezone):
        # Check if the user is trying to filter by month and year
        # if so, we'll use the created_at_in_timezone field to filter
        # and remove the createdAt field from the variable_values

        month = date_variables.get("month", {}).get("exact")
        year = date_variables.get("year", {}).get("exact")

        gte = date_variables.get("gte")
        lte = date_variables.get("lte")

        if month:
            queryset = queryset.annotate(
                created_at_in_timezone_month=Extract(
                    "created_at", "month", tzinfo=pytz.timezone(timezone)
                )
            ).filter(created_at_in_timezone_month=month)
        if year:
            queryset = queryset.annotate(
                created_at_in_timezone_year=Extract(
                    "created_at", "year", tzinfo=pytz.timezone(timezone)
                )
            ).filter(created_at_in_timezone_year=year)

        if gte:
            queryset = queryset.filter(created_at_in_timezone__gte=gte)
        if lte:
            queryset = queryset.filter(created_at_in_timezone__lte=lte)

        return queryset

    @classmethod
    def find_private_field(cls, name):
        """
        Method to find the private field in the model
        for a name
        """
        for field in cls._meta.model._meta.private_fields:
            if field.name == name:
                return field
        return None

    @classmethod
    def order_by_custom(cls, queryset, custom_order_by, variable_values):
        """
        method to order by a custom private field
        We first annotate the queryset with the custom field and the
        operation defined to get the field
        and then order by the custom field
        """
        for ob in custom_order_by:
            for key, value in ob.items():
                # convert the camelCase field from graphql to snake case in the model
                key_sk = snakecase(key) + "_custom"
                # get the attrs to annotate, the name and the operation defined
                computed = cls.find_private_field(snakecase(key)).compute(**variable_values)
                if isinstance(computed, dict):
                    kwargs = computed
                else:
                    kwargs = {key_sk: computed}
                queryset = queryset.annotate(**kwargs)
                # order by the new field
                if value == "ASC":
                    queryset = queryset.order_by(key_sk)
                elif value == "DESC":
                    queryset = queryset.order_by(f"-{key_sk}")
        return queryset

    @classmethod
    def batchread(cls, parent, info, related_field=None, **kwargs):
        for key, value in info.variable_values.items():
            if isinstance(value, Enum):
                info.variable_values[key] = value.value

        date_filters = info.variable_values.pop("createdAt", None)

        custom_order_by = []
        if "orderBy" in info.variable_values:
            model_private_fields = [field.name for field in cls._meta.model._meta.private_fields]
            # check if there is some private field within the order by operator
            if model_private_fields:
                for ob in info.variable_values["orderBy"]:
                    if snakecase(list(ob.keys())[0]) in model_private_fields:
                        custom_order_by.append(ob)

                # we modify the orderBy to only contains the fields that are not private
                info.variable_values["orderBy"] = [
                    ob for ob in info.variable_values["orderBy"] if ob not in custom_order_by
                ]

        query = super().batchread(parent, info, related_field, **kwargs)

        if date_filters:
            timezone_from_cookie = convert_offset_to_timezone(
                int(info.context.COOKIES.get("timezone", 0))
            )
            query = cls.filter_by_date_timezone(query, date_filters, timezone_from_cookie)

        if custom_order_by:
            query = cls.order_by_custom(query, custom_order_by, info.variable_values)

        return query

    @classmethod
    def mutate(cls, parent, info, instance, data, *args, **kwargs):
        try:
            for key, value in data.items():
                if isinstance(value, Enum):
                    data[key] = value.value
            return super().mutate(parent, info, instance, data, *args, **kwargs)
        except Exception as e:
            # Log the error for debugging purposes
            # structured_logger.log_error(
            #     f"Error in CustomDjangoCRUDObjectType.mutate: {str(e)}",
            #     **{"data": data, "instance": instance, "args": args, "kwargs": kwargs},
            # )
            raise e

    @classmethod
    def BatchReadField(cls, *args, **kwargs):
        arguments = {
            "where": graphene.Argument(
                convert_model_to_input_type(
                    cls._meta.model, input_flag="where", registry=cls._meta.registry
                )
            ),
            "order_by": graphene.List(
                convert_model_to_input_type(
                    cls._meta.model, input_flag="order_by", registry=cls._meta.registry
                )
            ),
            "page": graphene.Argument(graphene.Int, default_value=None),
        }

        if hasattr(cls, "CustomArguments"):
            arguments.update({"custom_args": graphene.Argument(cls.CustomArguments)})

        return graphene.Field(
            graphene.List(cls), args=arguments, resolver=cls.batchread, *args, **kwargs
        )

    @classmethod
    def ReadField(cls, *args, **kwargs):
        arguments = OrderedDict()
        arguments = {
            "where": graphene.Argument(
                convert_model_to_input_type(
                    cls._meta.model, input_flag="where", registry=cls._meta.registry
                )
            )
        }

        if hasattr(cls, "CustomArguments"):
            arguments.update({"custom_args": graphene.Argument(cls.CustomArguments)})
        return graphene.Field(cls, args=arguments, resolver=cls.read, *args, **kwargs)
