import time
from datetime import date, datetime

from .timezone import DEFAULT_TZ, UTC


def now(tz=DEFAULT_TZ):
    """
    Get the current datetime.

    :param tz: The preferred time-zone, defaults to DEFAULT_TZ
    :type tz: TzInfo (or similar pytz time-zone)
    :return: A time-zone aware datetime set to now
    :rtype: datetime
    """
    return datetime.now(tz=tz)

def today(tz=DEFAULT_TZ):
    """
    Get a datetime set to midnight today.

    :param tz: The preferred time-zone, defaults to DEFAULT_TZ
    :type tz: TzInfo (or similar pytz time-zone)
    :return: A time-zone aware datetime set to midnight this morning
    :rtype: datetime
    """

    dt = now(tz=tz)
    dt = dt.replace(microsecond=0, second=0, minute=0, hour=0)
    return dt.tzinfo.normalize(dt)

def get_date(year=None, month=1, day=1):
    """
    Get a date. Only year needs to be specified. The remaining fields
    defaults to the lowest value.

    :param year: The year
    :type year: int, required
    :param month: The month (1-12), defaults to 1
    :type month: int, optional
    :param day: The day-of-month (1-31), defaults to 1
    :type day: int, optional
    :return: A date
    :rtype: date
    """
    assert year and 1900 <= year <= 2100, "Must specify year (1900-2100)"
    return date(year, month, day)

def get_datetime(year=None, month=1, day=1, hour=0, minute=0, second=0,
        millis=0, tz=DEFAULT_TZ):
    """
    Get a datetime. Only year needs to be specified. The remaining fields
    defaults to the lowest value. Timezone defaults to `DEFAULT_TZ`.

    :param year: The year
    :type year: int, required
    :param month: The month (1-12), defaults to 1
    :type month: int, optional
    :param day: The day-of-month (1-31), defaults to 1
    :type day: int, optional
    :param hour: The hour-of-day (0-23), defaults to 0
    :type hour: int, optional
    :param minute: The minute (0-59), defaults to 0
    :type minute: int, optional
    :param second: The second (0-59), defaults to 0
    :type second: int, optional
    :param millis: The milliseconds (0-999), defaults to 0
    :type millis: int, optional
    :param tz: The time-zone, defaults to DEFAULT_TZ
    :type tz: TzInfo (or similar pytz time-zone)
    :return: A time-zone aware datetime
    :rtype: datetime
    """

    assert year and 1900 <= year <= 2100, "Must specify year (1900-2100)"
    dt = datetime(year, month, day, hour, minute, second, millis * 1000)
    return tz.localize(dt)


def to_millis(datetime_obj):
    """
    Convert a datetime object to milliseconds since epoch.
    """
    assert is_tz_aware(datetime_obj), "Must be timezone-aware"
    # First convert to UTC
    utc_dt = datetime_obj.astimezone(UTC)
    # Get seconds since epoch and fraction of a second in millis
    seconds = int(time.mktime(utc_dt.timetuple()) * 1000)
    millis_fraction = utc_dt.microsecond // 1000
    # Tada!
    return seconds + millis_fraction


def from_millis(millis, tz=DEFAULT_TZ):
    """
    Convert milliseconds since epoch to a datetime in given timezone.

    Timezone defaults to `DEFAULT_TZ`.
    """
    dt = datetime.fromtimestamp(millis / 1000.0, UTC)
    return to_timezone(dt, tz=tz)


def to_timezone(datetime_obj, tz=DEFAULT_TZ):
    """
    Make a datetime object timezone-aware in given timezone. If it already
    has a timezone, convert the instant to provided timezone.
    """
    if is_tz_aware(datetime_obj):
        return datetime_obj.astimezone(tz)
    return tz.localize(datetime_obj)


def is_tz_aware(datetime_obj):
    """
    Check whether a datetime_obj is timezone-aware or not.
    """
    tz = datetime_obj.tzinfo
    return tz is not None and tz.utcoffset(datetime_obj) is not None


def is_tz_naive(datetime_obj):
    """
    Check whether a datetime_obj is timezone-naive.
    """
    return not is_tz_aware(datetime_obj)


def is_in_timezone(datetime_obj, tz):
    """
    Check whether datetime_obj is in given timezone.
    """
    return datetime_obj.tzinfo == tz
