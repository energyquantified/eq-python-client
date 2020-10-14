from dateutil import parser

from ..data import Product, OHLC, OHLCList
from ..exceptions import ParseException
from ..metadata import ContractPeriod
from .metadata import parse_curve, parse_contract


def parse_ohlc_response(json):
    # Parse curve
    curve = json.get("curve")
    if curve:
        curve = parse_curve(curve)
    # Parse OHLC objects
    data = parse_ohlc_list(json.get("data"))

    return OHLCList(data, curve=curve)


def parse_ohlc_list(json):
    # Parse data[], but keep track of data[index] to create a better exception
    data = []
    ohlc = None
    for index, item in enumerate(json):
        try:
            ohlc = parse_ohlc(item)
        except Exception as e:
            raise ParseException(
                f"Failed to parse data[{index}] in OHLC JSON response: {ohlc}"
            ) from e
        data.append(ohlc)
    return data


def parse_ohlc(json):
    product = parse_product(json.get("product"))
    return OHLC(
        product=product,
        open=json.get("open"),
        high=json.get("high"),
        low=json.get("low"),
        close=json.get("close"),
        settlement=json.get("settlement"),
        volume=json.get("volume"),
        open_interest=json.get("open_interest")
    )


def parse_product(json):
    traded = parser.isoparse(json.get("traded_at")).date()
    period = ContractPeriod.by_tag(json.get("period"))
    front = json.get("front")
    delivery = parser.isoparse(json.get("delivery")).date()
    return Product(
        traded=traded,
        period=period,
        front=front,
        delivery=delivery
    )
