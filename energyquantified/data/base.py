

class Series:
    """
    Base class for Timeseries and Periodseries.
    """

    def __init__(
            self,
            curve=None,
            name=None,
            resolution=None,
            instance=None,
            contract=None):
        # --- Members ---
        #: The curve
        self.curve = curve
        self._name = None
        #: The resolution
        self.resolution = resolution
        #: The instance (if any)
        self.instance = instance
        #: The contract for OHLC operations resulting in a time series
        self.contract = contract
        #: The data
        self.data = []

    @property
    def name(self):
        """
        Return the curve name, if a :class:`energyquantified.metadata.Curve`
        is associated with this series.

        :return: The ``curve.name`` if it exists, otherwise ``None``
        :rtype: str, NoneType
        """
        if self._name:
            return self._name
        if self.curve:
            return self.curve.name
        return None

    def set_name(self, name):
        """
        Set a custom name (defaults to using ``curve.name``).

        :param name: An user-defined name
        :type name: str
        """
        assert name is None or isinstance(name, str),\
            "name must be None or a string"
        self._name = name

    def instance_or_contract_dataframe_column_header(self):
        """
        Get the instance or contract for this time series, in a format
        fitting for a ``pandas.DataFrame`` column header.

        :return: An instance or contract column header for a data frame
        :rtype: str, NoneType
        """
        if self.instance:
            return self.instance.as_dataframe_column_header()
        if self.contract:
            return self.contract.as_dataframe_column_header()
        return ''

    def has_data(self):
        """
        Check if this series has any data.

        :return: True if there is at least one data point, otherwise False
        :rtype: bool
        """
        return bool(self.data)

    def begin(self):
        """
        Get the begin date-time in the timeseries (inclusive).

        :return: The begin date
        :rtype: datetime
        """
        # This method must be implemented in subclasses
        raise NotImplementedError("Method begin() is not implemented")

    def end(self):
        """
        Get the end date-time in the timeseries (exclusive).

        :return: The end date
        :rtype: datetime
        """
        # This method must be implemented in subclasses
        raise NotImplementedError("Method end() is not implemented")

    def __iter__(self):
        """
        Create a generator of all values in the time series.

        :return: A generator for all data points in the time series
        :rtype: generator
        """
        return (item for item in self.data or [])
