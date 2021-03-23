from collections import namedtuple
from datetime import datetime
import numbers
import sys

from ..time import Resolution, Frequency
from .base import Series
from .timeseries import TimeseriesList, Timeseries, Value


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

    def __init__(self, data=None, **kwargs):
        super().__init__(**kwargs)
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
        timeseries = Timeseries(
            curve=self.curve,
            resolution=resolution,
            instance=self.instance,
            data=data
        )
        timeseries.set_name(self._name)
        return timeseries

    def to_df(self, frequency=None, name=None, single_level_header=False):
        """
        Alias for :meth:`Periodseries.to_dataframe`.

        Convert this period-based to a ``pandas.DataFrame`` as a time series
        in the given frequency.

        Using :py:meth:`Periodseries.to_timeseries` to convert this
        period-based series to a regular time series first. When periods
        overlap the same step in the resulting time series, a weighted
        average is calculated down to second-precision.

        :param frequency: The frequency of the resulting ``pandas.DataFrame``\
            time series
        :type frequency: Frequency, required
        :param name: Set a name for the column in the ``pandas.DataFrame``,\
            defaults to ``value``
        :type name: str, optional
        :param single_level_header: Set to True to use single-level header \
            in the DataFrame, defaults to False
        :type single_level_header: boolean, optional
        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return self.to_dataframe(
            frequency=frequency,
            name=name,
            single_level_header=single_level_header
        )

    def to_dataframe(self, frequency=None, name=None,
                     single_level_header=False):
        """
        Convert this period-based to a ``pandas.DataFrame`` as a time series
        in the given frequency.

        Using :py:meth:`Periodseries.to_timeseries` to convert this
        period-based series to a regular time series first. When periods
        overlap the same step in the resulting time series, a weighted
        average is calculated down to second-precision.

        :param frequency: The frequency of the resulting ``pandas.DataFrame``\
            time series
        :type frequency: Frequency, required
        :param name: Set a name for the column in the ``pandas.DataFrame``,\
            defaults to ``value``
        :type name: str, optional
        :param single_level_header: Set to True to use single-level header \
            in the DataFrame, defaults to False
        :type single_level_header: boolean, optional
        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        # Verify parameters
        assert isinstance(frequency, Frequency), "Must be a frequency"
        # Conversion
        timeseries = self.to_timeseries(frequency=frequency)
        df = timeseries.to_dataframe(
            name=name,
            single_level_header=single_level_header
        )
        return df

    def print(self, file=sys.stdout):
        """
        Utility method to print a period-based series to any file handle
        (defaults to stdout).
        """
        print(f"Periodseries:", file=file)
        if self.curve:
            print(f"  Curve: {repr(self.curve)}", file=file)
        if self.instance:
            print(f"  Instance: {self.instance}", file=file)
        print(f"  Resolution: {self.resolution}", file=file)
        print(f"", file=file)
        for d in self.data:
            d.print(file=file)


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


# Period-based series list with helpers



class PeriodseriesList(list):
    """
    A list of Periodseries objects. Have methods for converting them to a
    :py:class:`TimeseriesList` or a `pandas.DataFrame`.

    :param iterable: Any iterable of `Periodseries`
    :type iterable: iterable
    """

    def __init__(self, iterable=()):
        # Initialize list
        super().__init__(iterable)
        # Asserts
        _validate_periodseries_list(iterable)

    def to_timeseries(self, frequency=None):
        """
        Convert all period-based series in this list to time series.

        When periods overlap the same step in the resulting time series,
        a weighted average is calculated down to second-precision.

        :param frequency: The frequency of the resulting time series
        :type frequency: Frequency, required
        :return: A list of time series
        :rtype: TimeseriesList
        """
        # Verify parameters
        assert isinstance(frequency, Frequency), "Must be a frequency"
        # Convert all period-based series to time series
        return TimeseriesList(
            periodseries.to_timeseries(frequency=frequency)
            for periodseries in self
        )

    def to_df(self, frequency=None, single_level_header=False):
        """
        Alias for :meth:`Timeseries.to_dataframe`.

        Convert this PeriodseriesList to a ``pandas.DataFrame`` where all time
        series are placed in its own column and are lined up with the date-time
        as index.

        :param frequency: The frequency of the resulting time series'
        :type frequency: Frequency, required
        :param single_level_header: Set to True to use single-level header \
            in the DataFrame, defaults to False
        :type single_level_header: boolean, optional
        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return self.to_dataframe(
            frequency=frequency,
            single_level_header=single_level_header
        )

    def to_dataframe(self, frequency=None, single_level_header=False):
        """
        Convert this PeriodseriesList to a ``pandas.DataFrame`` where all time
        series are placed in its own column and are lined up with the date-time
        as index.

        :param frequency: The frequency of the resulting time series'
        :type frequency: Frequency, required
        :param single_level_header: Set to True to use single-level header \
            in the DataFrame, defaults to False
        :type single_level_header: boolean, optional
        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        # Verify parameters
        assert isinstance(frequency, Frequency), "Must be a frequency"
        # Convert to time series then to data frame
        timeseries_list = self.to_timeseries(frequency=frequency)
        return timeseries_list.to_dataframe(
            single_level_header=single_level_header
        )

    def append(self, periodseries):
        _validate_periodseries(periodseries)
        return super().append(periodseries)

    def extend(self, iterable):
        # Asserts
        _validate_periodseries_list(iterable)
         # Perform operation
        return super().extend(iterable)

    def insert(self, index, periodseries):
        # Asserts
        _validate_periodseries(periodseries)
         # Perform operation
        return super().insert(index, periodseries)

    def __add__(self, rhs):
        _validate_periodseries_list(rhs)
        return PeriodseriesList(list.__add__(self, rhs))

    def __iadd__(self, rhs):
        _validate_periodseries_list(rhs)
        return PeriodseriesList(list.__iadd__(self, rhs))

    def __setitem__(self, key, periodseries):
        _validate_periodseries(periodseries)
        return super().__setitem__(periodseries)

    def __mul__(self, rhs):
        raise NotImplementedError("PeriodseriesList does not support multiply")

    def __rmul__(self, rhs):
        raise NotImplementedError("PeriodseriesList does not support multiply")

    def __imul__(self, rhs):
        raise NotImplementedError("PeriodseriesList does not support multiply")

    def copy(self):
        return PeriodseriesList(self)

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        if isinstance(result, list):
            return PeriodseriesList(result)
        else:
            return result


def _validate_periodseries(periodseries):
    assert isinstance(periodseries, Periodseries), (
        f"Element is not a Periodseries. Expects all "
        f"elements to be Periodseries objects."
    )


def _validate_periodseries_list(periodseries_list):
    for index, periodseries in enumerate(periodseries_list):
        assert isinstance(periodseries, Periodseries), (
            f"Element {index} is not a Periodseries. Expects all "
            f"elements to be Periodseries objects."
        )
