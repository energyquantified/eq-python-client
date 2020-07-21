from .base import BaseAPI

from ..metadata import CurveType
from ..parser.timeseries import parse_timeseries


# Tuple of supported values for Curve.curve_type in the time series API
CURVE_TYPES = (CurveType.TIMESERIES, CurveType.SCENARIO_TIMESERIES)

class TimeseriesAPI(BaseAPI):
    """
    Time series API operations. Access these operations via an
    instance of the :py:class:`energyquantified.EnergyQuantified` class:

       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.timeseries.load(curve, begin, end)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(
            self,
            curve,
            begin=None,
            end=None,
            frequency=None,
            aggregation=None,
            hour_filter=None):
        """
        Load time series data for a :py:class:`energyquantified.metadata.Curve`.

        This operation works for curves with
        ``curve_type = TIMESERIES | SCENARIO_TIMESERIES`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date-time
        :type begin: date, datetime, str, required
        :param end: The end date-time
        :type end: date, datetime, str, required
        :param frequency: Set the preferred frequency for aggregations, defaults to None
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
        url = f"/timeseries/{safe_curve}/"
        # Parameters
        params = {}
        self._add_datetime(params, "begin", begin, required=True)
        self._add_datetime(params, "end", end, required=True)
        self._add_frequency(params, "frequency", frequency)
        if "frequency" in params:
            self._add_aggregation(params, "aggregation", aggregation)
            self._add_filter(params, "hour-filter", hour_filter)
        # HTTP request
        response = self._get(url, params=params)
        return parse_timeseries(response.json())
