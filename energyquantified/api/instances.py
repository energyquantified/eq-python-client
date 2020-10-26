from .base import BaseAPI

from ..exceptions import ValidationError
from ..metadata import CurveType
from ..parser.metadata import parse_instance_list
from ..parser.timeseries import parse_timeseries, parse_timeseries_list


# Tuple of supported values for Curve.curve_type in the instances API
CURVE_TYPES = (CurveType.INSTANCE,)


class InstancesAPI(BaseAPI):
    """
    Instance API operations. Access these operations via an
    instance of the :py:class:`energyquantified.EnergyQuantified` class:

       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.timeseries.load(curve, begin, end)
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
            frequency=None,
            aggregation=None,
            hour_filter=None,
            ensembles=False):
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
        :param frequency: Set the preferred frequency for aggregations,\
            defaults to None
        :type frequency: Frequency, optional
        :param aggregation: The aggregation method (i.e. AVERAGE, MIN, MAX),\
            has no effect unless *frequency* is provided, defaults to AVERAGE
        :type aggregation: Aggregation, optional
        :param hour_filter: Filters on hours to include (i.e. BASE, PEAK),\
            has no effect unless *frequency* is provided, defaults to BASE
        :type hour_filter: Filter, optional
        :param ensembles: Whether or not to include ensembles where available,\
            defaults to False
        :type ensembles: bool, optional
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
        self._add_frequency(params, "frequency", frequency)
        if "frequency" in params:
            self._add_aggregation(params, "aggregation", aggregation)
            self._add_filter(params, "hour-filter", hour_filter)
        # HTTP request
        response = self._get(url, params=params)
        return parse_timeseries_list(response.json())

    def latest(
            self,
            curve,
            tags=None,
            issued_at_latest=None,
            frequency=None,
            aggregation=None,
            hour_filter=None,
            ensembles=False):
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
        :param frequency: Set the preferred frequency for aggregations,\
            defaults to None
        :type frequency: Frequency, optional
        :param aggregation: The aggregation method (i.e. AVERAGE, MIN, MAX),\
            has no effect unless *frequency* is provided, defaults to AVERAGE
        :type aggregation: Aggregation, optional
        :param hour_filter: Filters on hours to include (i.e. BASE, PEAK),\
            has no effect unless *frequency* is provided, defaults to BASE
        :type hour_filter: Filter, optional
        :param ensembles: Whether or not to include ensembles where available,\
            defaults to False
        :type ensembles: bool, optional
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
        self._add_frequency(params, "frequency", frequency)
        if "frequency" in params:
            self._add_aggregation(params, "aggregation", aggregation)
            self._add_filter(params, "hour-filter", hour_filter)
        # HTTP request
        response = self._get(url, params=params)
        return parse_timeseries(response.json())

    def get(
            self,
            curve,
            issued=None,
            tag="",
            frequency=None,
            aggregation=None,
            hour_filter=None,
            ensembles=False):
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
        :type frequency: Frequency, optional
        :param aggregation: The aggregation method (i.e. AVERAGE, MIN, MAX),\
            has no effect unless *frequency* is provided, defaults to AVERAGE
        :type aggregation: Aggregation, optional
        :param hour_filter: Filters on hours to include (i.e. BASE, PEAK),\
            has no effect unless *frequency* is provided, defaults to BASE
        :type hour_filter: Filter, optional
        :param ensembles: Whether or not to include ensembles where available,\
            defaults to False
        :type ensembles: bool, optional
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
        self._add_frequency(params, "frequency", frequency)
        if "frequency" in params:
            self._add_aggregation(params, "aggregation", aggregation)
            self._add_filter(params, "hour-filter", hour_filter)
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
            frequency=None,
            aggregation=None,
            hour_filter=None):
        """
        Load one instance for each day based on some common criteria, stitch
        them together and return a continuous time series.

        By default, this method selects the day-ahead instances (forecasts),
        but you can set ``days_ahead`` to 0 or higher. 0 means intraday,
        1 means the day-ahead (default), 2 means the day after day-ahead,
        and so on.

        You may control the time of the day the instance is issued by setting
        exactly one of the follow parameters: ``time_of_day``,
        ``after_time_of_day`` or ``before_time_of_day``. These should be set
        to a time (HH:MM:SS). You can use the :py:class:`datetime.time`.

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
        :param frequency: Set the preferred frequency for aggregations,\
            defaults to None
        :type frequency: Frequency, optional
        :param aggregation: The aggregation method (i.e. AVERAGE, MIN, MAX),\
            has no effect unless *frequency* is provided, defaults to AVERAGE
        :type aggregation: Aggregation, optional
        :param hour_filter: Filters on hours to include (i.e. BASE, PEAK),\
            has no effect unless *frequency* is provided, defaults to BASE
        :type hour_filter: Filter, optional
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
        self._add_int(params, "days-ahead", days_ahead, min=0, max=10000, required=True)
        self._add_str(params, "issued", issued, allowed_values=['earliest', 'latest'], required=True)
        self._add_time(params, "time-of-day", time_of_day)
        self._add_time(params, "after-time-of-day", after_time_of_day)
        self._add_time(params, "before-time-of-day", before_time_of_day)
        self._add_frequency(params, "frequency", frequency)
        if "frequency" in params:
            self._add_aggregation(params, "aggregation", aggregation)
            self._add_filter(params, "hour-filter", hour_filter)
        # Additional validation checks
        if sum(1 if t is not None else 0 for t in (time_of_day, after_time_of_day, before_time_of_day)) > 1:
            raise ValidationError(reason=(
                "At most one of the following fields must be set: "
                "time_of_day, after_time_of_day, before_time_of_day"
            ))
        # HTTP request
        response = self._get(url, params=params)
        return parse_timeseries(response.json())
