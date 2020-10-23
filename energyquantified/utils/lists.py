from energyquantified.data import Timeseries, Periodseries
from energyquantified.time import Frequency

from energyquantified.utils.pandas import timeseries_list_to_dataframe


class TimeseriesList(list):
    """
    A list of Timeseries objects. All time series must have the same
    frequency.

    :param iterable: Any iterable of time series
    :type iterable: iterable
    """

    def __init__(self, iterable=(), frequency=None):
        # Initialize list
        super().__init__(iterable)
        # Get frequency
        self._frequency = frequency
        # Asserts
        _validate_timeseries_list(self)
        _check_and_get_frequency_list(self, self._frequency)

    @property
    def frequency(self):
        return self._frequency

    def to_df(self):
        """
        Alias for :meth:`Timeseries.to_dataframe`.

        Convert this TimeseriesList to a ``pandas.DataFrame`` where all time
        series are placed in its own column and are lined up with the date-time
        as index.

        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return self.to_dataframe()

    def to_dataframe(self):
        """
        Convert this TimeseriesList to a ``pandas.DataFrame`` where all time
        series are placed in its own column and are lined up with the date-time
        as index.

        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return timeseries_list_to_dataframe(self)

    def append(self, timeseries):
        # Asserts
        _validate_timeseries(timeseries)
        self._frequency = _check_and_get_frequency(timeseries, self._frequency)
        # Perform operation
        return super().append(timeseries)

    def extend(self, iterable):
        # Asserts
        _validate_timeseries_list(iterable)
        self._frequency = _check_and_get_frequency_list(iterable, self._frequency)
         # Perform operation
        return super().extend(iterable)

    def insert(self, index, timeseries):
        # Asserts
        _validate_timeseries(timeseries)
        self._frequency = _check_and_get_frequency(timeseries, self._frequency)
         # Perform operation
        return super().insert(index, timeseries)

    def __add__(self, rhs):
        # Asserts
        _validate_timeseries_list(rhs)
        self._frequency = _check_and_get_frequency_list(rhs, self._frequency)
        # Perform operation
        return TimeseriesList(list.__add__(self, rhs), frequency=self._frequency)

    def __iadd__(self, rhs):
        # Asserts
        _validate_timeseries_list(rhs)
        self._frequency = _check_and_get_frequency_list(rhs, self._frequency)
        # Perform operation
        return TimeseriesList(list.__iadd__(self, rhs), frequency=self._frequency)

    def __setitem__(self, key, timeseries):
        # Asserts
        _validate_timeseries(timeseries)
        self._frequency = _check_and_get_frequency(timeseries, self._frequency)
        # Perform operation
        return super().__setitem__(timeseries)

    def __mul__(self, rhs):
        raise NotImplementedError("TimeseriesList does not support multiply")

    def __rmul__(self, rhs):
        raise NotImplementedError("TimeseriesList does not support multiply")

    def __imul__(self, rhs):
        raise NotImplementedError("TimeseriesList does not support multiply")

    def copy(self):
        return TimeseriesList(self, frequency=self._frequency)

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        if isinstance(result, list):
            return TimeseriesList(result, frequency=self._frequency)
        else:
            return result


class PeriodseriesList(list):
    """
    A list of Periodseries objects. Have methods for converting them to a
    :py:class:`TimeseriesList` or a `pandas.DataFrame`.

    :param iterable: Any iterable of `Periodseries`
    :type iterable: iterable
    """

    def __init__(self, iterable=()):
        _validate_periodseries_list(iterable)
        super().__init__(iterable)

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

    def to_df(self, frequency=None):
        """
        Alias for :meth:`Timeseries.to_dataframe`.

        Convert this PeriodseriesList to a ``pandas.DataFrame`` where all time
        series are placed in its own column and are lined up with the date-time
        as index.

        :param frequency: The frequency of the resulting time series'
        :type frequency: Frequency, required
        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return self.to_dataframe(frequency=frequency)

    def to_dataframe(self, frequency=None):
        """
        Convert this PeriodseriesList to a ``pandas.DataFrame`` where all time
        series are placed in its own column and are lined up with the date-time
        as index.

        :param frequency: The frequency of the resulting time series'
        :type frequency: Frequency, required
        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        # Verify parameters
        assert isinstance(frequency, Frequency), "Must be a frequency"
        # Convert to time series then to data frame
        timeseries_list = self.to_timeseries(frequency=frequency)
        return timeseries_list.to_dataframe()

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


# Helper functions


def _find_frequency(timeseries_list):
    if timeseries_list:
        return timeseries_list[0].resolution.frequency
    return None


def _check_and_get_frequency(timeseries, frequency=None):
    if frequency:
        assert timeseries.resolution.frequency == frequency, (
            f"Items in TimeseriesList must have frequency {frequency}, but "
            f"the Timeseries has {timeseries.resolution.frequency}."
        )


def _check_and_get_frequency_list(timeseries_list, frequency=None):
    if not frequency:
        frequency = _find_frequency(timeseries_list)
    if frequency:
        for index, timeseries in enumerate(timeseries_list):
            assert timeseries.resolution.frequency == frequency, (
                f"Element {index} does not match the frequency of "
                f"the other Timeseries objects."
            )


def _validate_timeseries(timeseries):
    assert isinstance(timeseries, Timeseries), (
        f"Element is not a Timeseries. Expects all "
        f"elements to be Timeseries objects."
    )


def _validate_timeseries_list(timeseries_list):
    for index, timeseries in enumerate(timeseries_list):
        assert isinstance(timeseries, Timeseries), (
            f"Element {index} is not a Timeseries. Expects all "
            f"elements to be Timeseries objects."
        )


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
