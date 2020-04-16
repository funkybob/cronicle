import re

from collections import namedtuple
from datetime import datetime, tzinfo, timezone
from functools import partial
from typing import Tuple

Pattern = namedtuple("Patter", ["minute", "hour", "dom", "month", "dow"])

slash_re = re.compile(r"^\*/(\d+)$")
range_re = re.compile(r"(\d+)-(\d+)$")


SHORTHAND_MAP = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


class oneshot:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, cls=None):
        if instance is None:
            return self
        result = instance.__dict__[self.name] = self.func(instance)
        return result


def match_splot(value):
    return True


def match_slash(value, *, divisor):
    return value % divisor == 0


def match_range(value, *, start, end):
    return start <= value <= end


def match_value(value, *, match):
    return value == match


def parse_field(field):
    terms = field.split(",")

    matchers = [build_matcher(term) for term in terms]
    return matchers


def build_matcher(term):
    if term == "*":
        return match_splot

    m = slash_re.search(term)
    if m:
        return partial(match_slash, divisor=int(m.group(1)))

    m = range_re.search(term)
    if m:
        return partial(match_range, start=int(m.group(1)), end=int(m.group(2)))

    try:
        val = int(term)
    except ValueError:
        raise ValueError("Invalid pattern: %s is not a number" % (term,))

    return partial(match_value, match=val)


class Cron:
    def __init__(self, pattern: str, timezone: tzinfo = timezone.utc):
        self.tz = timezone
        self.fragments = SHORTHAND_MAP.get(pattern, pattern).split(" ")
        self.pattern = Pattern(*self.fragments)

        if len(self.fragments) != len(Pattern._fields):
            raise ValueError("Invalid pattern: wrong number of fields.")

    def matches(self, when: datetime) -> bool:
        """
        Tests if this pattern matches the given datetime.
        """
        return all(self.why(when))

    def why(self, when: datetime) -> Tuple[bool, bool, bool, bool, bool]:
        """
        Explains why a pattern matches a datetime.
        """
        _when = when.astimezone(self.tz)
        return (
            self.match_minute(_when),
            self.match_hour(_when),
            self.match_dom(_when),
            self.match_month(_when),
            self.match_dow(_when),
        )

    @oneshot
    def minute_matchers(self):
        return parse_field(self.pattern.minute)

    @oneshot
    def hour_matchers(self):
        return parse_field(self.pattern.hour)

    @oneshot
    def dom_matchers(self):
        return parse_field(self.pattern.dom)

    @oneshot
    def month_matchers(self):
        return parse_field(self.pattern.month)

    @oneshot
    def dow_matchers(self):
        return parse_field(self.pattern.dow)

    def match_minute(self, when):
        value = when.minute
        return any([matcher(value) for matcher in self.minute_matchers])

    def match_hour(self, when):
        value = when.hour
        return any([matcher(value) for matcher in self.hour_matchers])

    def match_dom(self, when):
        value = when.day
        return any([matcher(value) for matcher in self.dom_matchers])

    def match_month(self, when):
        value = when.month
        return any([matcher(value) for matcher in self.month_matchers])

    def match_dow(self, when):
        value = when.weekday()
        return any([matcher(value) for matcher in self.dow_matchers])
