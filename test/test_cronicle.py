from datetime import datetime

import pytest

from cronicle import Cron


@pytest.mark.parametrize('pattern, when, match', [
    ('* * * * *', datetime.now(), True),
    ('0 * * * *', datetime(2020, 4, 13, 11, 0), True),
    ('0 * * * *', datetime(2020, 4, 13, 11, 1), False),
    ('*/5 * * * *', datetime(2020, 4, 13, 11, 0), True),
    ('*/5 * * * *', datetime(2020, 4, 13, 11, 1), False),
    ('1,5,12 * * * *', datetime(2020, 4, 13, 11, 1), True),
    ('1,5,12 * * * *', datetime(2020, 4, 13, 11, 5), True),
    ('1,5,12 * * * *', datetime(2020, 4, 13, 11, 12), True),
    ('1,5,12 * * * *', datetime(2020, 4, 13, 11, 13), False),
])
def test_matches(pattern, when, match):
    assert Cron(pattern).matches(when) == match


@pytest.mark.parametrize('pattern, match', [
    ('* * * * *', (True, True, True, True, True)),
    ('1 * * * *', (False, True, True, True, True)),
    ('*/4 * * * *', (False, True, True, True, True)),
    ('1,4,59 * * * *', (False, True, True, True, True)),
    # ('1-14 * * * *', (False, True, True, True, True)),

    ('* 3 * * *', (True, False, True, True, True)),
    ('* */5 * * *', (True, False, True, True, True)),
    ('* 1,5,20 * * *', (True, False, True, True, True)),
    # ('* 1-10 * * *', (True, False, True, True, True)),

    ('* * 12 * *', (True, True, False, True, True)),
    ('* * */4 * *', (True, True, False, True, True)),
    ('* * 1,12,24 * *', (True, True, False, True, True)),
    # ('* * 1-12 * *', (True, True, False, True, True)),

    ('* * * 2 *', (True, True, True, False, True)),
    ('* * * */3 *', (True, True, True, False, True)),
    ('* * * 1,3,11 *', (True, True, True, False, True)),
    # ('* * * * *', (True, True, True, False, True)),

    ('* * * * 2', (True, True, True, True, False)),
    ('* * * * */2', (True, True, True, True, False)),
    ('* * * * 2,5', (True, True, True, True, False)),
    # ('* * * * 2-5', (True, True, True, True, False)),
])
def test_why(pattern, match):
    when = datetime(2020, 4, 14, 11, 15)

    assert Cron(pattern).why(when) == match

