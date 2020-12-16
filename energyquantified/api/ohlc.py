from .base import BaseAPI

from ..exceptions import ValidationError
from ..metadata import CurveType, OHLCField
from ..parser.ohlc import parse_ohlc_response
from ..parser.timeseries import parse_timeseries
from ..parser.periodseries import parse_periodseries


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

        This operation works for curves with ``curve_type = OHLC`` only.

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

    def latest(
            self,
            curve,
            date=None):
        """
        Select all OHLC for specific trading day, while defaulting to the
        latest available OHLC data.

        If ``date`` is given, this method will try to fetch OHLC data for
        that trading day. When there is no data for the given day, OHLC data
        will be loaded for the closest trading day earlier in time with data.

        This operation works for curves with ``curve_type = OHLC`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param date: The trading date, defaults to today
        :type date: date, str, required
        :return: A list of OHLC objects
        :rtype: :py:class:`energyquantified.data.OHLCList`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/ohlc/{safe_curve}/latest/"
        # Parameters
        params = {}
        self._add_date(params, "date", date)
        # HTTP request
        response = self._get(url, params=params)
        return parse_ohlc_response(response.json())

    def load_delivery_as_timeseries(
            self,
            curve,
            begin=None,
            end=None,
            period=None,
            delivery=None,
            field=OHLCField.SETTLEMENT,
            fill=None):
        """
        Load historical OHLC data for specific contract, and convert it to a
        :py:class:`energyquantified.data.Timeseries`.

        Defaults to use the settlement field, but you can select any field
        you want. All other parameters are required.

        This operation works for curves with ``curve_type = OHLC`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date
        :type begin: date, str, required
        :param end: The end date
        :type end: date, str, required
        :param period: The contract period (week, month, quarter)
        :type period: ContractPeriod, str, required
        :param delivery: The delivery date for the contract
        :type delivery: date, str, required
        :param field: The field (close, settlement, etc.) to extract to a\
            time series, defaults to ``OHLCField.SETTLEMENT``
        :type field: OHLCField, str, required
        :param fill: How to handle days without trades. Allowed values are:\
            ``no-fill`` do nothing, ``fill-holes`` fill in holes with data\
            from previous trading day, ``forward-fill`` fill in all blanks\
            with data from the previous trading day (also into the future).\
            Defaults to ``no-fill``.
        :type fill: str, optional
        :return: A time series
        :rtype: :py:class:`energyquantified.data.Timeseries`
        """
        # Curve name for URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        # Parameters
        params = {}
        self._add_date(params, "begin", begin, required=True)
        self._add_date(params, "end", end, required=True)
        self._add_contract_period(params, "period", period, required=True)
        self._add_date(params, "delivery", delivery, required=True)
        self._add_fill(params, "fill", fill)
        # Build URL
        field = self._urlencode_ohlc_field(field, "field")
        url = f"/ohlc/{safe_curve}/timeseries/{field}/"
        # HTTP request
        response = self._get(url, params=params)
        return parse_timeseries(response.json())

    def load_front_as_timeseries(
            self,
            curve,
            begin=None,
            end=None,
            period=None,
            front=None,
            field=OHLCField.SETTLEMENT,
            fill=None):
        """
        Load historical OHLC data for a continuous front contract, and convert
        it to a :py:class:`energyquantified.data.Timeseries`.

        Defaults to use the settlement field, but you can select any field
        you want. All other parameters are required.

        This operation works for curves with ``curve_type = OHLC`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date
        :type begin: date, str, required
        :param end: The end date
        :type end: date, str, required
        :param period: The contract period (week, month, quarter)
        :type period: ContractPeriod, str, required
        :param front: The front contract (1=front, 2=second front, etc.)
        :type front: int, required
        :param field: The field (close, settlement, etc.) to extract to a\
            time series, defaults to ``OHLCField.SETTLEMENT``
        :type field: OHLCField, str, required
        :param fill: How to handle days without trades. Allowed values are:\
            ``no-fill`` do nothing, ``fill-holes`` fill in holes with data\
            from previous trading day, ``forward-fill`` fill in all blanks\
            with data from the previous trading day (also into the future).\
            Defaults to ``no-fill``.
        :type fill: str, optional
        :return: A time series
        :rtype: :py:class:`energyquantified.data.Timeseries`
        """
        # Curve name for URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        # Parameters
        params = {}
        self._add_date(params, "begin", begin, required=True)
        self._add_date(params, "end", end, required=True)
        self._add_contract_period(params, "period", period, required=True)
        self._add_int(params, "front", front, min=1, required=True)
        self._add_fill(params, "fill", fill)
        # Build URL
        field = self._urlencode_ohlc_field(field, "field")
        url = f"/ohlc/{safe_curve}/timeseries/{field}/"
        # HTTP request
        response = self._get(url, params=params)
        return parse_timeseries(response.json())

    def latest_as_periods(
            self,
            curve,
            field=OHLCField.SETTLEMENT,
            date=None):
        """
        Load all OHLC rows from a single trading day, sort them, and
        merge/convert them to a continuous series.

        It defaults to using the latest prices available, therefore
        "latest_as_period".

        If ``date`` is given, this method will try to fetch OHLC data for
        that trading day. When there is no data for the given day, OHLC data
        will be loaded for the closest trading day earlier in time with data.

        By default, this method uses the settlement price. Select another
        field, such as close price, by setting the `field` parameter.

        This operation works for curves with ``curve_type = OHLC`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param field: The field to generate the series from, \
            defaults to OHLCField.SETTLEMENT
        :type field: OHLCField, str, optional
        :param date: The trading date, defaults to today
        :type date: date, str, required
        :return: A period-based series
        :rtype: :py:class:`energyquantified.data.Periodseries`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        # Parameters
        params = {}
        self._add_date(params, "date", date)
        # Build URL
        field = self._urlencode_ohlc_field(field, "field")
        url = f"/ohlc/{safe_curve}/latest/periods/{field}/"
        # HTTP request
        response = self._get(url, params=params)
        return parse_periodseries(response.json())
