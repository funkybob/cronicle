from datetime import datetime, timezone

import pytest

from cronparse import Cron


@pytest.mark.parametrize(
    "pattern, when, match",
    [
        ("* * * * *", datetime.now(tz=timezone.utc), True),
        ("0 * * * *", datetime(2020, 4, 13, 11, 0, tzinfo=timezone.utc), True),
        ("0 * * * *", datetime(2020, 4, 13, 11, 1, tzinfo=timezone.utc), False),
        ("*/5 * * * *", datetime(2020, 4, 13, 11, 0, tzinfo=timezone.utc), True),
        ("*/5 * * * *", datetime(2020, 4, 13, 11, 1, tzinfo=timezone.utc), False),
        ("1,5,12 * * * *", datetime(2020, 4, 13, 11, 1, tzinfo=timezone.utc), True),
        ("1,5,12 * * * *", datetime(2020, 4, 13, 11, 5, tzinfo=timezone.utc), True),
        ("1,5,12 * * * *", datetime(2020, 4, 13, 11, 12, tzinfo=timezone.utc), True),
        ("1,5,12 * * * *", datetime(2020, 4, 13, 11, 13, tzinfo=timezone.utc), False),
        # '0 0 1 1 *',
        ("@yearly", datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc), True),
        ("@annually", datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc), True),
        # '0 0 1 * *'
        ("@monthly", datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc), True),
        # '0 0 * * 0'
        ("@weekly", datetime(2020, 1, 6, 0, 0, tzinfo=timezone.utc), True),
        # '0 0 * * *'
        ("@daily", datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc), True),
        ("@midnight", datetime(2020, 1, 1, 0, 0, tzinfo=timezone.utc), True),
        # '0 * * * *'
        ("@hourly", datetime(2020, 1, 1, 1, 0, tzinfo=timezone.utc), True),
    ],
)
def test_matches(pattern, when, match):
    assert Cron(pattern).matches(when) == match


@pytest.mark.parametrize(
    "pattern, match",
    [
        ("* * * * *", (True, True, True, True, True)),
        # Minute
        ("1 * * * *", (False, True, True, True, True)),
        ("*/4 * * * *", (False, True, True, True, True)),
        ("1,4,59 * * * *", (False, True, True, True, True)),
        ("1-14 * * * *", (False, True, True, True, True)),
        # Hour
        ("* 3 * * *", (True, False, True, True, True)),
        ("* */5 * * *", (True, False, True, True, True)),
        ("* 1,5,20 * * *", (True, False, True, True, True)),
        ("* 1-10 * * *", (True, False, True, True, True)),
        # DoM
        ("* * 12 * *", (True, True, False, True, True)),
        ("* * */4 * *", (True, True, False, True, True)),
        ("* * 1,12,24 * *", (True, True, False, True, True)),
        ("* * 1-12 * *", (True, True, False, True, True)),
        # Month
        ("* * * 2 *", (True, True, True, False, True)),
        ("* * * */3 *", (True, True, True, False, True)),
        ("* * * 1,3,11 *", (True, True, True, False, True)),
        ("* * * 5-11 *", (True, True, True, False, True)),
        # DoW
        ("* * * * 2", (True, True, True, True, False)),
        ("* * * * */2", (True, True, True, True, False)),
        ("* * * * 2,5", (True, True, True, True, False)),
        ("* * * * 2-5", (True, True, True, True, False)),
        # 0 == Monday
        ("* * * * 0", (True, True, True, True, False)),
    ],
)
def test_why(pattern, match):
    # 'Tue Apr 14 11:15:00 2020'
    when = datetime(2020, 4, 14, 11, 15, tzinfo=timezone.utc)

    assert Cron(pattern).why(when) == match



@pytest.mark.parametrize(
    "pattern, exc, msg",
    [
      # Non numbers
      ("A * * * *", ValueError, "Invalid pattern: A is not a number"),
      ("* A * * *", ValueError, "Invalid pattern: A is not a number"),
      ("* * A * *", ValueError, "Invalid pattern: A is not a number"),
      ("* * * A *", ValueError, "Invalid pattern: A is not a number"),
      ("* * * * A", ValueError, "Invalid pattern: A is not a number"),
      # Wrong field count
      ("* * ** *", ValueError, "Invalid pattern: could not parse"),
    ]
)
def test_invalid(pattern, exc, msg):
    with pytest.raises(exc, match=msg):
        Cron(pattern)

