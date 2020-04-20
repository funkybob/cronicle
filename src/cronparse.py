import re

from collections import namedtuple
from datetime import datetime, tzinfo, timezone
from functools import partial
from typing import Tuple

Pattern = namedtuple("Pattern", ["minute", "hour", "dom", "month", "dow"])

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


def match_splot(value):
    return True


def match_slash(value, *, divisor):
    return value % divisor == 0


def match_range(value, *, start, end):
    return start <= value <= end


def match_value(value, *, match):
    return value == match


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


def parse_field(field):
    terms = field.split(",")

    matchers = [build_matcher(term) for term in terms]
    return matchers


class Cron:
    def __init__(self, pattern: str, timezone: tzinfo = timezone.utc):
        self.tz = timezone
        self.fragments = SHORTHAND_MAP.get(pattern, pattern).split(" ")
        try:
            self.pattern = Pattern(*self.fragments)
        except TypeError:
            raise ValueError("Invalid pattern: could not parse")
        self.matchers = Pattern(*[parse_field(field) for field in self.pattern])

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

    def match_minute(self, when):
        value = when.minute
        return any([matcher(value) for matcher in self.matchers.minute])

    def match_hour(self, when):
        value = when.hour
        return any([matcher(value) for matcher in self.matchers.hour])

    def match_dom(self, when):
        value = when.day
        return any([matcher(value) for matcher in self.matchers.dom])

    def match_month(self, when):
        value = when.month
        return any([matcher(value) for matcher in self.matchers.month])

    def match_dow(self, when):
        value = when.weekday()
        return any([matcher(value) for matcher in self.matchers.dow])
