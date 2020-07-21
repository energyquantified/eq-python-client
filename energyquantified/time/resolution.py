from datetime import datetime

from .frequency import Frequency
from .utils import to_timezone


class Resolution:
    """
    A combination of a frequency and a time zone with utility methods
    for iteration and snapping datetimes to given frequency.

    :param frequency: The frequency for this resolution
    :type frequency: Frequency
    :param timezone: The time-zone for this resolution
    :type timezone: TzInfo (or similar pytz time-zone)
    """

    def __init__(self, frequency, timezone):
        assert isinstance(frequency, Frequency), "Invalid frequency"
        assert timezone, "Invalid or missing timezone"
        self.frequency = frequency
        self.timezone = timezone

    def __str__(self):
        return (
            "<Resolution: "
            f"frequency={self.frequency.tag}, timezone={self.timezone}"
            ">"
        )

    def __repr__(self):
        return str(self)

    def is_iterable(self):
        """
        Check whether or not this Resolution is iterable

        :return: True if this Resolution is iterable, otherwise False
        :rtype: bool
        """
        return self.frequency.is_iterable

    def to_dict(self):
        """
        Convert this resolution to a dict in the same format as data is
        returned from the Energy Quantified Time Series API.

        :return: A dict of this resolution in the same format as the API response
        :rtype: dict
        """
        return {
            "frequency": self.frequency.tag,
            "timezone": str(self.timezone),
        }

    def now(self):
        """
        Create a datetime, snapped to beginning of the current period of
        this resolution's frequency.

        :return: A date-time of now, snapped to beginning of the resolution's\
                 frequency
        :rtype: datetime
        """
        dt_with_tz = datetime.now(tz=self.timezone)
        return self.floor(dt_with_tz)

    def datetime(self, year=None, month=1, day=1, hour=0, minute=0, second=0,
                 millis=0):
        """
        Create a datetime. Only year needs to be specified. The remaining
        fields defaults to the lowest value. The datetime will have the same
        timezone as this resolution and will be snapped to the frequency.

        :param year: The year
        :type year: int, required
        :param month: The month (1-12), defaults to 1
        :type month: int, optional
        :param day: The day-of-month (1-31), defaults to 1
        :type day: int, optional
        :param hour: The hour of the day (0-23), defaults to 0
        :type hour: int, optional
        :param minute: The minute (0-59), defaults to 0
        :type minute: int, optional
        :param second: The second (0-59), defaults to 0
        :type second: int, optional
        :param millis: The millisecond (0-999), defaults to 0
        :type millis: int, optional
        :return: A new date-time, snapped down to the frequency
        :rtype: datetime
        """
        assert year and 1900 <= year <= 2100, "Must specify year (1900-2100)"
        dt = datetime(year, month, day, hour, minute, second, millis * 1000)
        dt_with_tz = self.timezone.localize(dt)
        return self.floor(dt_with_tz)

    def matches(self, datetime_obj):
        """
        Check if a datetime obj has the same time zone as this resolution
        and that the datetime aligns with the frequency of this resolution.

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :return: True if it falls into this frequency, otherwise False
        :rtype: bool
        """
        if self.frequency <= Frequency.P1D:
            return self.frequency.matches(datetime_obj)
        else:
            return (
                datetime_obj.tzinfo.zone == self.timezone.zone
                and self.frequency.matches(datetime_obj)
            )

    def __rshift__(self, datetime_obj):
        """
        Move a datetime one step forward in time. Usage:

           >>> datetime_obj = resolution >> datetime_obj

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :return: The supplied date-time shifted one step forward in time
        :rtype: datetime
        """
        assert self.is_iterable(), (
            "Operator >> requires an iterable Resolution"
        )
        # self >> datetime_obj to move one step forward
        return self.shift(datetime_obj, 1)

    def __lshift__(self, datetime_obj):
        """
        Move a datetime one step backward in time. Usage:

           >>> datetime_obj = resolution << datetime_obj

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :return: The supplied date-time shifted one step backward in time
        :rtype: datetime
        """
        assert self.is_iterable(), (
            "Operator << requires an iterable Resolution"
        )
        # self << datetime_obj to move one step backward
        return self.shift(datetime_obj, -1)

    def shift(self, datetime_obj, steps):
        """
        Shift a date-time by N steps in this resolution's frequency. 0 steps
        means no change. 1 step means one tick forward, -1 step means one
        tick backwards.

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :param steps: Number of steps forward (positive) or backwards (negative)
        :type steps: int
        :return: A shifted date-time
        :rtype: datetime
        """
        assert self.is_iterable(), (
            "Resolution.shift() requires an iterable Resolution"
        )
        self._assert_valid(datetime_obj)
        return self.frequency.shift(datetime_obj, steps)

    def floor(self, datetime_obj):
        """
        Snap a date or datetime down to the nearest instant in this
        resolution's frequency.

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :return: A date-time snapped down to the nearest instant in this\
                 resolution's frequency.
        :rtype: datetime
        """
        # Make sure it is in the correct time zone and truncate
        dt = to_timezone(datetime_obj, tz=self.timezone)
        return self.frequency.truncate(dt)

    def ceil(self, datetime_obj):
        """
        Snap a date or datetime up to the nearest instant in this
        resolution's frequency.

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :return: A date-time snapped up to the nearest instant in this\
                 resolution's frequency.
        :rtype: datetime
        """
        # Floor
        truncated = self.floor(datetime_obj)
        # Shift one step if not already in resolution
        return self >> truncated if truncated != datetime_obj else truncated

    def enumerate(self, begin=None, end=None):
        """
        Returns a generator over all datetimes between `begin` and `end` in
        this resolution. Example:

        >>> resolution = Resolution(Frequency.P1D, CET)
        >>> begin = resolution.datetime(2020, 5, 16)
        >>> end = resolution.datetime(2020, 5, 26)
        >>> for i in resolution.enumerate(begin, end):
                print(i)

        :param begin: The begin date-time (inclusive)
        :type begin: datetime, required
        :param end: The end date-time (exclusive)
        :type end: datetime, required
        :yield: A generator of date-times between `begin` and `end` in\
                this resolution
        :rtype: datetime
        """
        assert self.is_iterable(), (
            "Resolution.enumerate() requires an iterable Resolution"
        )
        assert begin, "begin is not set"
        assert end, "end is not set"
        self._assert_valid(begin)
        d = begin
        while d < end:
            yield d
            d = self >> d

    def _assert_valid(self, datetime_obj):
        assert self.matches(datetime_obj), (
            "datetime_obj %s does not match %s" % (datetime_obj, self)
        )
