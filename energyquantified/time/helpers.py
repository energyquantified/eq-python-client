from datetime import datetime, date, timedelta

from dateutil.relativedelta import relativedelta

from .utils import is_tz_aware


def shift(
    datetime_obj,
    years=0,
    months=0,
    weeks=0,
    days=0,
    hours=0,
    minutes=0,
    seconds=0,
    millis=0,
):
    """
    Shift a date by a certain amount of time, using a timedelta
    under the hood, while normalizing the tzinfo.
    """
    # Make the delta
    delta = relativedelta(
        years=years,
        months=months,
        weeks=weeks,
        days=days,
        hours=hours,
        minutes=minutes,
        seconds=seconds,
        microseconds=millis * 1000,
    )
    if years != 0 or months != 0 or weeks != 0 or days != 0:
        # Do arithmetic in without time-zone info, then localize when done
        tz, dt_naive = datetime_obj.tzinfo, datetime_obj.replace(tzinfo=None)
        dt_naive = dt_naive + delta
        return tz.localize(dt_naive)
    else:
        # Add delta and normalize datetime if tzinfo is attached
        if is_tz_aware(datetime_obj):
            return datetime_obj.tzinfo.normalize(datetime_obj + delta)
        return datetime_obj + delta


def replace(datetime_obj, **kwargs):
    """
    Replaces fields of a datetime while normalizing the tzinfo. All
    kwargs will be passed on to datetime.replace.
    """
    if is_tz_aware(datetime_obj):
        return datetime_obj.tzinfo.normalize(datetime_obj.replace(**kwargs))
    return datetime_obj.replace(**kwargs)


def truncate_second(datetime_obj):
    """
    Truncates and returns new a datetime to seconds.

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    d = datetime_obj.replace(microsecond=0)
    if is_tz_aware(datetime_obj):
        return datetime_obj.tzinfo.normalize(d)
    return d


def truncate_minute(datetime_obj):
    """
    Truncates and returns new a datetime to minutes.

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    d = datetime_obj.replace(microsecond=0, second=0)
    if is_tz_aware(datetime_obj):
        return datetime_obj.tzinfo.normalize(d)
    return d


def truncate_5min(datetime_obj):
    """
    Truncates and returns new a datetime to 5 minutes (:00, :05, :10, ...).

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    m = (datetime_obj.minute // 5) * 5
    d = datetime_obj.replace(microsecond=0, second=0, minute=m)
    if is_tz_aware(datetime_obj):
        return datetime_obj.tzinfo.normalize(d)
    return d


def truncate_10min(datetime_obj):
    """
    Truncates and returns new a datetime to 10 minutes (:00, :10, :20, ...).

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    m = (datetime_obj.minute // 10) * 10
    d = datetime_obj.replace(microsecond=0, second=0, minute=m)
    if is_tz_aware(datetime_obj):
        return datetime_obj.tzinfo.normalize(d)
    return d


def truncate_15min(datetime_obj):
    """
    Truncates and returns new a datetime to 15 minutes (:00, :15, :30, :45).

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    m = (datetime_obj.minute // 15) * 15
    d = datetime_obj.replace(microsecond=0, second=0, minute=m)
    if is_tz_aware(datetime_obj):
        return datetime_obj.tzinfo.normalize(d)
    return d


def truncate_30min(datetime_obj):
    """
    Truncates and returns new a datetime to 30 minutes (:00, :30).

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    m = (datetime_obj.minute // 30) * 30
    d = datetime_obj.replace(microsecond=0, second=0, minute=m)
    if is_tz_aware(datetime_obj):
        return datetime_obj.tzinfo.normalize(d)
    return d


def truncate_hour(datetime_obj):
    """
    Truncates and returns new a datetime to hours.

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    d = datetime_obj.replace(microsecond=0, second=0, minute=0)
    if is_tz_aware(datetime_obj):
        return datetime_obj.tzinfo.normalize(d)
    return d


def truncate_date(datetime_obj):
    """
    Truncates and returns new a datetime to date, or returns the date
    if it is a date.

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    if isinstance(datetime_obj, datetime):
        # Datetime
        d = datetime_obj.replace(microsecond=0, second=0, minute=0, hour=0)
        if is_tz_aware(datetime_obj):
            return datetime_obj.tzinfo.normalize(d)
        return d
    else:
        # Date
        return datetime_obj


def truncate_week(datetime_obj):
    """
    Truncates and returns new a datetime to date, or returns the date
    if it is a date.

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    days_from_monday = datetime_obj.isoweekday() - 1
    # Date
    if isinstance(datetime_obj, datetime):
        # Datetime
        d = datetime_obj.replace(microsecond=0, second=0, minute=0, hour=0)
        d = d - timedelta(days=days_from_monday)
        if is_tz_aware(datetime_obj):
            return datetime_obj.tzinfo.normalize(d)
        return d
    else:
        # Date
        return datetime_obj - timedelta(days=days_from_monday)


def truncate_month(datetime_obj):
    """
    Truncates and returns new a datetime to first of month, or returns the date
    if it is a date.

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    if isinstance(datetime_obj, datetime):
        # Datetime
        d = datetime_obj.replace(microsecond=0, second=0, minute=0, hour=0, day=1)
        if is_tz_aware(datetime_obj):
            return datetime_obj.tzinfo.normalize(d)
        return d
    else:
        # Date
        return datetime_obj.replace(day=1)


def truncate_quarter(datetime_obj):
    """
    Truncates and returns new a datetime to the first day of a quarter, or
    returns the date if it is a date.

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    month = datetime_obj.month
    new_month = month - ((month - 1) % 3)
    if isinstance(datetime_obj, datetime):
        # Datetime
        d = datetime_obj.replace(
            microsecond=0, second=0, minute=0, hour=0, day=1, month=new_month
        )
        if is_tz_aware(datetime_obj):
            return datetime_obj.tzinfo.normalize(d)
        return d
    else:
        # Date
        return datetime_obj.replace(day=1, month=new_month)


def truncate_season(datetime_obj):
    """
    Truncates and returns new a datetime to the first day of a season, or
    returns the date if it is a date.

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    month = datetime_obj.month
    year = datetime_obj.year
    new_month = month - ((month - 1) % 3)
    # Check the various months
    if new_month == 1:
        new_month = 10
        year = year - 1
    elif new_month == 10:
        pass
    else:
        new_month = 4
    # Handle date and datetime objects differently
    if isinstance(datetime_obj, datetime):
        # Datetime
        d = datetime_obj.replace(
            microsecond=0, second=0, minute=0, hour=0, day=1, month=new_month, year=year
        )
        if is_tz_aware(datetime_obj):
            return datetime_obj.tzinfo.normalize(d)
        return d
    else:
        # Date
        return datetime_obj.replace(day=1, month=new_month, year=year)


def truncate_year(datetime_obj):
    """
    Truncates and returns new a datetime for the first day of the year, or
    returns the date if it is a date.

    Keeps the timezone of the datetime. Works for timezone naive objects, too.
    """
    if isinstance(datetime_obj, datetime):
        # Datetime
        d = datetime_obj.replace(
            microsecond=0, second=0, minute=0, hour=0, day=1, month=1
        )
        if is_tz_aware(datetime_obj):
            return datetime_obj.tzinfo.normalize(d)
        return d
    else:
        # Date
        return datetime_obj.replace(day=1, month=1)
