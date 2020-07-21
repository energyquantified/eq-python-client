from collections import namedtuple
from datetime import datetime
import enum
import numbers
import sys


from ..time import Resolution
from ..utils.pandas import timeseries_to_dataframe
from .base import Series


class ValueType(enum.Enum):
    """
    Enumerator of supported value types for ``timeseries.data[]``.
    """
    #: Single value. See :py:class:`energyquantified.data.Value`.
    VALUE = "VALUE"
    #: Only scenarios. See :py:class:`energyquantified.data.ScenariosValue`.
    SCENARIOS = "SCENARIOS"
    #: A value and scenarios. See
    #: :py:class:`energyquantified.data.MeanScenariosValue`.
    MEAN_AND_SCENARIOS = "MEAN_AND_SCENARIOS"


class Value(namedtuple("Value", ("date", "value"))):
    """
    A time series value.

    Implemented as a namedtuple of (date, value).

    .. py:attribute:: date

        The date-time for a time series value (index)

    .. py:attribute:: value

        The numeric value
    """

    def value_type(self):
        """
        Get the value type for this tuple.

        :return: The value type for this tuple
        :rtype: ValueType
        """
        return ValueType.VALUE

    def validate(self):
        """
        Check if this time series value is in a valid format.

        :raises ValueError: When this value tuple is invalid
        """
        if not isinstance(self.date, datetime):
            raise ValueError("Value.date is not a datetime")
        if not (self.value is None or isinstance(self.value, (numbers.Number))):
            raise ValueError("Value.value must either be a number or None")

    def num_scenarios(self):
        """
        Count number of scenarios in this data point.

        :return: Always 0, as Value-types has no scenarios
        :rtype: int
        """
        return 0

    def has_scenarios(self):
        """
        Check whether or not this data point has `support` for scenarios.

        :return: Always False, as Value-types has no scenarios
        :rtype: bool
        """
        return False

    def print(self, file=sys.stdout):
        """
        Print this time series value.
        """
        dt = self.date.isoformat(sep=' ')
        v = self.value
        print(f"{dt}\t{v:13.2f}", file=file)

    def to_dict(self):
        """
        Convert a time series value to a dict in the same short
        format as the API response.

        :return: A dict of this value in the same format as the API response
        :rtype: dict
        """
        return {
            "d": self.date.isoformat(sep=' '),
            "v": self.value
        }

    def __str__(self):
        dt = self.date.isoformat(sep=' ')
        v = self.value
        return f"<Value: date={dt}, value={v}>"

    def __repr__(self):
        return str(self)


class ScenariosValue(namedtuple("Value", ("date", "scenarios"))):
    """
    A time series value of scenarios.

    Implemented as a namedtuple of (date, scenarios).

    .. py:attribute:: date

        The date-time for a time series value (index)

    .. py:attribute:: scenarios

        A tuple of scenario values
    """

    def value_type(self):
        """
        Get the value type for this tuple.

        :return: The value type for this tuple
        :rtype: ValueType
        """
        return ValueType.SCENARIOS

    def validate(self):
        """
        Check if this time series value is in a valid format.

        :raises ValueError: When this value tuple is invalid
        """
        if not isinstance(self.date, datetime):
            raise ValueError("ScenariosValue.date is not a datetime")
        if not (self.scenarios is tuple):
            raise ValueError("ScenariosValue.scenarios is not a tuple")
        if not all(
                (s is None or isinstance(s, (numbers.Number)))
                for s in self.scenarios
            ):
            raise ValueError(
                "ScenariosValue.scenarios has members that aren't numbers"
            )

    def num_scenarios(self):
        """
        Count number of scenarios in this data point.

        :return: Number of scenarios in this data point.
        :rtype: int
        """
        return len(self.scenarios)

    def has_scenarios(self):
        """
        Check whether or not this data point has `support` for scenarios.

        :return: Always True, as ScenariosValue-types has scenarios
        :rtype: bool
        """
        return True

    def print(self, file=sys.stdout):
        """
        Print this time series value.
        """
        dt = self.date.isoformat(sep=' ')
        s = self.scenarios
        print(f"{dt}\t{s}", file=file)

    def to_dict(self):
        """
        Convert a time series value to a dict in the same short
        format as the API response.

        :return: A dict of this value in the same format as the API response
        :rtype: dict
        """
        return {
            "d": self.date.isoformat(sep=' '),
            "s": self.scenarios
        }

    def __str__(self):
        dt = self.date.isoformat(sep=' ')
        s = self.scenarios
        return f"<ScenariosValue: date={dt}, scenarios={s}>"

    def __repr__(self):
        return str(self)


class MeanScenariosValue(namedtuple("Value", ("date", "value", "scenarios"))):
    """
    A time series value with scenarios and a mean value.

    Implemented as a namedtuple of (date, value, scenarios).

    .. py:attribute:: date

        The date-time for a time series value (index)

    .. py:attribute:: value

        The numeric value

    .. py:attribute:: scenarios

        A tuple of scenario values
    """

    def value_type(self):
        """
        Get the value type for this tuple.

        :return: The value type for this tuple
        :rtype: ValueType
        """
        return ValueType.MEAN_AND_SCENARIOS

    def validate(self):
        """
        Check if this time series value is in a valid format.

        :raises ValueError: When this value tuple is invalid
        """
        if not isinstance(self.date, datetime):
            raise ValueError("ScenariosValue.date is not a datetime")
        if not (self.value is None or isinstance(self.value, (numbers.Number))):
            raise ValueError("Value.value must either be a number or None")
        if not (self.scenarios is tuple):
            raise ValueError("ScenariosValue.scenarios is not a tuple")
        if not all(
                (s is None or isinstance(s, (numbers.Number)))
                for s in self.scenarios
            ):
            raise ValueError(
                "MeanScenariosValue.scenarios has members that aren't numbers"
            )

    def num_scenarios(self):
        """
        Count number of scenarios in this data point.

        :return: Number of scenarios in this data point.
        :rtype: int
        """
        return len(self.scenarios)

    def has_scenarios(self):
        """
        Check whether or not this data point has `support` for scenarios.

        :return: Always True, as MeanScenariosValue-types has scenarios
        :rtype: bool
        """
        return True

    def print(self, file=sys.stdout):
        """
        Print this time series value.
        """
        dt = self.date.isoformat(sep=' ')
        v = self.value
        s = self.scenarios
        print(f"{dt}\t{v:13.2f}\t{s}", file=file)

    def to_dict(self):
        """
        Convert a time series value to a dict in the same short
        format as the API response.

        :return: A dict of this value in the same format as the API response
        :rtype: dict
        """
        return {
            "d": self.date.isoformat(sep=' '),
            "v": self.value,
            "s": self.scenarios
        }

    def __str__(self):
        dt = self.date.isoformat(sep=' ')
        v = self.value
        s = self.scenarios
        return f"<MeanScenariosValue: date={dt}, value={v}, scenarios={s}>"

    def __repr__(self):
        return str(self)


class Timeseries(Series):
    """
    A time series with metadata.

    :param curve: The curve, defaults to None
    :type curve: Curve, optional
    :param resolution: The resolution of the time series, defaults to None
    :type resolution: Resolution, optional
    :param instance: The instance, defaults to None
    :type instance: Instance, optional
    :param data: A list of values (Value, ScenariosValue, or MeanScenariosValue)
    :type data: list[]
    :param scenario_names: A list of scenario names, if any
    :type scenario_names: list[str], optional
    """

    def __init__(self, data=None, scenario_names=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert isinstance(self.resolution, Resolution), (
            "Timeseries.resolution is required"
        )
        self.data = data or []
        self.scenario_names = scenario_names or []
        self._fix_scenario_names()

    def __str__(self):
        items = []
        items.append(f"resolution={self.resolution}")
        items.append(f"curve=\"{self.curve}\"")
        if self.instance:
            items.append(f"instance={self.instance}")
        if self.has_scenarios():
            items.append(f"scenario_names={self.scenario_names}")
        if self.has_data():
            items.append(f"begin=\"{self.begin().isoformat(sep=' ')}\"")
            items.append(f"end=\"{self.end().isoformat(sep=' ')}\"")
        else:
            items.append("EMPTY")
        return f"<Timeseries: {', '.join(items)}>"

    def __repr__(self):
        return str(self)

    def _fix_scenario_names(self):
        if self.data and self.data[0].has_scenarios() \
                and not self.scenario_names:
            num_scenarios = self.data[0].num_scenarios()
            self.scenario_names = [f'e{i:02}' for i in range(num_scenarios)]


    def has_scenarios(self):
        """
        Check whether or not this time series has scenarios.

        :return: True when this time series has scenarios, otherwise False
        :rtype: bool
        """
        return (
            len(self.scenario_names) > 0 or
            (self.data and self.data[0].has_scenarios())
        )

    def value_type(self):
        """
        Return the value type of this time series.

        :return: The value type of this time series
        :rtype: ValueType
        """
        if self.has_data():
            return self.data[0].value_type()
        else:
            return ValueType.VALUE

    def begin(self):
        if self.data:
            return self.data[0].date
        else:
            raise ValueError("Timeseries has no values")

    def end(self):
        if self.data:
            return self.resolution >> self.data[-1].date
        else:
            raise ValueError("Timeseries has no values")

    def to_df(self, name=None):
        """
        Alias for :meth:`Timeseries.to_dataframe`. Convert this timeseries
        to a ``pandas.DataFrame``.

        :param name: Set a name for the value column, defaults to ``value``
        :type name: str, optional
        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return self.to_dataframe(name=name)

    def to_dataframe(self, name=None):
        """
        Convert this timeseries to a ``pandas.DataFrame``.

        :param name: Set a name for the value column, defaults to ``value``
        :type name: str, optional
        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return timeseries_to_dataframe(self, name=name)

    def validate(self):
        """
        Validate the time series.
        """
        # Check resolution
        if not self.resolution:
            raise ValueError("Timeseries has no resolution")
        r = self.resolution
        # Empty is OK
        if not self.data:
            return
        # Check all data points
        d = self.data[0].date
        for index, item in enumerate(self.data):
            # Validate values
            item.validate()
            # Check date vs resolution
            if not r.matches(item.date):
                raise ValueError(
                    f"Date-time not in Resolution: {item.date} at index {index}"
                )
            # Check if the current date
            if not d == item.date:
                raise ValueError(
                    f"Expected {d}, but got {item.date} at index {index}"
                )
            d = r >> d

    def print(self, file=sys.stdout):
        """
        Utility method to print a time series to any file handle (defaults
        to stdout).
        """
        print(f"Timeseries:", file=file)
        if self.curve:
            print(f"  Curve: {repr(self.curve)}", file=file)
        if self.instance:
            print(f"  Instance: {self.instance}", file=file)
        if self.scenario_names:
            print(f"  Scenarios: {self.scenario_names}", file=file)
        print(f"  Resolution: {self.resolution}", file=file)
        print(f"", file=file)
        for d in self.data:
            d.print(file=file)
