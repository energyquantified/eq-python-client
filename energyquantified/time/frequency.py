import enum

from dateutil.relativedelta import relativedelta

from .helpers import (
    shift,
    truncate_second, truncate_5min, truncate_10min,
    truncate_15min, truncate_30min, truncate_hour, truncate_date,
    truncate_week, truncate_month, truncate_quarter, truncate_year,
    truncate_season
)


# Lookup dict for frequencies by tag
_frequencies_lookup = {}


class Frequency(enum.Enum):
    """
    Enumerator of valid frequencies for Energy Quantified's API. The
    supported frequencies are:

     * ``P1Y`` – Yearly
     * ``SEASON`` – Summer or winter
     * ``P3M`` – Quarterly
     * ``P1M`` – Monthly
     * ``P1W`` – Weekly
     * ``P1D`` – Daily
     * ``PT1H`` – Hourly
     * ``PT30M`` – 30 minutes
     * ``PT15M`` – 15 minutes
     * ``PT10M`` – 10 minutes
     * ``PT5M`` – 5 minutes
     * ``NONE`` – Tick-data (no frequency)
    """

    # Fixed-interval frequencies
    P1Y    = (True, "years", 1, truncate_year, "Y")
    SEASON = (True, "months", 6, truncate_season, "S")
    P3M    = (True, "months", 3, truncate_quarter, "Q")
    P1M    = (True, "months", 1, truncate_month, "M")
    P1W    = (True, "weeks", 1, truncate_week, "W")
    P1D    = (True, "days", 1, truncate_date, "D")
    PT1H   = (True, "hours", 1, truncate_hour, "H")
    PT30M  = (True, "minutes", 30, truncate_30min, "30min")
    PT15M  = (True, "minutes", 15, truncate_15min, "15min")
    PT10M  = (True, "minutes", 10, truncate_10min, "10min")
    PT5M   = (True, "minutes", 5, truncate_5min, "5min")

    # No fixed interval (i.e. tick data)
    NONE  = (False, "microseconds", 1, lambda dt: dt, None)

    def __init__(self, is_iterable=None, field=None, steps=1,
                 truncate_func=None, pretty_name=None):
        self.is_iterable = is_iterable
        self.ordinal = len(self.__class__.__members__) + 1
        self.field = field
        self.steps = steps
        self.delta = relativedelta(**{ field: steps }) if is_iterable else None
        self.truncate_func = truncate_func
        self.pretty_name = pretty_name
        _frequencies_lookup[self.name.lower()] = self

    @classmethod
    def by_tag(cls, tag):
        """
        Look up frequencies by tag.

        :param tag: The tag to look up
        :type tag: str
        :return: A Frequency for this tag
        :rtype: Frequency
        """
        return _frequencies_lookup[tag.lower()]

    @classmethod
    def is_valid_tag(cls, tag):
        """
        Check whether a frequency tag exists or not.

        :param tag: The tag to look up
        :type tag: str
        :return: True if the frequency tag exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _frequencies_lookup

    def __lt__(self, b): return self.ordinal < b.ordinal
    def __gt__(self, b): return self.ordinal > b.ordinal
    def __le__(self, b): return self.ordinal <= b.ordinal
    def __ge__(self, b): return self.ordinal >= b.ordinal

    @property
    def tag(self):
        """
        The frequency tag (P1D, PT1H, etc.).
        """
        return self.name

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.name

    def matches(self, datetime_obj):
        """
        Check if a date-time aligns with this frequency.

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :return: True if it falls into this frequency, otherwise False
        :rtype: bool
        """
        return self.truncate_func(datetime_obj) == datetime_obj

    def truncate(self, datetime_obj):
        """
        Snap a date-time down to the nearest instant in this
        frequency.

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :return: A datetime snapped down to the nearest instant in this frequency
        :rtype: datetime
        """
        return self.truncate_func(datetime_obj)

    def get_delta(self, num_steps):
        """
        Create a relativedelta of N steps in this frequency. 0 steps
        means no change. 1 step means one tick forward, -1 step means one
        tick backwards.

        :param num_steps: Number of steps forward (positive) or backwards\
                          (negative)
        :type num_steps: int
        :return: A relativedelta (similar to timedelta)
        :rtype: relativedelta
        """
        # Requires an iterable frequency
        assert self.is_iterable, "%s is not iterable" % self
        return relativedelta(**{ self.field: self.steps * num_steps })

    def shift(self, datetime_obj, num_steps):
        """
        Shift a date-time by N steps in this frequency. 0 steps
        means no change. 1 step means one tick forward, -1 step means one
        tick backwards.

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :param num_steps: Number of steps forward (positive) or backwards\
                          (negative)
        :type num_steps: int
        :return: A shifted date-time
        :rtype: datetime
        """
        # Requires an iterable frequency
        assert self.is_iterable, "%s is not iterable" % self
        return shift(datetime_obj, **{ self.field: self.steps * num_steps })

    def between(self, datetime_obj1, datetime_obj2):
        """
        Count number of steps in this frequency between two dates.

        :param datetime_obj1: The first date-time
        :type datetime_obj1: datetime
        :param datetime_obj2: The second date-time
        :type datetime_obj2: datetime
        :return: The number of time this frequency fits between the two dates
        :rtype: int
        """
        # Requires an iterable frequency
        assert self.is_iterable, "%s is not iterable" % self
        # Check that they are in the frequency
        assert self.matches(datetime_obj1), "First date must match frequency"
        assert self.matches(datetime_obj2), "Second date must match frequency"
        d1, d2 = datetime_obj1, datetime_obj2
        # Same date
        if d1 == d2:
            return 0
        # Initiate counters and deltas
        delta = self.get_delta(1)
        d = d1
        i = 0
        # Forwards or backwards
        if d1 < d2:
            while d < d2:
                d = d + delta
                i = i + 1
        else:
            while d > d2:
                d = d - delta
                i = i - 1
        # The conclusion
        return i


# Additional lookups for

_frequencies_lookup["pt60m"] = Frequency.PT1H


# Constants

NONE   = Frequency.NONE

PT5M   = Frequency.PT5M
PT10M  = Frequency.PT10M
PT15M  = Frequency.PT15M
PT30M  = Frequency.PT30M
PT60M  = Frequency.PT1H
PT1H   = Frequency.PT1H
P1D    = Frequency.P1D
P1W    = Frequency.P1W
P1M    = Frequency.P1M
P3M    = Frequency.P3M
SEASON = Frequency.SEASON
P1Y    = Frequency.P1Y


# Lookup

LOOKUP = { str(f): f for f in list(Frequency) }
LOOKUP["PT60M"] = PT1H
