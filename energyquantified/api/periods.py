from .base import BaseAPI

from ..metadata import CurveType
from ..parser.periodseries import parse_periodseries


# Tuple of supported values for Curve.curve_type in the periods API
CURVE_TYPES = (CurveType.PERIOD,)


class PeriodsAPI(BaseAPI):
    """
    Period-based series API operations. Access these operations via an
    instance of the :py:class:`energyquantified.EnergyQuantified` class:

       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.periods.load(curve, begin, end)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load(
            self,
            curve,
            begin=None,
            end=None):
        """
        Load period-based series data for a curve.

        This operation works for curves with ``curve_type = PERIOD`` only.

        :param curve: The curve or curve name
        :type curve:  :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date-time
        :type begin: date, datetime, str, required
        :param end: The end date-time
        :type end: date, datetime, str, required
        :return: A period-based series
        :rtype: :py:class:`energyquantified.data.Periodseries`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/periods/{safe_curve}/"
        # Parameters
        params = {}
        self._add_datetime(params, "begin", begin, required=True)
        self._add_datetime(params, "end", end, required=True)
        # HTTP request
        response = self._get(url, params=params)
        return parse_periodseries(response.json())
