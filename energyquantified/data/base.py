

class Series:
    """
    Base class for Timeseries and Periodseries.
    """

    def __init__(self, curve=None, resolution=None, instance=None):
        # --- Members ---
        #: The curve
        self.curve = curve
        #: The resolution
        self.resolution = resolution
        #: The instance (if any)
        self.instance = instance
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
        return curve.name if self.curve else None

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
