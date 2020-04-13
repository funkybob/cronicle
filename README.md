# Cronicle

A simple tool for testing [crontab](https://en.wikipedia.org/wiki/Cron) like syntax.

## Usage

    >>> from cronicle import Cron
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

