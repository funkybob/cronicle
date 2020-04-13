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
def test_matching(pattern, when, match):
    assert Cron(pattern).matches(when) == match
