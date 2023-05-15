import enum
from datetime import datetime, date

from ..time import Frequency


_aggregation_lookup = {}

class Aggregation(enum.Enum):
    """
    Supported aggregations in the API. Includes simple implementations of
    the different aggregation types for learning purposes.
    """

    #: Calculate the mean value
    AVERAGE = (lambda items: sum(items) / len(items),)
    #: Calculate the sum of all values
    SUM = (sum,)
    #: Find the minimum value
    MIN = (min,)
    #: Find the maximum value
    MAX = (max,)

    def __init__(self, func):
        self._func = func
        _aggregation_lookup[self.tag.lower()] = self

    @property
    def tag(self):
        """
        Get the tag for this aggregation type.

        :return: The aggregation tag (name)
        :rtype: str
        """
        return self.name

    def aggregate(self, iterable):
        """
        Perform an aggregation on any iterable of numbers (such as lists,
        tuples, generators etc.).

        :param iterable: Any iterable of numbers
        :type iterable: iterable
        :return: An aggregate
        :rtype: float
        """
        return self._func(iterable)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether an aggregation tag exists or not.

        :param tag: An aggregation tag
        :type tag: str
        :return: True if it exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _aggregation_lookup

    @staticmethod
    def by_tag(tag):
        """
        Look up aggregation by tag.

        :param tag: An aggregation tag
        :type tag: str
        :return: The aggregation for the given tag
        :rtype: Aggregation
        """
        return _aggregation_lookup[tag.lower()]


_filter_lookup = {}

class Filter(enum.Enum):
    """
    Supported filters in the API.

    Includes simple implementations of the filters for learning
    purposes.

    Note: The API automatically separates futures peak and offpeak by
    looking at the selected frequency for aggregations:

     * For weekly, monthly, quartly and yearly frequency, the futures
       peak and offpeak are used.
     * For daily or higher frequencies, the standard peak and offpeak
       are used.

    """

    #: All hours
    BASE = (
        lambda dt: True,
        lambda dt: True
    )
    #: Peak hours
    PEAK = (
        lambda dt: 8 <= dt.hour <= 19,
        lambda dt: dt.isoweekday() <= 5 and 8 <= dt.hour <= 19
    )
    #: Offpeak hours
    OFFPEAK = (
        lambda dt: not PEAK.is_in_filter(dt),
        lambda dt: not PEAK.is_in_future_filter(dt),
    )
    #: Monday–Friday
    WORKDAYS = (
        lambda dt: dt.isoweekday() <= 5,
        lambda dt: dt.isoweekday() <= 5
    )
    #: Saturday and Sunday
    WEEKEND = (
        lambda dt: dt.isoweekday() > 5,
        lambda dt: dt.isoweekday() > 5
    )

    def __init__(self, filter_func, future_filter_func):
        self._filter_func = filter_func
        self._future_filter_func = future_filter_func
        _filter_lookup[self.tag.lower()] = self

    @property
    def tag(self):
        """
        The filter tag (name)
        """
        return self.name

    def get_filter_function(self, frequency):
        """
        Given a frequency, return the appropriate filter function:

         * For weekly, monthly, quartly and yearly frequency, the futures
           peak and offpeak function is used.
         * For daily or higher frequencies, the standard peak and offpeak
           function is used.

        :param frequency: The resulting frequency of an aggregation
        :type frequency: Frequency
        :return: A filter function
        :rtype: function
        """
        assert isinstance(frequency, Frequency), "Not a Frequency provided"
        if frequency >= Frequency.P1D:
            # For daily, hourly or higher frequencies
            return self._filter_func
        else:
            # For futures resolutions (weekly, monthly, quarterly, yearly)
            return self._future_filter_func

    def is_in_filter(self, datetime_obj):
        """
        Check whether or not a datetime object is in a filter.

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :return: True if the date-time object falls into filter, otherwise False
        :rtype: bool
        """
        assert isinstance(datetime_obj, datetime), "Not a datetime object"
        return self._filter_func(datetime_obj)

    def is_in_future_filter(self, datetime_obj):
        """
        Check whether or not a datetime object is in a filter for
        futures-contracts (weekly, monthly, quarterly, yearly).

        :param datetime_obj: A date-time
        :type datetime_obj: datetime
        :return: True if the date-time object falls into filter, otherwise False
        :rtype: bool
        """
        assert isinstance(datetime_obj, (datetime, date)), (
            "Not a datetime or date object"
        )
        return self._future_filter_func(datetime_obj)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a filter tag exists or not.

        :param tag: A filter tag
        :type tag: str
        :return: True if it exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _filter_lookup

    @staticmethod
    def by_tag(tag):
        """
        Look up a filter by tag.

        :param tag: A filter tag
        :type tag: str
        :return: The filter for the given tag
        :rtype: Filter
        """
        return _filter_lookup[tag.lower()]
