from datetime import timedelta

from ..exceptions import ValidationError
from ..metadata import Curve, CurveType
from ..parser.timeseries import parse_timeseries_list
from ..parser.trades import (
    parse_trade_contract_list,
    parse_trade_ohlc_series_list,
)
from ..time import Frequency
from .base import BaseAPI

CURVE_TYPES = (CurveType.TRADES,)
TRADE_PERIODS = (Frequency.PT15M, Frequency.PT30M, Frequency.PT1H)

MIN_LEAD_TIME = timedelta(0)
MAX_LEAD_TIME = timedelta(hours=36)


class _BaseTradesAPI(BaseAPI):
    """
    Parameter handling shared by the trade contract and trade OHLC
    operations, as both search for contracts in a delivery interval.
    """

    def _contract_search_params(
        self,
        begin,
        end,
        after_time_of_day,
        before_time_of_day,
        periods,
        exclude_periods,
    ):
        params = {}
        self._add_datetime(params, "begin", begin, required=True)
        self._add_datetime(params, "end", end, required=True)
        self._add_time(params, "after-time-of-day", after_time_of_day)
        self._add_time(params, "before-time-of-day", before_time_of_day)
        self._add_frequency_list(
            params, "periods", periods, allowed_values=TRADE_PERIODS
        )
        self._add_frequency_list(
            params, "exclude-periods", exclude_periods, allowed_values=TRADE_PERIODS
        )
        return params


class TradesAPI(_BaseTradesAPI):
    """
    Trade operations. Access these operations via an instance of the
    :py:class:`energyquantified.EnergyQuantified` class:

       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.trades.contracts(curve, begin, end)

    OHLC data for trade contracts lives one level down, under
    :py:class:`energyquantified.api.TradesOhlcAPI`, mirroring the
    ``/trades/{curve}/ohlc/`` endpoints:

       >>> eq.trades.ohlc.load(curve, begin, end)
    """

    def __init__(self, client):
        super().__init__(client)
        #: See :py:class:`energyquantified.api.TradesOhlcAPI`. For loading
        #: OHLC data for trade contracts.
        self.ohlc = TradesOhlcAPI(client)

    def contracts(
        self,
        curve,
        begin=None,
        end=None,
        after_time_of_day=None,
        before_time_of_day=None,
        periods=None,
        exclude_periods=None,
    ):
        """
        List trade contracts in a delivery interval, without loading their
        OHLC data.

        This operation works for curves with ``curve_type = TRADES`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin of the delivery interval (inclusive)
        :type begin: date, datetime, str, required
        :param end: The end of the delivery interval (exclusive). It cannot\
            be more than one week after ``begin``.
        :type end: date, datetime, str, required
        :param after_time_of_day: Only include contracts whose delivery\
            begins at or after this local time of day
        :type after_time_of_day: time, str, optional
        :param before_time_of_day: Only include contracts whose delivery\
            begins before this local time of day
        :type before_time_of_day: time, str, optional
        :param periods: Only include contracts with these delivery periods.\
            Allowed values are ``PT15M``, ``PT30M``, and ``PT1H``.
        :type periods: Frequency, str, list, optional
        :param exclude_periods: Exclude contracts with these delivery periods
        :type exclude_periods: Frequency, str, list, optional
        :return: A list of trade contracts
        :rtype: list[:py:class:`energyquantified.data.TradeContract`]
        """
        timezone = curve.timezone if isinstance(curve, Curve) else None
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/trades/{safe_curve}/contracts/"
        params = self._contract_search_params(
            begin=begin,
            end=end,
            after_time_of_day=after_time_of_day,
            before_time_of_day=before_time_of_day,
            periods=periods,
            exclude_periods=exclude_periods,
        )
        response = self._get(url, params=params)
        return parse_trade_contract_list(response.json(), timezone=timezone)


class TradesOhlcAPI(_BaseTradesAPI):
    """
    OHLC operations for trade contracts. Access these operations via the
    ``ohlc`` attribute on :py:class:`energyquantified.api.TradesAPI`:

       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.trades.ohlc.load(curve, begin, end)
    """

    def load(
        self,
        curve,
        begin=None,
        end=None,
        after_time_of_day=None,
        before_time_of_day=None,
        periods=None,
        exclude_periods=None,
        frequency=None,
        aggregate_by_contract=False,
        min_lead_time=None,
        max_lead_time=None,
        unit=None,
    ):
        """
        Load OHLC data for all trade contracts matching a delivery-interval
        search.

        This operation works for curves with ``curve_type = TRADES`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin of the delivery interval (inclusive)
        :type begin: date, datetime, str, required
        :param end: The end of the delivery interval (exclusive). It cannot\
            be more than one week after ``begin``.
        :type end: date, datetime, str, required
        :param after_time_of_day: Only include contracts whose delivery\
            begins at or after this local time of day
        :type after_time_of_day: time, str, optional
        :param before_time_of_day: Only include contracts whose delivery\
            begins before this local time of day
        :type before_time_of_day: time, str, optional
        :param periods: Only include contracts with these delivery periods.\
            Allowed values are ``PT15M``, ``PT30M``, and ``PT1H``.
        :type periods: Frequency, str, list, optional
        :param exclude_periods: Exclude contracts with these delivery periods
        :type exclude_periods: Frequency, str, list, optional
        :param frequency: Aggregate the trade data into coarser buckets.\
            Buckets are aligned backwards from each contract's delivery. It\
            cannot be combined with ``aggregate_by_contract``.
        :type frequency: Frequency, str, optional
        :param aggregate_by_contract: Set to True to combine all trade data\
            for each contract into one OHLC value, defaults to False
        :type aggregate_by_contract: bool, optional
        :param min_lead_time: Only include trades made more than this long\
            before delivery begins (exclusive), defaults to ``PT0S``. It must\
            be between zero and 36 hours and a whole number of minutes.
        :type min_lead_time: timedelta, str, optional
        :param max_lead_time: Only include trades made at most this long\
            before delivery begins (inclusive), defaults to ``PT36H``. It must\
            be between zero and 36 hours and a whole number of minutes.
        :type max_lead_time: timedelta, str, optional
        :param unit: Convert the price fields to another unit, defaults to\
            the curve's unit
        :type unit: str, optional
        :return: A list of trade OHLC series, one per contract
        :rtype: :py:class:`energyquantified.data.TradeOHLCSeriesList`
        """
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/trades/{safe_curve}/ohlc/"
        params = self._contract_search_params(
            begin=begin,
            end=end,
            after_time_of_day=after_time_of_day,
            before_time_of_day=before_time_of_day,
            periods=periods,
            exclude_periods=exclude_periods,
        )
        self._add_ohlc_params(
            params,
            frequency=frequency,
            aggregate_by_contract=aggregate_by_contract,
            min_lead_time=min_lead_time,
            max_lead_time=max_lead_time,
        )
        self._add_str(params, "unit", unit)
        response = self._get(url, params=params)
        return parse_trade_ohlc_series_list(response.json())

    def load_as_timeseries(
        self,
        curve,
        field=None,
        begin=None,
        end=None,
        after_time_of_day=None,
        before_time_of_day=None,
        periods=None,
        exclude_periods=None,
        frequency=None,
        aggregate_by_contract=False,
        min_lead_time=None,
        max_lead_time=None,
        fill=None,
        unit=None,
    ):
        """
        Extract one trade OHLC field for every contract matching a
        delivery-interval search, and convert each of them to a
        :py:class:`energyquantified.data.Timeseries`.

        ``begin`` and ``end`` only bound the delivery interval used to find
        contracts. Each returned time series runs from the first to the last
        bucket with trades for its contract.

        This operation works for curves with ``curve_type = TRADES`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param field: The field (open, high, low, close, vwap, volume, or\
            count) to extract to a time series
        :type field: TradeOHLCField, str, required
        :param begin: The begin of the delivery interval (inclusive)
        :type begin: date, datetime, str, required
        :param end: The end of the delivery interval (exclusive). It cannot\
            be more than one week after ``begin``.
        :type end: date, datetime, str, required
        :param after_time_of_day: Only include contracts whose delivery\
            begins at or after this local time of day
        :type after_time_of_day: time, str, optional
        :param before_time_of_day: Only include contracts whose delivery\
            begins before this local time of day
        :type before_time_of_day: time, str, optional
        :param periods: Only include contracts with these delivery periods.\
            Allowed values are ``PT15M``, ``PT30M``, and ``PT1H``.
        :type periods: Frequency, str, list, optional
        :param exclude_periods: Exclude contracts with these delivery periods
        :type exclude_periods: Frequency, str, list, optional
        :param frequency: Aggregate the trade data into coarser buckets. It\
            cannot be combined with ``aggregate_by_contract``.
        :type frequency: Frequency, str, optional
        :param aggregate_by_contract: Set to True to combine all trade data\
            for each contract into one OHLC value, defaults to False
        :type aggregate_by_contract: bool, optional
        :param min_lead_time: Only include trades made more than this long\
            before delivery begins (exclusive), defaults to ``PT0S``
        :type min_lead_time: timedelta, str, optional
        :param max_lead_time: Only include trades made at most this long\
            before delivery begins (inclusive), defaults to ``PT36H``
        :type max_lead_time: timedelta, str, optional
        :param fill: How to handle buckets without trades between the first\
            and last observation. Allowed values are: ``no-fill`` do\
            nothing, ``fill-holes`` and ``forward-fill`` both repeat the\
            previous value. Defaults to ``no-fill``.
        :type fill: str, optional
        :param unit: Convert the price fields to another unit, defaults to\
            the curve's unit
        :type unit: str, optional
        :return: A list of time series, one per contract
        :rtype: :py:class:`energyquantified.data.TimeseriesList`
        """
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        safe_field = self._urlencode_trade_ohlc_field(field, "field")
        url = f"/trades/{safe_curve}/ohlc/timeseries/{safe_field}/"
        params = self._contract_search_params(
            begin=begin,
            end=end,
            after_time_of_day=after_time_of_day,
            before_time_of_day=before_time_of_day,
            periods=periods,
            exclude_periods=exclude_periods,
        )
        self._add_ohlc_params(
            params,
            frequency=frequency,
            aggregate_by_contract=aggregate_by_contract,
            min_lead_time=min_lead_time,
            max_lead_time=max_lead_time,
        )
        self._add_fill(params, "fill", fill)
        self._add_str(params, "unit", unit)
        response = self._get(url, params=params)
        return parse_timeseries_list(response.json())

    def _add_ohlc_params(
        self,
        params,
        frequency,
        aggregate_by_contract,
        min_lead_time,
        max_lead_time,
    ):
        if frequency is not None and aggregate_by_contract:
            raise ValidationError(
                reason=(
                    "'frequency' cannot be set when 'aggregate_by_contract' is True"
                ),
                parameter="frequency",
            )
        self._add_frequency(params, "frequency", frequency)
        self._add_bool(
            params,
            "aggregate-by-contract",
            aggregate_by_contract,
            required=True,
        )
        self._add_duration(
            params,
            "min-lead-time",
            min_lead_time,
            min=MIN_LEAD_TIME,
            max=MAX_LEAD_TIME,
        )
        self._add_duration(
            params,
            "max-lead-time",
            max_lead_time,
            min=MIN_LEAD_TIME,
            max=MAX_LEAD_TIME,
        )
        if (
            isinstance(min_lead_time, timedelta)
            and isinstance(max_lead_time, timedelta)
            and min_lead_time >= max_lead_time
        ):
            raise ValidationError(
                reason="Must be shorter than 'max_lead_time'",
                parameter="min_lead_time",
            )
