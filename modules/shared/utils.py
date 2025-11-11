import graphene
from graphene import relay
from django.db.models import Func
import pytz
from datetime import timedelta, datetime


class TotalCountConnection(relay.Connection):
    total_count = graphene.Int()

    class Meta:
        abstract = True

    def resolve_total_count(self, info, *args, **kwargs):
        iterable = getattr(self, "iterable", None)
        if iterable is None:
            return 0
        try:
            return iterable.count()
        except Exception:
            return len(iterable)


class CustomNode(relay.Node):
    class Meta:
        name = "Node"

    @staticmethod
    def to_global_id(type, id):
        return id


class TimeZoneConversion(Func):
    function = "timezone"
    template = "%(function)s('%(timezone)s', %(expressions)s)"

    def __init__(self, timezone, expression, **extra):
        super().__init__(expression, timezone=timezone, **extra)


def convert_offset_to_timezone(offset_minutes):
    # Convert minutes to hours and minutes
    offset_hours = offset_minutes // 60
    offset_remainder_minutes = offset_minutes % 60

    # Create a timedelta object from the offset
    offset = timedelta(hours=offset_hours, minutes=offset_remainder_minutes)

    # Create a timezone object from the timedelta
    now = datetime.now(pytz.utc)  # current time
    tz_names = [
        tz.zone
        for tz in map(pytz.timezone, pytz.all_timezones)
        if now.astimezone(tz).utcoffset() == offset
    ]
    if tz_names:
        return tz_names[0]
    return "America/New_York"
