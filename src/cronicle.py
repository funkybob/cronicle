import re

from collections import namedtuple
from datetime import datetime, tzinfo, timezone
from typing import Tuple

Pattern = namedtuple("Pattern", "minute hour dom month dow")

slash_re = re.compile(r"^\*/(\d+)$")


class Cron:
    def __init__(self, pattern: str, timezone: tzinfo = timezone.utc):
        self.tz = timezone
        self.pattern = Pattern(*pattern.split(" "))

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

    def _match(self, frag: str, value: int):
        """
        Helper to match pattern fragment with date value
        """
        if frag == "*":
            return True

        m = slash_re.search(frag)
        if m:
            return value % int(m.group(1)) == 0

        try:
            val = int(frag)
        except ValueError:
            raise ValueError("Invalid pattern: %s" % (self.pattern,))

        return val == value

    def match_minute(self, when: datetime) -> bool:
        return self._match(self.pattern.minute, when.minute)

    def match_hour(self, when: datetime) -> bool:
        return self._match(self.pattern.hour, when.hour)

    def match_dom(self, when: datetime) -> bool:
        return self._match(self.pattern.dom, when.day)

    def match_month(self, when: datetime) -> bool:
        return self._match(self.pattern.month, when.month)

    def match_dow(self, when: datetime) -> bool:
        return self._match(self.pattern.dow, when.weekday())
