import copy
import pickle
import unittest
from datetime import datetime, time, timedelta

import pytz

from energyquantified.api import TradesAPI, TradesOhlcAPI
from energyquantified.data import (
    TimeseriesList,
    TradeContract,
    TradeOHLC,
    TradeOHLCSeries,
    TradeOHLCSeriesList,
)
from energyquantified.events.messages.server.messages.event import _parse_curve_event
from energyquantified.exceptions import ValidationError
from energyquantified.metadata import Curve, CurveType, DataType, TradeOHLCField
from energyquantified.parser.metadata import parse_curve
from energyquantified.parser.trades import parse_trade_ohlc_series_list
from energyquantified.time import Frequency

CURVE_JSON = {
    "name": "NO Power EUR/MWh 1min Trade",
    "curve_type": "TRADES",
    "area": "NO",
    "categories": ["Power"],
    "resolution": {"frequency": "PT1M", "timezone": "Europe/Oslo"},
    "unit": "EUR",
    "denominator": "MWh",
    "data_type": "TRADES",
    "source": "Exchange",
    "commodity": "Power",
}

CONTRACT_JSON = {
    "period": "PT15M",
    "delivery": "2026-08-18 12:00+02:00",
}

OHLC_JSON = {
    "traded_at": "2026-08-18 10:00+02:00",
    "open": 10.0,
    "high": 14.0,
    "low": 9.0,
    "close": 13.0,
    "vwap": 12.5,
    "volume": 5.0,
    "count": 7,
}

OHLC_RESPONSE_JSON = {
    "curve": CURVE_JSON,
    "frequency": "PT1M",
    "unit": "EUR",
    "denominator": "MWh",
    "data": [
        {
            "trade_contract": CONTRACT_JSON,
            "data": [OHLC_JSON],
        }
    ],
}

TIMESERIES_RESPONSE_JSON = [
    {
        "curve": CURVE_JSON,
        "trade_contract": CONTRACT_JSON,
        "resolution": {"frequency": "PT1M", "timezone": "Europe/Oslo"},
        "unit": "EUR",
        "denominator": "MWh",
        "data": [
            {"d": "2026-08-18 10:00+02:00", "v": 12.5},
            {"d": "2026-08-18 10:01+02:00", "v": None},
        ],
    }
]


class Response:
    def __init__(self, json):
        self._json = json
        self.status_code = 200

    def json(self):
        return self._json


class Session:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.requests = []

    def get(self, url, params=None):
        self.requests.append((url, params))
        return Response(next(self.responses))


class Client:
    def __init__(self, responses):
        self._session = Session(responses)


class TradesAPITest(unittest.TestCase):
    def setUp(self):
        self.curve = Curve(
            CURVE_JSON["name"],
            curve_type=CurveType.TRADES,
            frequency=Frequency.PT1M,
            timezone=pytz.timezone("Europe/Oslo"),
            unit="EUR",
            denominator="MWh",
            data_type=DataType.TRADES,
        )

    def test_ohlc_operations_are_nested_under_ohlc(self):
        api = TradesAPI(Client([]))

        # OHLC data is served from /trades/{curve}/ohlc/, so it is grouped
        # under eq.trades.ohlc.*, leaving eq.trades.* free for the raw trade
        # endpoints at /trades/{curve}/.
        self.assertIsInstance(api.ohlc, TradesOhlcAPI)
        self.assertTrue(hasattr(api, "contracts"))
        self.assertFalse(hasattr(api, "load"))
        self.assertFalse(hasattr(api, "load_as_timeseries"))

    def test_contract_list(self):
        client = Client([[CONTRACT_JSON]])
        api = TradesAPI(client)
        begin = datetime.fromisoformat("2026-08-18T00:00:00+02:00")

        contracts = api.contracts(
            self.curve,
            begin=begin,
            end="2026-08-19 00:00:00+02:00",
            after_time_of_day=time(8),
            before_time_of_day="20:00:00",
            periods=[Frequency.PT15M, "PT30M"],
            exclude_periods=Frequency.PT1H,
        )

        self.assertEqual(len(contracts), 1)
        self.assertIsInstance(contracts[0], TradeContract)
        self.assertEqual(contracts[0].period, Frequency.PT15M)
        self.assertEqual(contracts[0].delivery.tzinfo.zone, "Europe/Oslo")
        self.assertEqual(
            client._session.requests[0],
            (
                "/trades/NO%20Power%20EUR%2FMWh%201min%20Trade/contracts/",
                {
                    "begin": begin,
                    "end": "2026-08-19 00:00:00+02:00",
                    "after-time-of-day": "08:00:00.000",
                    "before-time-of-day": "20:00:00",
                    "periods": ["PT15M", "PT30M"],
                    "exclude-periods": ["PT1H"],
                },
            ),
        )

    def test_load_parses_envelope_and_sends_aggregation(self):
        client = Client([OHLC_RESPONSE_JSON])
        api = TradesAPI(client)

        result = api.ohlc.load(
            self.curve,
            begin="2026-08-18",
            end="2026-08-19",
            frequency=Frequency.PT5M,
            min_lead_time=timedelta(minutes=15),
            max_lead_time=timedelta(hours=6),
            unit="NOK",
        )

        self.assertIsInstance(result, TradeOHLCSeriesList)
        self.assertEqual(result.curve.curve_type, CurveType.TRADES)
        self.assertEqual(result.frequency, Frequency.PT1M)
        self.assertEqual(result.unit, "EUR")
        self.assertEqual(result.denominator, "MWh")
        self.assertIsInstance(result[0], TradeOHLCSeries)
        self.assertIsInstance(result[0][0], TradeOHLC)
        self.assertEqual(result[0].contract.period, Frequency.PT15M)
        self.assertEqual(result[0].frequency, Frequency.PT1M)
        self.assertEqual(result[0][0].vwap, 12.5)
        self.assertEqual(
            client._session.requests[0],
            (
                "/trades/NO%20Power%20EUR%2FMWh%201min%20Trade/ohlc/",
                {
                    "begin": "2026-08-18",
                    "end": "2026-08-19",
                    "frequency": "PT5M",
                    "aggregate-by-contract": "false",
                    "min-lead-time": "PT15M",
                    "max-lead-time": "PT360M",
                    "unit": "NOK",
                },
            ),
        )

    def test_load_as_timeseries_builds_field_path(self):
        client = Client([TIMESERIES_RESPONSE_JSON])
        api = TradesAPI(client)

        result = api.ohlc.load_as_timeseries(
            self.curve,
            field=TradeOHLCField.VWAP,
            begin="2026-08-18",
            end="2026-08-19",
            aggregate_by_contract=True,
            fill="forward-fill",
        )

        self.assertIsInstance(result, TimeseriesList)
        self.assertEqual(result[0].trade_contract.period, Frequency.PT15M)
        self.assertEqual(
            result[0].trade_contract.delivery.tzinfo.zone, "Europe/Oslo"
        )
        self.assertEqual(result[0].data[0].value, 12.5)
        self.assertEqual(
            client._session.requests[0],
            (
                (
                    "/trades/NO%20Power%20EUR%2FMWh%201min%20Trade/ohlc/"
                    "timeseries/vwap/"
                ),
                {
                    "begin": "2026-08-18",
                    "end": "2026-08-19",
                    "aggregate-by-contract": "true",
                    "fill": "forward-fill",
                },
            ),
        )

    def test_rejects_invalid_parameters(self):
        api = TradesAPI(Client([]))

        # 'frequency' and 'aggregate_by_contract' are mutually exclusive
        with self.assertRaises(ValidationError):
            api.ohlc.load(
                self.curve,
                begin="2026-08-18",
                end="2026-08-19",
                frequency=Frequency.PT5M,
                aggregate_by_contract=True,
            )

        # Delivery periods must be PT15M, PT30M or PT1H
        with self.assertRaises(ValidationError):
            api.contracts(
                self.curve,
                begin="2026-08-18",
                end="2026-08-19",
                periods=Frequency.P1D,
            )

        # Lead times cannot be longer than 36 hours
        with self.assertRaises(ValidationError):
            api.ohlc.load(
                self.curve,
                begin="2026-08-18",
                end="2026-08-19",
                max_lead_time=timedelta(hours=48),
            )

        # Lead times must be a whole number of minutes
        with self.assertRaises(ValidationError):
            api.ohlc.load(
                self.curve,
                begin="2026-08-18",
                end="2026-08-19",
                min_lead_time=timedelta(seconds=90),
            )

        # 'min_lead_time' must be shorter than 'max_lead_time'
        with self.assertRaises(ValidationError):
            api.ohlc.load(
                self.curve,
                begin="2026-08-18",
                end="2026-08-19",
                min_lead_time=timedelta(hours=6),
                max_lead_time=timedelta(hours=1),
            )

        # The trade OHLC field must be a known field
        with self.assertRaises(ValidationError):
            api.ohlc.load_as_timeseries(
                self.curve,
                field="settlement",
                begin="2026-08-18",
                end="2026-08-19",
            )


class EQ:
    def __init__(self, responses):
        self.trades = TradesAPI(Client(responses))


class TradeEventTest(unittest.TestCase):
    EVENT_JSON = {
        "id": "1759653600000-0",
        "event_type": "CURVE_UPDATE",
        "curve": CURVE_JSON,
        "trade_contract": CONTRACT_JSON,
        "begin": "2026-08-18 10:00+02:00",
        "end": "2026-08-18 10:01+02:00",
        "values_changed": 1,
    }

    def test_parses_trade_contract(self):
        event = _parse_curve_event(self.EVENT_JSON)

        self.assertIsInstance(event.trade_contract, TradeContract)
        self.assertEqual(event.trade_contract.period, Frequency.PT15M)
        self.assertEqual(event.trade_contract.delivery.tzinfo.zone, "Europe/Oslo")

    def test_load_data_loads_the_event_contract(self):
        event = _parse_curve_event(self.EVENT_JSON)
        eq = EQ([OHLC_RESPONSE_JSON])

        result = event.load_data(eq)

        self.assertIsInstance(result, TradeOHLCSeriesList)
        url, params = eq.trades.ohlc._client._session.requests[0]
        self.assertEqual(url, "/trades/NO%20Power%20EUR%2FMWh%201min%20Trade/ohlc/")
        self.assertEqual(params["begin"].isoformat(), "2026-08-18T12:00:00+02:00")
        self.assertEqual(params["end"].isoformat(), "2026-08-18T12:15:00+02:00")
        self.assertEqual(params["periods"], ["PT15M"])

    def test_load_data_requires_trade_contract(self):
        event_json = {**self.EVENT_JSON}
        del event_json["trade_contract"]
        event = _parse_curve_event(event_json)

        with self.assertRaises(ValueError):
            event.load_data(EQ([]))


class TradeOHLCSeriesListTest(unittest.TestCase):
    EMPTY_RESPONSE_JSON = {"curve": CURVE_JSON, "data": []}

    def test_copy_and_pickle(self):
        series_list = parse_trade_ohlc_series_list(OHLC_RESPONSE_JSON)

        for copied in (
            copy.copy(series_list),
            copy.deepcopy(series_list),
            pickle.loads(pickle.dumps(series_list)),
        ):
            self.assertIsInstance(copied, TradeOHLCSeriesList)
            self.assertEqual(len(copied), 1)
            self.assertEqual(copied[0].data, series_list[0].data)
            self.assertEqual(copied.curve.name, CURVE_JSON["name"])
            self.assertEqual(copied.frequency, Frequency.PT1M)
            self.assertEqual(copied.unit, "EUR")
            self.assertEqual(copied.denominator, "MWh")

    def test_to_pandas_dataframe_dtypes(self):
        try:
            import pandas  # noqa: F401
        except ImportError:
            self.skipTest("pandas is not installed")

        # Whole-number prices must still give float columns
        int_ohlc_json = {**OHLC_JSON, "open": 10, "high": 14, "low": 9}
        int_response_json = {
            **OHLC_RESPONSE_JSON,
            "data": [{"trade_contract": CONTRACT_JSON, "data": [int_ohlc_json]}],
        }
        for json in (int_response_json, self.EMPTY_RESPONSE_JSON):
            series_list = parse_trade_ohlc_series_list(json)
            for df in (
                series_list.to_pandas_dataframe(),
                TradeOHLCSeries(curve=series_list.curve).to_pandas_dataframe(),
            ):
                dtypes = {column: str(dtype) for column, dtype in df.dtypes.items()}
                for column in ("delivery", "traded_at"):
                    self.assertEqual(str(df[column].dt.tz), "Europe/Oslo")
                for column in ("open", "high", "low", "close", "vwap", "volume"):
                    self.assertEqual(dtypes[column], "float64")
                self.assertEqual(dtypes["count"], "int64")

        df = parse_trade_ohlc_series_list(OHLC_RESPONSE_JSON).to_pandas_dataframe()
        self.assertEqual(df["delivery"][0].isoformat(), "2026-08-18T12:00:00+02:00")
        self.assertEqual(df["traded_at"][0].isoformat(), "2026-08-18T10:00:00+02:00")

    def test_to_polars_dataframe_uses_curve_timezone(self):
        try:
            import polars as pl
        except ImportError:
            self.skipTest("polars is not installed")

        for json in (OHLC_RESPONSE_JSON, self.EMPTY_RESPONSE_JSON):
            series_list = parse_trade_ohlc_series_list(json)
            for df in (
                series_list.to_polars_dataframe(),
                TradeOHLCSeries(curve=series_list.curve).to_polars_dataframe(),
            ):
                for column in ("delivery", "traded_at"):
                    self.assertEqual(
                        df.schema[column], pl.Datetime("us", "Europe/Oslo")
                    )

        # Empty and non-empty frames can be combined
        df = pl.concat(
            [
                parse_trade_ohlc_series_list(self.EMPTY_RESPONSE_JSON).to_pl_df(),
                parse_trade_ohlc_series_list(OHLC_RESPONSE_JSON).to_pl_df(),
            ]
        )
        self.assertEqual(df["delivery"][0].isoformat(), "2026-08-18T12:00:00+02:00")
        self.assertEqual(df["traded_at"][0].isoformat(), "2026-08-18T10:00:00+02:00")


class PPACurveTest(unittest.TestCase):
    def test_parses_ppa_curve(self):
        curve = parse_curve({**CURVE_JSON, "curve_type": "PPA", "data_type": "PPA"})

        self.assertEqual(curve.curve_type, CurveType.PPA)
        self.assertEqual(curve.data_type, DataType.PPA)


if __name__ == "__main__":
    unittest.main()
