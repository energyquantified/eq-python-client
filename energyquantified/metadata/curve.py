import enum

from ..time import Resolution, UTC


class Curve:
    """
    The curve identifies any type of time series data and OHLC data.

    The ``curve.name`` is used in the API when loading data for a curve.
    """

    def __init__(self, name, curve_type=None, instance_issued_timezone=None,
                 area=None, area_sink=None, place=None,
                 resolution=None, frequency=None, timezone=None,
                 categories=None, unit=None, denominator=None, data_type=None,
                 source=None):
        #: The curve name is the identifier.
        self.name = name
        #: Curve type (the type of data this curve refers to).
        self.curve_type = curve_type
        if self.curve_type.has_instances:
            #: For instance-based curves: The time-zone of the issue date
            #: in the instance, see :py:attr:`Instance.issued`.
            self.instance_issued_timezone = instance_issued_timezone or UTC
        else:
            self.instance_issued_timezone = None
        # The areas and place (if any)
        #: The area
        self.area = area
        #: The importing area for exchange curves
        self.area_sink = area_sink
        if area_sink:
            #: The exporting area for exchange curves
            self.area_source = area
        self.place = place
        # Resolution
        if resolution:
            #: The frequency of data in this curve
            self.frequency = resolution.frequency
            #: The time-zone of date-times in this curve
            self.timezone = resolution.timezone
        else:
            self.frequency = frequency
            self.timezone = timezone
        # Other metadata
        #: List of categories for this curve.
        self.categories = categories
        #: The unit (MW, EUR, etc.). See also :py:attr:`Curve.denominator`.
        self.unit = unit
        #: The denominator (for EUR/MWh: unit=EUR and denominator=MWh). See
        #: also :py:attr:`Curve.unit`.
        self.denominator = denominator
        #: The data type, :py:class:`DataType`.
        self.data_type = data_type
        #: The source of the data.
        self.source = source

    @property
    def resolution(self):
        """
        The resolution (combination of frequency and timezone) for this curve.
        """
        return Resolution(self.frequency, self.timezone)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Curve: \"{self.name}\", curve_type={self.curve_type}>"


_datatype_lookup = {}

class DataType(enum.Enum):
    """
    Data types describe the type of data (i.e. actuals, forecast). This is
    the attribute that is always set as the last word in the curve name.
    """

    #: Third-party actuals collected by Energy Quantified, but not modified.
    ACTUAL = ("ACTUAL", "Actual")
    #: Scenario data where Energy Quantified has created.
    CLIMATE = ("CLIMATE", "Climate")
    #: A combination of third-party actuals and numbers generated by Energy
    #: Quantified, where we have filled missing with our best calculations.
    SYNTHETIC = ("SYNTHETIC", "Synthetic")
    #: The forecast models run backwards.
    BACKCAST = ("BACKCAST", "Backcast")
    #: The seasonal normals using 40 weather years.
    NORMAL = ("NORMAL", "Normal")
    #: Some model value (such as a factor).
    VALUE = ("VALUE", "Value")
    #: Forecasts generated by Energy Quantified unless another source is
    #: explicitly stated in the curve name.
    FORECAST = ("FORECAST", "Forecast")
    #: Currency rates.
    FOREX = ("FOREX", "Forex")
    #: Closing data from the market.
    OHLC = ("OHLC", "OHLC")
    #: Capacity data generated from REMIT outage messages.
    REMIT = ("REMIT", "REMIT")
    #: Total installed capacity.
    CAPACITY = ("CAPACITY", "Capacity")

    def __init__(self, tag=None, label=None):
        self.tag = tag
        self.label = label
        _datatype_lookup[tag.lower()] = self

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.name

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a data type tag exists or not.

        :param tag: A data type tag
        :type tag: str
        :return: True if it exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _datatype_lookup

    @staticmethod
    def by_tag(tag):
        """
        Look up data type by tag.

        :param tag: A data type tag
        :type tag: str
        :return: The data type for the given tag
        :rtype: DataType
        """
        return _datatype_lookup[tag.lower()]


_curvetype_lookup = {}

class CurveType(enum.Enum):
    """
    Curve type is not a part of the curve name.

    Curve type describes the storage format of the underlying data and which
    operations must be used to fetch data for these curves.

     * Load time series and scenario-based time series using the
       ``EnergyQuantified.timeseries.*`` operations.
     * To load instances (i.e. forecasts), use the
       ``EnergyQuantified.timeseries.*`` operations.
     * Periods and period-instances can be loaded by using each of
       their respective operations located under
       ``EnergyQuantified.periods.*`` and
       ``EnergyQuantified.instance_periods.*``.
     * OHLC means "open, high, low and close" data. To load data from
       these curves, use the OHLC operations.
    """

    #: Plain, fixed-interval time series data
    TIMESERIES = ("TIMESERIES", False)
    #: Plain, fixed-interval scenarios of time series data
    SCENARIO_TIMESERIES = ("SCENARIO_TIMESERIES", False)
    #: Instances (forecasts)
    INSTANCE = ("INSTANCE", True)
    #: Period-based data
    PERIOD = ("PERIOD", False)
    #: Instances of period-based data
    INSTANCE_PERIOD = ("INSTANCE_PERIOD", False)
    #: Closing prices for market data
    OHLC = ("OHLC", False)

    def __init__(self, tag=None, has_instances=False):
        self.tag = tag
        self.has_instances = has_instances
        _curvetype_lookup[tag.lower()] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a curve type tag exists or not.

        :param tag: A curve type tag
        :type tag: str
        :return: True if it exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _curvetype_lookup

    @staticmethod
    def by_tag(tag):
        """
        Look up curve type by tag.

        :param tag: A curve type tag
        :type tag: str
        :return: The curve type for the given tag
        :rtype: CurveType
        """
        return _curvetype_lookup[tag.lower()]
