import unittest
import warnings

import pytz

from energyquantified.api import MetadataAPI
from energyquantified.metadata import (
    Area,
    CurveType,
    DataType,
    PlaceType,
    SubscriptionCollectionPerm,
)
from energyquantified.time import Frequency

SUBSCRIPTION_JSON = {
    "access": "PAYING",
    "type": "COLLECTION",
    "label": "My collection",
    "collection": "my-collection",
    "collection_perms": "RW",
}


def place_json(name, **overrides):
    json = {
        "type": "PRODUCER",
        "key": name.lower().replace(" ", "-"),
        "name": name,
        "unit": None,
        "fuels": ["Wind"],
        "location": [52.5, 13.4],
        "areas": ["DE"],
        "children": [],
        "curves": [],
        "remit_units": [],
    }
    json.update(overrides)
    return json


def curve_json(name, **overrides):
    json = {
        "name": name,
        "curve_type": "INSTANCE",
        "instance_issued_timezone": "CET",
        "area": "DE",
        "area_sink": "FR",
        "place": place_json("Wind Farm"),
        "categories": ["Exchange", "Forecast"],
        "resolution": {"frequency": "PT1H", "timezone": "CET"},
        "unit": "MW",
        "denominator": None,
        "data_type": "FORECAST",
        "source": "EC",
        "commodity": "Power",
        "subscription": SUBSCRIPTION_JSON,
    }
    json.update(overrides)
    return json


# Curve fields with a value unknown to this client version:
# (field, JSON overrides, unknown value)
UNKNOWN_CURVE_VALUES = [
    ("curve_type", {"curve_type": "NEW_CURVE_TYPE"}, "NEW_CURVE_TYPE"),
    (
        "instance_issued_timezone",
        {"instance_issued_timezone": "New/Zone"},
        "New/Zone",
    ),
    ("area", {"area": "NEW_AREA"}, "NEW_AREA"),
    ("area_sink", {"area_sink": "NEW_AREA"}, "NEW_AREA"),
    (
        "place.type",
        {"place": place_json("Wind Farm", type="NEW_PLACE_TYPE")},
        "NEW_PLACE_TYPE",
    ),
    (
        "place.areas",
        {"place": place_json("Wind Farm", areas=["DE", "NEW_AREA"])},
        "NEW_AREA",
    ),
    (
        "resolution.frequency",
        {"resolution": {"frequency": "P2W", "timezone": "CET"}},
        "P2W",
    ),
    (
        "resolution.timezone",
        {"resolution": {"frequency": "PT1H", "timezone": "New/Zone"}},
        "New/Zone",
    ),
    ("data_type", {"data_type": "NEW_DATA_TYPE"}, "NEW_DATA_TYPE"),
    (
        "subscription.access",
        {"subscription": {**SUBSCRIPTION_JSON, "access": "NEW_ACCESS"}},
        "NEW_ACCESS",
    ),
    (
        "subscription.type",
        {"subscription": {**SUBSCRIPTION_JSON, "type": "NEW_TYPE"}},
        "NEW_TYPE",
    ),
    (
        "subscription.collection_perms",
        {"subscription": {**SUBSCRIPTION_JSON, "collection_perms": "X"}},
        "X",
    ),
]

# Place fields with a value unknown to this client version:
# (field, JSON overrides, unknown value)
UNKNOWN_PLACE_VALUES = [
    ("type", {"type": "NEW_PLACE_TYPE"}, "NEW_PLACE_TYPE"),
    ("areas", {"areas": ["DE", "NEW_AREA"]}, "NEW_AREA"),
]


class Response:
    def __init__(self, json, headers):
        self._json = json
        self.headers = headers
        self.status_code = 200

    def json(self):
        return self._json


class Session:
    def __init__(self, response):
        self.response = response

    def get(self, url, params=None):
        return self.response


class Client:
    def __init__(self, response):
        self._session = Session(response)


def page_response(items):
    return Response(
        items,
        headers={
            "X-Current-Page": "1",
            "X-Page-Size": "50",
            "X-First-Page": "1",
            "X-Last-Page": "1",
            "X-Total-Items": str(len(items)),
        },
    )


class SkipInvalidTestCase(unittest.TestCase):
    def assertSkipped(self, caught, kind, name, unknown_value):
        self.assertEqual(len(caught), 1)
        message = str(caught[0].message)
        self.assertIn(f"Skipping {kind} '{name}'", message)
        self.assertIn(unknown_value.lower(), message.lower())


class CurvesSearchTest(SkipInvalidTestCase):
    def test_parses_curves(self):
        api = MetadataAPI(Client(page_response([curve_json("Curve A")])))

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            page = api.curves()

        self.assertEqual(len(page), 1)
        curve = page[0]
        self.assertEqual(curve.curve_type, CurveType.INSTANCE)
        self.assertEqual(curve.instance_issued_timezone, pytz.timezone("CET"))
        self.assertEqual(curve.area, Area.DE)
        self.assertEqual(curve.area_sink, Area.FR)
        self.assertEqual(curve.place.kind, PlaceType.PRODUCER)
        self.assertEqual(curve.frequency, Frequency.PT1H)
        self.assertEqual(curve.data_type, DataType.FORECAST)
        self.assertEqual(
            curve.subscription.collection_perms, SubscriptionCollectionPerm.RW
        )

    def test_skips_curves_with_unknown_values(self):
        for field, overrides, unknown_value in UNKNOWN_CURVE_VALUES:
            with self.subTest(field=field):
                api = MetadataAPI(Client(page_response([
                    curve_json("Curve A"),
                    curve_json("Curve B", **overrides),
                    curve_json("Curve C"),
                ])))

                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    page = api.curves()

                self.assertEqual([c.name for c in page], ["Curve A", "Curve C"])
                self.assertEqual(page.total_items, 3)
                self.assertSkipped(caught, "curve", "Curve B", unknown_value)

    def test_raises_on_malformed_curves(self):
        malformed = curve_json("Curve A")
        del malformed["resolution"]
        api = MetadataAPI(Client(page_response([malformed])))

        with self.assertRaises(AttributeError):
            api.curves()


class PlacesSearchTest(SkipInvalidTestCase):
    def test_parses_places(self):
        api = MetadataAPI(Client(page_response([
            place_json(
                "Wind Farm",
                children=[place_json("Turbine 1")],
                curves=[curve_json("Curve A")],
            ),
        ])))

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            page = api.places()

        self.assertEqual(len(page), 1)
        place = page[0]
        self.assertEqual(place.kind, PlaceType.PRODUCER)
        self.assertEqual(place.areas, [Area.DE])
        self.assertEqual([p.name for p in place.children], ["Turbine 1"])
        self.assertEqual([c.name for c in place.curves], ["Curve A"])

    def test_skips_places_with_unknown_values(self):
        for field, overrides, unknown_value in UNKNOWN_PLACE_VALUES:
            with self.subTest(field=field):
                api = MetadataAPI(Client(page_response([
                    place_json("Place A"),
                    place_json("Place B", **overrides),
                    place_json("Place C"),
                ])))

                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    page = api.places()

                self.assertEqual([p.name for p in page], ["Place A", "Place C"])
                self.assertEqual(page.total_items, 3)
                self.assertSkipped(caught, "place", "Place B", unknown_value)

    def test_skips_child_places_with_unknown_values(self):
        for field, overrides, unknown_value in UNKNOWN_PLACE_VALUES:
            with self.subTest(field=field):
                api = MetadataAPI(Client(page_response([
                    place_json("Wind Farm", children=[
                        place_json("Turbine 1"),
                        place_json("Turbine 2", **overrides),
                    ]),
                ])))

                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    page = api.places()

                self.assertEqual([p.name for p in page], ["Wind Farm"])
                self.assertEqual(
                    [p.name for p in page[0].children], ["Turbine 1"]
                )
                self.assertSkipped(caught, "place", "Turbine 2", unknown_value)

    def test_skips_place_curves_with_unknown_values(self):
        for field, overrides, unknown_value in UNKNOWN_CURVE_VALUES:
            with self.subTest(field=field):
                api = MetadataAPI(Client(page_response([
                    place_json("Wind Farm", curves=[
                        curve_json("Curve A"),
                        curve_json("Curve B", **overrides),
                    ]),
                ])))

                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    page = api.places()

                self.assertEqual([p.name for p in page], ["Wind Farm"])
                self.assertEqual([c.name for c in page[0].curves], ["Curve A"])
                self.assertSkipped(caught, "curve", "Curve B", unknown_value)


if __name__ == "__main__":
    unittest.main()
