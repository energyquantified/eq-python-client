from .base import BaseAPI

from ..metadata import CurveType
from ..parser.metadata import parse_instance_list
from ..parser.periodseries import parse_periodseries, parse_periodseries_list


# Tuple of supported values for Curve.curve_type in the period instances API
CURVE_TYPES = (CurveType.INSTANCE_PERIOD,)


class PeriodInstancesAPI(BaseAPI):
    """
    Period-based series instances API operations. Access these operations via
    an instance of the :py:class:`energyquantified.EnergyQuantified` class:

       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.period_instances.load(curve, begin, end)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list(
            self,
            curve,
            tags=None,
            exlude_tags=None,
            limit=20,
            issued_at_latest=None,
            issued_at_earliest=None):
        """
        List instances for the curve. Does not lad any period-based series.

        Filter on the instance `tags` or `exclude_tags` (list of values
        allowed), or restrict the instance issue date by setting
        `issued_at_latest` and/or `issued_at_earliest`.

        Limit the maximum number of returned instances by setting `limit`
        anywhere between 1 and 20.

        This operation works for curves with
        ``curve_type = INSTANCE_PERIOD`` only.

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
        url = f"/period-instances/{safe_curve}/list/"
        # Parameters
        params = {}
        self._add_str_list(params, "tags", tags)
        self._add_str_list(params, "exclude-tags", exlude_tags)
        self._add_int(params, "limit", limit, min=1, max=20, required=True)
        self._add_datetime(params, "issued-at-latest", issued_at_latest)
        self._add_datetime(params, "issued-at-earliest", issued_at_earliest)
        # HTTP request
        response = self._get(url, params=params)
        return parse_instance_list(response.json())

    def load(
            self,
            curve,
            begin=None,
            end=None,
            tags=None,
            exlude_tags=None,
            limit=3,
            issued_at_latest=None,
            issued_at_earliest=None):
        """
        Load period-based series instances.

        Filter on the instance `tags` or `exclude_tags` (list of values
        allowed), or restrict the instance issue date by setting
        `issued_at_latest` and/or `issued_at_earliest`.

        This operation works for curves with
        ``curve_type = INSTANCE_PERIOD`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date-time
        :type begin: date, datetime, str, required
        :param end: The end date-time
        :type end: date, datetime, str, required
        :param tags: Filter by instance tags, defaults to None
        :type tags: list, str, optional
        :param exlude_tags: Exclude instance tags, defaults to None
        :type exlude_tags: list, str, optional
        :param limit: Number of instances returned, defaults to 3
        :type limit: int, optional
        :param issued_at_latest: Filter by issue date, defaults to None
        :type issued_at_latest: datetime, date, str, optional
        :param issued_at_earliest: Filter by issue date, defaults to None
        :type issued_at_earliest: datetime, date, str, optional
        :return: List of :py:class:`energyquantified.data.Periodseries` objects
        :rtype: list
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/period-instances/{safe_curve}/"
        # Parameters
        params = {}
        self._add_datetime(params, "begin", begin, required=True)
        self._add_datetime(params, "end", end, required=True)
        self._add_str_list(params, "tags", tags)
        self._add_str_list(params, "exclude-tags", exlude_tags)
        self._add_int(params, "limit", limit, min=1, max=20, required=True)
        self._add_datetime(params, "issued-at-latest", issued_at_latest)
        self._add_datetime(params, "issued-at-earliest", issued_at_earliest)
        # HTTP request
        response = self._get(url, params=params)
        return parse_periodseries_list(response.json())

    def latest(
            self,
            curve,
            begin=None,
            end=None,
            issued_at_latest=None):
        """
        Get the latest period-based series instance.

        This operation works for curves with
        ``curve_type = INSTANCE_PERIOD`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date-time
        :type begin: date, datetime, str, required
        :param end: The end date-time
        :type end: date, datetime, str, required
        :param issued_at_latest: The latest issue date for the loaded instance,\
             defaults to None
        :type issued_at_latest: date, datetime, str, optional
        :return: A period-based series
        :rtype: :py:class:`energyquantified.data.Periodseries`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/period-instances/{safe_curve}/get/latest/"
        # Parameters
        params = {}
        self._add_datetime(params, "begin", begin, required=True)
        self._add_datetime(params, "end", end, required=True)
        self._add_datetime(params, "issued-at-latest", issued_at_latest)
        # HTTP request
        response = self._get(url, params=params)
        return parse_periodseries(response.json())

    def get(
            self,
            curve,
            begin=None,
            end=None,
            issued=None,
            tag=""):
        """
        Get a specific period-based series instance.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date-time
        :type begin: date, datetime, str, required
        :param end: The end date-time
        :type end: date, datetime, str, required
        :param issued: The instance issue date
        :type issued: datetime, date, str, required
        :param tag: The instance tag
        :type tag: str, required
        :return: A period-based series
        :rtype: :py:class:`energyquantified.data.Periodseries`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/period-instances/{safe_curve}/get/latest/"
        safe_issued = self._urlencode_datetime(issued, "issued")
        if tag:
            safe_tag = self._urlencode_string(tag, "tag", lambda t: t.strip())
            url = f"/period-instances/{safe_curve}/get/{safe_issued}/{safe_tag}/"
        else:
            url = f"/period-instances/{safe_curve}/get/{safe_issued}/"
        # Parameters
        params = {}
        self._add_datetime(params, "begin", begin, required=True)
        self._add_datetime(params, "end", end, required=True)
        # HTTP request
        response = self._get(url, params=params)
        return parse_periodseries(response.json())
