from collections import namedtuple
from datetime import datetime
import numbers
import sys

from ..time import Resolution, Frequency
from ..utils.pandas import timeseries_to_dataframe
from .base import Series
from .timeseries import Timeseries, Value


class Period(namedtuple("Period", ("begin", "end", "value"))):
    """
    A period for a period-based series.

    Implemented as a namedtuple of (begin, end, value).

    .. py:attribute:: begin

        The begin date-time

    .. py:attribute:: end

        The end date-time

    .. py:attribute:: value

        The numeric value
    """

    def validate(self):
        """
        Check if this period is in a valid format.

        :raises ValueError: When this period tuple is invalid
        """
        if not isinstance(self.begin, datetime):
            raise ValueError("Period.begin is not a datetime")
        if not isinstance(self.end, datetime):
            raise ValueError("Period.end is not a datetime")
        if not (self.value is None or isinstance(self.value, (numbers.Number))):
            raise ValueError("Period.value must either be a number or None")

    def print(self, file=sys.stdout):
        """
        Print this period-based series value.
        """
        d0 = self.begin.isoformat(sep=' ')
        d1 = self.end.isoformat(sep=' ')
        v = self.value
        print(f"{d0}–{d1}\t{v:13.2f}", file=file)

    def to_dict(self):
        """
        Convert this period value to a dict in the same short
        format as the API response.

        :return: A dict of this period in the same format as the API response
        :rtype: dict
        """
        return {
            "begin": self.begin.isoformat(sep=' '),
            "end": self.end.isoformat(sep=' '),
            "v": self.value
        }

    def __str__(self):
        d0 = self.begin.isoformat(sep=' ')
        d1 = self.end.isoformat(sep=' ')
        v = self.value
        return f"<Period: begin={d0}, end={d1}, value={v}>"

    def __repr__(self):
        return str(self)

    def is_active(self, date):
        return self.begin <= date < self.end

    def is_empty_or_invalid(self):
        return self.begin >= self.end

    def is_date_before(self, date):
        return date < self.begin

    def is_date_after(self, date):
        return date >= self.end

    def is_interval_before(self, begin, end):
        return end <= self.begin

    def is_interval_after(self, begin, end):
        return begin >= self.end

    def is_overlayed(self, begin, end):
        return end > self.begin and begin < self.end

    def is_covered(self, begin, end):
        return self.begin <= begin and self.end >= end

    def get_duration_seconds(self, begin, end):
        d0 = max(self.begin, begin)
        d1 = min(self.end, end)
        return (d1 - d0).total_seconds()


class CapacityPeriod(namedtuple("Period", ("begin", "end", "value", "installed"))):
    """
    A period for a period-based series. Includes the installed capacity for
    the period (which may differ from the currently available capacity given in
    the *value* attribute).

    Implemented as a namedtuple of (begin, end, value).

    .. py:attribute:: begin

        The begin date-time

    .. py:attribute:: end

        The end date-time

    .. py:attribute:: value

        The numeric value

    .. py:attribute:: installed

        The total installed capacity
    """

    def validate(self):
        """
        Check if this period is in a valid format.

        :raises ValueError: When this period tuple is invalid
        """
        if not isinstance(self.begin, datetime):
            raise ValueError("Period.begin is not a datetime")
        if not isinstance(self.end, datetime):
            raise ValueError("Period.end is not a datetime")
        if not (self.value is None or isinstance(self.value, (numbers.Number))):
            raise ValueError("Period.value must either be a number or None")
        if not (self.installed is None or isinstance(self.installed, (numbers.Number))):
            raise ValueError("Period.installed must either be a number or None")

    def print(self, file=sys.stdout):
        """
        Print this period-based series value.
        """
        d0 = self.begin.isoformat(sep=' ')
        d1 = self.end.isoformat(sep=' ')
        v = self.value
        c = self.installed
        print(f"{d0}–{d1}\t{v:13.2f}\t{c:13.2f}", file=file)

    def to_dict(self):
        """
        Convert this period value to a dict in the same short
        format as the API response.

        :return: A dict of this period in the same format as the API response
        :rtype: dict
        """
        return {
            "begin": self.begin.isoformat(sep=' '),
            "end": self.end.isoformat(sep=' '),
            "v": self.value,
            "c": self.installed,
        }

    def __str__(self):
        d0 = self.begin.isoformat(sep=' ')
        d1 = self.end.isoformat(sep=' ')
        v = self.value
        c = self.installed
        return f"<Period: begin={d0}, end={d1}, value={v}, installed={c}>"

    def __repr__(self):
        return str(self)

    def is_active(self, date):
        return self.begin <= date < self.end

    def is_empty_or_invalid(self):
        return self.begin >= self.end

    def is_date_before(self, date):
        return date < self.begin

    def is_date_after(self, date):
        return date >= self.end

    def is_interval_before(self, begin, end):
        return end <= self.begin

    def is_interval_after(self, begin, end):
        return begin >= self.end

    def is_overlayed(self, begin, end):
        return end > self.begin and begin < self.end

    def is_covered(self, begin, end):
        return self.begin <= begin and self.end >= end

    def get_duration_seconds(self, begin, end):
        d0 = max(self.begin, begin)
        d1 = min(self.end, end)
        return (d1 - d0).total_seconds()


class Periodseries(Series):
    """
    A period-based series with metadata.

    :param curve: The curve, defaults to None
    :type curve: Curve, optional
    :param resolution: The resolution of the time series, defaults to None
    :type resolution: Resolution, optional
    :param instance: The instance, defaults to None
    :type instance: Instance, optional
    :param data: A list of periods (Period or CapacityPeriod)
    :type data: list[]
    """

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert isinstance(self.resolution, Resolution), (
            "Periodseries.resolution is required"
        )
        self.data = data or []

    def __str__(self):
        items = []
        items.append(f"resolution={self.resolution}")
        items.append(f"curve=\"{self.curve}\"")
        if self.instance:
            items.append(f"instance={self.instance}")
        if self.has_data():
            items.append(f"begin=\"{self.begin().isoformat(sep=' ')}\"")
            items.append(f"end=\"{self.end().isoformat(sep=' ')}\"")
        else:
            items.append("EMPTY")
        return f"<Periodseries: {', '.join(items)}>"

    def __repr__(self):
        return str(self)

    def begin(self):
        if self.data:
            return self.data[0].begin
        else:
            raise ValueError("Periodseries has no values")

    def end(self):
        if self.data:
            return self.data[-1].end
        else:
            raise ValueError("Periodseries has no values")

    def to_timeseries(self, frequency=None):
        """
        Convert this period-based series to a regular time series.

        When periods overlap the same step in the resulting time series,
        a weighted average is calculated down to second-precision.

        :param frequency: The frequency of the resulting time series
        :type frequency: Frequency, required
        :return: A time series
        :rtype: Timeseries
        """
        # Verify parameters
        assert isinstance(frequency, Frequency), "Must be a frequency"
        # Prepare conversion
        resolution = Resolution(frequency, self.resolution.timezone)
        if not self.has_data():
            return Timeseries(
                curve=self.curve,
                resolution=resolution,
                instance=self.instance,
                data=[]
            )
        begin = resolution.floor(self.begin())
        end = self.end()
        iterator = _PeriodsToTimeseriesIterator(
            periods=self.data,
            resolution=resolution,
            begin=begin,
            end=end
        )
        # Convert
        data = [Value(dt, value) for dt, value in iterator]
        return Timeseries(
            curve=self.curve,
            resolution=resolution,
            instance=self.instance,
            data=data
        )


class _PeriodsToTimeseriesIterator:
    """
    A period-based series iterator used for conversions to Timeseries objects.
    """

    def __init__(self, periods=None, resolution=None, begin=None, end=None):
        self.periods = [p for p in periods if p.end > begin and p.begin < end]
        self.resolution = resolution
        self.begin = begin
        self.end = end
        # Iterator stuff
        self.d = None
        self.p = None

    def __iter__(self):
        # No periods available
        if not self.periods:
            return []
        # Get first period
        self.d = self.begin
        self.p = self.periods.pop(0)
        return self

    def __next__(self):
        # Get dates and current period
        p = self.p
        d0 = self.d
        d1 = self.d = self.resolution >> d0
        # We're done
        if d0 >= self.end:
            raise StopIteration
        else:
            return self._find_next_value(p, d0, d1)

    def _find_next_value(self, p, d0, d1):
        # No more periods
        if not p:
            return (d0, None)
        # Period covers the entire time interval
        if p.is_covered(d0, d1):
            return (d0, p.value)
        # We do not have any values for given date
        if p.is_interval_before(d0, d1):
            return (d0, None)
        # We are past current period
        if p.is_interval_after(d0, d1):
            p = self.p = self.periods.pop(0) if self.periods else None
            return self._find_next_value(p, d0, d1)
        # Overlapping, but not covering – find all periods covering interval
        overlapping = self._get_overlayed_periods(d0, d1)
        # Current period starts in the middle of the interval
        if not overlapping:
            return (d0, None)
        # More than one period – check if they are connected (no gaps)
        if self._is_covering_interval(p, overlapping, d0, d1):
            # No gaps – generate a mean value
            mean = self._calc_mean_periods([p] + overlapping, d0, d1)
            return (d0, mean)
        # There are gaps, so we do not have a value
        return (d0, None)

    def _get_overlayed_periods(self, begin, end):
        # Find other periods overlapping current interval
        periods = []
        for p in self.periods:
            if p.is_overlayed(begin, end):
                periods.append(p)
            else:
                break
        return periods

    def _is_covering_interval(self, current, periods, begin, end):
        # Check if the first period starts somewhere in the interval
        if current.begin > begin:
            return False
        # Check for gaps between periods
        previous = current
        for p in periods:
            if previous.end != p.begin:
                return False
            previous = p
        # Check if the last element stops somewhere in the interval
        if previous.end < end:
            return False
        # All covered
        return True

    def _calc_mean_periods(self, periods, begin, end):
        # Get value and duration in interval for each period
        available_weights = [
            (p.value, p.get_duration_seconds(begin, end))
            for p in periods
        ]
        # Get sum of weight
        sum_weights = 1.0 * sum(weight for avail, weight in available_weights)
        # Get the mean value
        return (
            sum(avail * weight for avail, weight in available_weights)
            / sum_weights
        )
