import re

from collections import namedtuple
from datetime import datetime, tzinfo, timezone
from functools import partial
from typing import Tuple

FIELDS = ["minute", "hour", "dom", "month", "dow"]

slash_re = re.compile(r"^\*/(\d+)$")
list_re = re.compile(r"(\d+)(?:,(\d+))+$")

def match_splot(value):
    return True

def match_slash(value, *, divisor):
    return value % divisor == 0

def match_list(value, *, values):
    return value in values

def match_value(value, *, match):
    return value == match


GETTER = {
    'minute': lambda when: when.minute,
    'hour': lambda when: when.hour,
    'dom': lambda when: when.day,
    'month': lambda when: when.month,
    'dow': lambda when: when.weekday(),
}


class Cron:
    def __init__(self, pattern: str, timezone: tzinfo = timezone.utc):
        self.tz = timezone
        self.pattern = pattern

        frags = pattern.split(' ')
        if len(frags) != len(FIELDS):
            raise ValueError('Invalid pattern: wrong number of fields.')

        # A map of {field: match} functions per field
        self.tester = {
            field: self._get_tester(frag)
            for field, frag in zip(FIELDS, frags)
        }

    def _get_tester(self, frag: str):
        if frag == '*':
            return match_splot

        m = slash_re.search(frag)
        if m:
            return partial(match_slash, divisor=int(m.group(1)))

        m = list_re.search(frag)
        if m:
            return partial(match_list, values=[int(x) for x in frag.split(",")])

        try:
            val = int(frag)
        except ValueError:
            raise ValueError("Invalid pattern: %s is not a number" % (frag,))

        return partial(match_value, match=val)

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
        print({
            field: GETTER[field](when)
            for field in FIELDS
        })
        return tuple(
            self.tester[field](GETTER[field](when))
            for field in FIELDS
        )
