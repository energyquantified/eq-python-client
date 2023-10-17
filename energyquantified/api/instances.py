from .base import BaseAPI

from ..metadata import CurveType
from ..parser.metadata import parse_instance_list
from ..parser.timeseries import parse_timeseries, parse_timeseries_list
from ..parser.absolute import parse_absolute

# Tuple of supported values for Curve.curve_type in the instances API
CURVE_TYPES = (CurveType.INSTANCE,)


class InstancesAPI(BaseAPI):
    """
    Instance API operations. Access these operations via an
    instance of the :py:class:`energyquantified.EnergyQuantified` class:

       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.instances.list(curve, tags)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cache = {}

    def tags(self, curve):
        """
        Get all tags available for a curve.

        This operation works for curves with ``curve_type = INSTANCE`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :return: A set available tags for provded curve
        :rtype: set
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/instances/{safe_curve}/tags/"
        # HTTP request (check cache first)
        if self._cache.get(url):
            return self._cache[url]
        response = self._get(url)
        self._cache[url] = set(response.json())
        return self._cache[url]

    def list(
            self,
            curve,
            tags=None,
            exlude_tags=None,
            limit=25,
            issued_at_latest=None,
            issued_at_earliest=None):
        """
        List instances for the curve. Does not load any time series data.

        Filter on the instance `tags` or `exclude_tags` (list of values
        allowed), or restrict the instance issue date by setting
        `issued_at_latest` and/or `issued_at_earliest`.

        Limit the maximum number of returned instances by setting `limit`
        anywhere between 1 and 25.

        This operation works for curves with ``curve_type = INSTANCE`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param tags: Filter by instance tags, defaults to None
        :type tags: list, str, optional
        :param exlude_tags: Exclude instance tags, defaults to None
        :type exlude_tags: list, str, optional
        :param limit: Number of instances returned, defaults to 25
        :type limit: int, optional
        :param issued_at_latest: Filter by issue date, defaults to None
        :type issued_at_latest: datetime, date, str, optional
        :param issued_at_earliest: Filter by issue date, defaults to None
        :type issued_at_earliest: datetime, date, str, optional
        :return: A list of :py:class:`energyquantified.metadata.Instance`
        :rtype: list
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/instances/{safe_curve}/list/"
        # Parameters
        params = {}
        self._add_str_list(params, "tags", tags)
        self._add_str_list(params, "exclude-tags", exlude_tags)
        self._add_int(params, "limit", limit, min=1, max=25, required=True)
        self._add_datetime(params, "issued-at-latest", issued_at_latest)
        self._add_datetime(params, "issued-at-earliest", issued_at_earliest)
        # HTTP request
        response = self._get(url, params=params)
        return parse_instance_list(response.json())

    def load(
            self,
            curve,
            tags=None,
            exlude_tags=None,
            limit=5,
            issued_at_latest=None,
            issued_at_earliest=None,
            time_zone=None,
            frequency=None,
            aggregation=None,
            hour_filter=None,
            threshold=None,
            ensembles=False,
            unit=None):
        """
        Load time series instances.

        Filter on the instance `tags` or `exclude_tags` (list of values
        allowed), or restrict the instance issue date by setting
        `issued_at_latest` and/or `issued_at_earliest`.

        When `ensembles` is `False`: Adjust the maximum number of returned
        time series instances by setting `limit` between 1 and 25.

        When `ensembles` is `True`: `limit` must be between 1 and 10.

        Supports aggregation by specifying a `frequency`. Optionally, you
        can specify the `aggregation` method (default is average) and the
        hourly filter (base, peak, etc.).

        This operation works for curves with ``curve_type = INSTANCE`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param tags: Filter by instance tags, defaults to None
        :type tags: list, str, optional
        :param exlude_tags: Exclude instance tags, defaults to None
        :type exlude_tags: list, str, optional
        :param limit: Maximum number of instances returned, defaults to 5
        :type limit: int, optional
        :param issued_at_latest: [description], defaults to None
        :type issued_at_latest: [type], optional
        :param issued_at_earliest: [description], defaults to None
        :type issued_at_earliest: [type], optional
        :param time_zone: Set the timezone for the date-times
        :type time_zone: TzInfo, optional
        :param frequency: Set the preferred frequency for aggregations,\
            defaults to None
        :type frequency: Frequency, optional
        :param aggregation: The aggregation method (i.e. AVERAGE, MIN, MAX),\
            has no effect unless *frequency* is provided, defaults to AVERAGE
        :type aggregation: Aggregation, optional
        :param hour_filter: Filters on hours to include (i.e. BASE, PEAK),\
            has no effect unless *frequency* is provided, defaults to BASE
        :type hour_filter: Filter, optional
        :param threshold: Allow that many values to be missing within one \
            frame of *frequency*. Has no effect unless *frequency* is \
            provided, defaults to 0.
        :type threshold: int, optional
        :param ensembles: Whether to include ensembles where available,\
            defaults to False
        :type ensembles: bool, optional
        :param unit: Convert unit of data, defaults to curves unit
        :type unit: str, optional
        :return: A list :py:class:`energyquantified.data.Timeseries` instances
        :rtype: list
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        if ensembles:
            url = f"/ensembles/{safe_curve}/"
        else:
            url = f"/instances/{safe_curve}/"
        # Parameters
        params = {}
        self._add_str_list(params, "tags", tags)
        self._add_str_list(params, "exclude-tags", exlude_tags)
        if ensembles:
            self._add_int(params, "limit", limit, min=1, max=25, required=True)
        else:
            self._add_int(params, "limit", limit, min=1, max=10, required=True)
        self._add_datetime(params, "issued-at-latest", issued_at_latest)
        self._add_datetime(params, "issued-at-earliest", issued_at_earliest)
        self._add_time_zone(params, "timezone", time_zone, required=False)
        self._add_frequency(params, "frequency", frequency)
        if "frequency" in params:
            self._add_aggregation(params, "aggregation", aggregation)
            self._add_filter(params, "hour-filter", hour_filter)
            self._add_int(params, "threshold", threshold, min=0)
        self._add_str(params, "unit", unit)
        # HTTP request
        response = self._get(url, params=params)
        return parse_timeseries_list(response.json())

    def latest(
            self,
            curve,
            tags=None,
            issued_at_latest=None,
            time_zone=None,
            frequency=None,
            aggregation=None,
            hour_filter=None,
            threshold=None,
            ensembles=False,
            unit=None):
        """
        Get the latest time series instance with filtering on `tags` and
        `issued_at_latest`.

        Supports aggregation by specifying a `frequency`. Optionally, you
        can specify the `aggregation` method (default is average) and the
        hourly filter (base, peak, etc.).

        This operation works for curves with ``curve_type = INSTANCE`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param tags: Filter by instance tags, defaults to None
        :type tags: list, str, optional
        :param issued_at_latest: [description], defaults to None
        :type issued_at_latest: [type], optional
        :param time_zone: Set the timezone for the date-times
        :type time_zone: TzInfo, optional
        :param frequency: Set the preferred frequency for aggregations,\
            defaults to None
        :type frequency: Frequency, optional
        :param aggregation: The aggregation method (i.e. AVERAGE, MIN, MAX),\
            has no effect unless *frequency* is provided, defaults to AVERAGE
        :type aggregation: Aggregation, optional
        :param hour_filter: Filters on hours to include (i.e. BASE, PEAK),\
            has no effect unless *frequency* is provided, defaults to BASE
        :type hour_filter: Filter, optional
        :param threshold: Allow that many values to be missing within one \
            frame of *frequency*. Has no effect unless *frequency* is provided,\
            defaults to 0.
        :type threshold: int, optional
        :param ensembles: Whether to include ensembles where available,\
            defaults to False
        :type ensembles: bool, optional
        :param unit: Convert unit of data, defaults to curves unit
        :type unit: str, optional
        :return: A time series instance
        :rtype: :py:class:`energyquantified.data.Timeseries`
        """

        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        if ensembles:
            url = f"/ensembles/{safe_curve}/get/latest/"
        else:
            url = f"/instances/{safe_curve}/get/latest/"
        # Parameters
        params = {}
        self._add_str_list(params, "tags", tags)
        self._add_datetime(params, "issued-at-latest", issued_at_latest)
        self._add_time_zone(params, "timezone", time_zone, required=False)
        self._add_frequency(params, "frequency", frequency)
        if "frequency" in params:
            self._add_aggregation(params, "aggregation", aggregation)
            self._add_filter(params, "hour-filter", hour_filter)
            self._add_int(params, "threshold", threshold, min=0)
        self._add_str(params, "unit", unit)
        # HTTP request
        response = self._get(url, params=params)
        return parse_timeseries(response.json())

    def get(
            self,
            curve,
            issued=None,
            tag="",
            time_zone=None,
            frequency=None,
            aggregation=None,
            hour_filter=None,
            threshold=None,
            ensembles=False,
            unit=None):
        """
        Get an instance specified by a `issued` (issue date) and `tag`. The
        default tag is blank and tags are case-insensitive.

        Supports aggregation by specifying a `frequency`. Optionally, you
        can specify the `aggregation` method (default is average) and the
        hourly filter (base, peak, etc.).

        This operation works for curves with ``curve_type = INSTANCE`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param issued: The issue date-time, defaults to None
        :type issued: datetime, date, str, optional
        :param tag: The instance tag, defaults to ""
        :type tag: str, optional
        :param frequency: Set the preferred frequency for aggregations,\
            defaults to None
        :param time_zone: Set the timezone for the date-times
        :type time_zone: TzInfo, optional
        :type frequency: Frequency, optional
        :param aggregation: The aggregation method (i.e. AVERAGE, MIN, MAX),\
            has no effect unless *frequency* is provided, defaults to AVERAGE
        :type aggregation: Aggregation, optional
        :param hour_filter: Filters on hours to include (i.e. BASE, PEAK),\
            has no effect unless *frequency* is provided, defaults to BASE
        :type hour_filter: Filter, optional
        :param threshold: Allow that many values to be missing within one \
            frame of *frequency*. Has no effect unless *frequency* is provided,\
            defaults to 0.
        :type threshold: int, optional
        :param ensembles: Whether to include ensembles where available,\
            defaults to False
        :type ensembles: bool, optional
        :param unit: Convert unit of data, defaults to curves unit
        :type unit: str, optional
        :return: A time series instance
        :rtype: :py:class:`energyquantified.data.Timeseries`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        safe_issued = self._urlencode_datetime(issued, "issued")
        category = "ensembles" if ensembles else "instances"
        if tag:
            safe_tag = self._urlencode_string(tag, "tag", lambda t: t.lower())
            url = f"/{category}/{safe_curve}/get/{safe_issued}/{safe_tag}/"
        else:
            url = f"/{category}/{safe_curve}/get/{safe_issued}/"
        # Parameters
        params = {}
        self._add_time_zone(params, "timezone", time_zone, required=False)
        self._add_frequency(params, "frequency", frequency)
        if "frequency" in params:
            self._add_aggregation(params, "aggregation", aggregation)
            self._add_filter(params, "hour-filter", hour_filter)
            self._add_int(params, "threshold", threshold, min=0)
        self._add_str(params, "unit", unit)
        # HTTP request
        response = self._get(url, params=params)
        return parse_timeseries(response.json())

    def relative(
            self,
            curve,
            begin=None,
            end=None,
            tag=None,
            days_ahead=1,
            issued="latest",
            time_of_day=None,
            after_time_of_day=None,
            before_time_of_day=None,
            modified_at_latest=None,
            time_zone=None,
            frequency=None,
            aggregation=None,
            hour_filter=None,
            threshold=None,
            unit=None):
        """
        Load one instance for each day based on some common criteria, stitch
        them together and return a continuous time series.

        By default, this method selects the day-ahead instances (forecasts),
        but you can set ``days_ahead`` to 0 or higher. 0 means intraday,
        1 means the day-ahead (default), 2 means the day after day-ahead,
        and so on.

        You may control the time of the day the instance is issued by setting
        exactly one of the follow parameters: ``time_of_day``,
        ``after_time_of_day`` or ``before_time_of_day``. Additionally, you may
        control the time of the day the instance has been modified (or created
        if modified is null) by setting ``modified-at-latest``. These should be
        set to a time (HH:MM:SS). You can use the :py:class:`datetime.time`.

        This operation works for curves with ``curve_type = INSTANCE`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date-time
        :type begin: date, datetime, str, required
        :param end: The end date-time
        :type end: date, datetime, str, required
        :param days_ahead: The number of leading days (0 or higher),\
            defaults to 1
        :type days_ahead: int, optional
        :param issued: Whether to select the earliest or latest matching\
            instance per day, allowed values "earliest" | "latest",\
            defaults to "earliest"
        :type issued: str, optional
        :param time_of_day: The exact time of the instance is issued,\
            defaults to None
        :type time_of_day: time, str, optional
        :param after_time_of_day: The instance must be issued at this time of\
            day or after, defaults to None
        :type after_time_of_day: time, str, optional
        :param before_time_of_day:  The instance must be issued before this\
            time of day, defaults to None
        :type before_time_of_day: time, str, optional
        :param modified-at-latest:  The instance must be modified (or created\
            if modified is null) before this time of day, defaults to None
        :type modified-at-latest: time, str, optional
        :param time_zone: Set the timezone for the date-times
        :type time_zone: TzInfo, optional
        :param frequency: Set the preferred frequency for aggregations,\
            defaults to None
        :type frequency: Frequency, optional
        :param aggregation: The aggregation method (i.e. AVERAGE, MIN, MAX),\
            has no effect unless *frequency* is provided, defaults to AVERAGE
        :type aggregation: Aggregation, optional
        :param hour_filter: Filters on hours to include (i.e. BASE, PEAK),\
            has no effect unless *frequency* is provided, defaults to BASE
        :type hour_filter: Filter, optional
        :param threshold: Allow that many values to be missing within one \
            frame of *frequency*. Has no effect unless *frequency* is provided, \
            defaults to 0.
        :type threshold: int, optional
        :param unit: Convert unit of data, defaults to curves unit
        :type unit: str, optional
        :return: A time series
        :rtype: :py:class:`energyquantified.data.Timeseries`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/instances/{safe_curve}/get/relative/"
        # Parameters
        params = {}
        self._add_datetime(params, "begin", begin, required=True)
        self._add_datetime(params, "end", end, required=True)
        self._add_str(params, "tag", tag, required=True)
        self._add_int(params, "days-ahead", days_ahead, min=0, max=10000,
                      required=True)
        self._add_str(params, "issued", issued,
                      allowed_values=['earliest', 'latest'], required=True)
        self._add_time(params, "time-of-day", time_of_day)
        self._add_time(params, "after-time-of-day", after_time_of_day)
        self._add_time(params, "before-time-of-day", before_time_of_day)
        self._add_time(params, "modified-at-latest", modified_at_latest)
        self._add_time_zone(params, "timezone", time_zone, required=False)
        self._add_frequency(params, "frequency", frequency)
        if "frequency" in params:
            self._add_aggregation(params, "aggregation", aggregation)
            self._add_filter(params, "hour-filter", hour_filter)
            self._add_int(params, "threshold", threshold, min=0)
        self._add_str(params, "unit", unit)
        # HTTP request
        response = self._get(url, params=params)
        return parse_timeseries(response.json())

    def absolute(
            self,
            curve,
            delivery,
            begin,
            end,
            frequency=None,
            time_zone=None,
            hour_filter=None,
            unit=None,
            aggregation=None,
            tags=None,
            exclude_tags=None,
        ):
        """
        Load forecasted values from various instances for a specific point in time,
        to see how forecasts develop over time.

        The point in time is the datetime supplied to the ``delivery`` parameter.
        Choose the frequency of the delivery by providing the ``frequency``
        parameter. If a frequency is not provided, it defaults to using the Curve's
        frequency.

        Loads forecasted values from instances issued between ``begin`` (inclusive)
        and ``end`` (exclusive).

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param delivery: The datetime to load forecasted values for. The\
            frequency and time zone of the delivery defaults to the Curve's\
            frequency and instance zone, respectively, but can be changed by the\
            ``frequency`` and ``time_zone`` parameters.
        :type delivery: date, datetime, str, required
        :param begin: Earliest instance issued date-time (inclusive)
        :type begin: date, datetime, str, required
        :param end: Latest instance issued date-time (exclusive)
        :type end: date, datetime, str, required
        :param frequency: Aggregate the delivery to a lower frequency than the\
            Curve's frequency. Defaults to None, which keeps the result in the\
            Curve's frequency.
        :type frequency: Frequency, optional
        :param time_zone: Timezone of the delivery. Defaults to the Curve's\
            instance zone.
        :type time_zone: TzInfo, optional
        :param hour_filter: Filter on hours to include (i.e. BASE, PEAK),\
            has no effect unless *frequency* is provided. Defaults to BASE.
        :type hour_filter: Filter, optional
        :param unit: Convert unit of the data. Defaults to using the Curve's unit.
        :type unit: str, optional
        :param aggregation: The aggregation method (i.e. AVERAGE, MIN, MAX),\
            has no effect unless *frequency* is provided. Defaults to AVERAGE.
        :type aggregation: Aggregation, optional
        :param tags: Filter instances by tags, excluding instances not matching\
            any of the tags. Defaults to None, which does not filter.
        :type tags: list, str, optional
        :param exclude_tags: Filter instances by tags, excluding instances\
            matching any of the tags.
        :type exclude_tags: list, str, optional
        :return: An absolute result
        :rtype: :py:class:`energyquantified.data.AbsoluteResult`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/instances/{safe_curve}/get/absolute/"
        # Parameters
        params = {}
        self._add_datetime(params, "delivery", delivery, required=True)
        self._add_datetime(params, "begin", begin, required=True)
        self._add_datetime(params, "end", end, required=True)
        self._add_frequency(params, "frequency", frequency, required=False)
        self._add_time_zone(params, "timezone", time_zone, required=False)
        self._add_str(params, "unit", unit, required=False)
        self._add_str_list(params, "tags", tags, required=False)
        self._add_str_list(params, "exclude-tags", exclude_tags, required=False)
        if "frequency" in params:
            self._add_aggregation(params, "aggregation", aggregation, required=False)
            self._add_filter(params, "hour-filter", hour_filter, required=False)
        # HTTP request
        response = self._get(url, params=params)
        return parse_absolute(response.json())
