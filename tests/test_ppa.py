import unittest
from datetime import date

import pytz

from energyquantified.api import PpaAPI
from energyquantified.data import PPA, PPAList, PPAProduct
from energyquantified.events.messages.server.messages.event import _parse_curve_event
from energyquantified.exceptions import ParseException, ValidationError
from energyquantified.metadata import (
    ContractStructure,
    Curve,
    CurveType,
    DataType,
    PPADuration,
    Technology,
)
from energyquantified.parser.ppa import parse_ppa_response
from energyquantified.time import Frequency

CURVE_NAME = "DE Power Purchase Agreement EUR/MWh QW01 PPA"
SAFE_CURVE_NAME = "DE%20Power%20Purchase%20Agreement%20EUR%2FMWh%20QW01%20PPA"

CURVE_JSON = {
    "name": CURVE_NAME,
    "curve_type": "PPA",
    "area": "DE",
    "categories": ["Power", "Purchase", "Agreement"],
    "resolution": {"frequency": "P1D", "timezone": "CET"},
    "unit": "EUR",
    "denominator": "MWh",
    "data_type": "PPA",
    "source": "QW01",
    "commodity": "Power",
}

PPA_JSON = {
    "product": {
        "date": "2026-09-29",
        "technology": "wind_onshore",
        "contract_structure": "year",
        "delivery_begin": "2027-01-01",
        "duration": 10,
    },
    "price": 45.2,
}

RESPONSE_JSON = {
    "curve": CURVE_JSON,
    "unit": "EUR",
    "denominator": "MWh",
    "data": [PPA_JSON],
}


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


class PPAParserTest(unittest.TestCase):
    def test_parses_response(self):
        ppa_list = parse_ppa_response(RESPONSE_JSON)

        self.assertIsInstance(ppa_list, PPAList)
        self.assertEqual(ppa_list.curve.name, CURVE_NAME)
        self.assertEqual(ppa_list.curve.curve_type, CurveType.PPA)
        self.assertEqual(ppa_list.unit, "EUR")
        self.assertEqual(ppa_list.denominator, "MWh")
        self.assertEqual(
            list(ppa_list),
            [
                PPA(
                    product=PPAProduct(
                        date=date(2026, 9, 29),
                        technology=Technology.WIND_ONSHORE,
                        contract_structure=ContractStructure.YEARLY_BASELOAD,
                        delivery_begin=date(2027, 1, 1),
                        duration=PPADuration.TEN_YEARS,
                    ),
                    price=45.2,
                )
            ],
        )

    def test_str_and_repr(self):
        ppa_list = parse_ppa_response(RESPONSE_JSON)

        self.assertTrue(str(ppa_list).startswith('<PPAList: curve="'))
        self.assertIn("items=[<PPA: <PPAProduct: date=2026-09-29", str(ppa_list))
        self.assertTrue(repr(ppa_list).startswith("[<PPA: <PPAProduct:"))

    def test_parses_empty_response(self):
        ppa_list = parse_ppa_response({"curve": CURVE_JSON, "data": []})

        self.assertEqual(len(ppa_list), 0)

    def test_rejects_unknown_duration(self):
        bad_json = {**PPA_JSON, "product": {**PPA_JSON["product"], "duration": 7}}

        with self.assertRaises(ParseException):
            parse_ppa_response({"data": [bad_json]})


class PpaAPITest(unittest.TestCase):
    def setUp(self):
        self.curve = Curve(
            CURVE_NAME,
            curve_type=CurveType.PPA,
            frequency=Frequency.P1D,
            timezone=pytz.timezone("CET"),
            unit="EUR",
            denominator="MWh",
            data_type=DataType.PPA,
        )

    def test_load_sends_filters(self):
        client = Client([RESPONSE_JSON])
        api = PpaAPI(client)

        result = api.load(
            self.curve,
            begin=date(2026, 1, 1),
            end="2026-12-31",
            technology=[Technology.WIND_ONSHORE, "solar"],
            contract_structure=["year", ContractStructure.MONTHLY_BASELOAD],
            delivery_begin=date(2027, 1, 1),
            duration=[PPADuration.FIVE_YEARS, 10],
            unit="USD",
        )

        self.assertIsInstance(result, PPAList)
        self.assertEqual(
            client._session.requests[0],
            (
                f"/ppa/{SAFE_CURVE_NAME}/",
                {
                    "begin": date(2026, 1, 1),
                    "end": "2026-12-31",
                    "technology": ["wind_onshore", "solar"],
                    "contract-structure": ["year", "month"],
                    "delivery-begin": date(2027, 1, 1),
                    "duration": [5, 10],
                    "unit": "USD",
                },
            ),
        )

    def test_load_accepts_single_filter_values(self):
        client = Client([RESPONSE_JSON])
        api = PpaAPI(client)

        api.load(
            CURVE_NAME,
            begin="2026-01-01",
            end="2026-12-31",
            technology="WIND_OFFSHORE",
            contract_structure=ContractStructure.PROXY,
            duration=15,
        )

        _, params = client._session.requests[0]
        self.assertEqual(params["technology"], ["wind_offshore"])
        self.assertEqual(params["contract-structure"], ["proxy"])
        self.assertEqual(params["duration"], [15])

    def test_latest(self):
        client = Client([RESPONSE_JSON, RESPONSE_JSON])
        api = PpaAPI(client)

        api.latest(self.curve)
        api.latest(self.curve, date="2026-09-29", technology=Technology.SOLAR)

        self.assertEqual(
            client._session.requests,
            [
                (f"/ppa/{SAFE_CURVE_NAME}/latest/", {}),
                (
                    f"/ppa/{SAFE_CURVE_NAME}/latest/",
                    {"date": "2026-09-29", "technology": ["solar"]},
                ),
            ],
        )

    def test_rejects_invalid_parameters(self):
        api = PpaAPI(Client([]))

        # 'begin' and 'end' are required
        with self.assertRaises(ValidationError):
            api.load(self.curve, end="2026-12-31")

        # Only PPA curves are supported
        ohlc_curve = Curve("OHLC curve", curve_type=CurveType.OHLC)
        with self.assertRaises(ValidationError):
            api.load(ohlc_curve, begin="2026-01-01", end="2026-12-31")

        # Unknown technology
        with self.assertRaises(ValidationError):
            api.latest(self.curve, technology="hydro")

        # Unknown contract structure
        with self.assertRaises(ValidationError):
            api.latest(self.curve, contract_structure="quarter")

        # Unsupported duration
        with self.assertRaises(ValidationError):
            api.latest(self.curve, duration=7)

        # Durations are given in years, not as strings
        with self.assertRaises(ValidationError):
            api.latest(self.curve, duration="10")


class PPAEventTest(unittest.TestCase):
    EVENT_JSON = {
        "id": "1759653600000-0",
        "event_type": "CURVE_UPDATE",
        "curve": CURVE_JSON,
        "begin": "2026-09-29T00:00:00Z",
        "end": "2026-09-30T00:00:00Z",
        "values_changed": 1,
    }

    def test_load_data_loads_quote_dates(self):
        event = _parse_curve_event(self.EVENT_JSON)

        class EQ:
            ppa = PpaAPI(Client([RESPONSE_JSON]))

        result = event.load_data(EQ())

        self.assertIsInstance(result, PPAList)
        url, params = EQ.ppa._client._session.requests[0]
        self.assertEqual(url, f"/ppa/{SAFE_CURVE_NAME}/")
        self.assertEqual(params["begin"], date(2026, 9, 29))
        self.assertEqual(params["end"], date(2026, 9, 30))


class PPADataFrameTest(unittest.TestCase):
    def test_to_pandas_dataframe(self):
        try:
            import pandas  # noqa: F401
        except ImportError:
            self.skipTest("pandas is not installed")

        df = parse_ppa_response(RESPONSE_JSON).to_pandas_dataframe()

        self.assertEqual(
            list(df.columns),
            [
                "date",
                "technology",
                "contract_structure",
                "delivery_begin",
                "duration",
                "price",
            ],
        )
        self.assertEqual(
            df.iloc[0].to_dict(),
            {
                "date": date(2026, 9, 29),
                "technology": "wind_onshore",
                "contract_structure": "year",
                "delivery_begin": date(2027, 1, 1),
                "duration": 10,
                "price": 45.2,
            },
        )

    def test_to_polars_dataframe(self):
        try:
            import polars  # noqa: F401
        except ImportError:
            self.skipTest("polars is not installed")

        df = parse_ppa_response(RESPONSE_JSON).to_polars_dataframe()

        self.assertEqual(
            df.to_dicts(),
            [
                {
                    "date": date(2026, 9, 29),
                    "technology": "wind_onshore",
                    "contract_structure": "year",
                    "delivery_begin": date(2027, 1, 1),
                    "duration": 10,
                    "price": 45.2,
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
