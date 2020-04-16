# Cronparse

A simple tool for testing [crontab](https://en.wikipedia.org/wiki/Cron) like syntax.

## Usage

    >>> from cronparse import Cron
    >>> c = Cron('*/5 * * * 0')  # Matches only on Mondays, every 5th minute
    >>> from datetime import datetime
    >>> d = datetime(2020, 4, 13, 11, 5)
    >>> c.matches(d)
    True
    >>> d = d.replace(minute=6)
    >>> c.matches(d)
    False
    >>> d = d.replace(day=14, minute=5)
    >>> c.matches(d)
    False
    >>> c.why(d) # Ask which fragment of the rule did not match
    [True, True, True, True, False]

## crontab rule syntax

### Supported syntax:

1. \* - match any value
2. 1 - match exact value
3. \*/5 - match every 5th value
4. 1,3,4 - match values from list
5. 1-3 - match values in a range
6. 1-3,7,\*/2 - combinations!
7. @yearly, @annually, @monthly, @weekly, @daily, @midnight, @hourly

### Unsupported syntax:

- Day names
- Month names
- @reboot

## Timezone Support

Optionally, you can pass a `datetime.tzinfo` as the second argument. It
defaults to `datetime.timezone.utc`.

Any `datetime` passed for testing will first be moved to that timezone.
