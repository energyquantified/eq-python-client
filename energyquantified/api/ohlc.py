from .base import BaseAPI

from ..exceptions import ValidationError
from ..metadata import CurveType
from ..parser.ohlc import parse_ohlc_response


# Tuple of supported values for Curve.curve_type in the time series API
CURVE_TYPES = (CurveType.OHLC,)

class OhlcAPI(BaseAPI):
    """
    Operations for OHLC data retrieval. Access these operations via an
    instance of the :py:class:`energyquantified.EnergyQuantified` class:

       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.ohlc.load(curve, begin, end)
    """

    def load(
            self,
            curve,
            begin=None,
            end=None,
            period=None,
            delivery=None,
            front=None):
        """
        Load OHLC data for a :py:class:`energyquantified.metadata.Curve`.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date
        :type begin: date, str, required
        :param end: The end date
        :type end: date, str, required
        :param period: Filter on contract period (day, week, month etc.),\
            defaults to None
        :type period: ContractPeriod, str, optional
        :param delivery: Filter on delivery date, requires parameter ``period``\
            to be set; cannot be used together with ``front``, defaults to None
        :type delivery: date, str, optional
        :param front: Filter on front contract, requires parameter ``period``\
            to be set; cannot be used together with ``delivery``,\
            defaults to None
        :type front: int, optional
        :return: A list of OHLC objects
        :rtype: :py:class:`energyquantified.data.OHLCList`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/ohlc/{safe_curve}/"
        # Parameters
        params = {}
        self._add_date(params, "begin", begin, required=True)
        self._add_date(params, "end", end, required=True)
        self._add_contract_period(params, "period", period)
        self._add_int(params, "front", front, min=1)
        self._add_date(params, "delivery", delivery)
        # Additional checks
        has_period = "period" in params
        if has_period:
            if "front" in params and "delivery" in params:
                raise ValidationError(reason=(
                    "At most one of the following fields may be set: "
                    "'front', 'delivery'"
                ))
        else:
            if "front" in params:
                raise ValidationError(reason=(
                    "Parameter 'front' can only be used in together with "
                    "'period'"
                ))
            if "delivery" in params:
                raise ValidationError(reason=(
                    "Parameter 'delivery' can only be used in together with "
                    "'period'"
                ))
        # HTTP request
        response = self._get(url, params=params)
        return parse_ohlc_response(response.json())