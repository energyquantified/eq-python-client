from collections import namedtuple
import enum

from .base import Series
from ..time import Frequency


_periods_lookup = {}

class Period(enum.Enum):
    """
    Enumerator of contract periods available in for OHLC contracts
    in the API.
    """
    YEAR = ("year", Frequency.P1Y)
    MDEC = ("mdec", Frequency.P1Y)
    SEASON = ("season", Frequency.SEASON)
    QUARTER = ("quarter", Frequency.P3M)
    MONTH = ("month", Frequency.P1M)
    WEEK = ("week", Frequency.P1W)
    DAY = ("day", Frequency.P1D)

    def __init__(self, tag, frequency):
        self.tag = tag
        self.frequency = frequency
        _periods_lookup[self.tag.lower()] = self

    @staticmethod
    def by_tag(tag):
        return _periods_lookup[tag.lower()]


_Product = namedtuple("Product", ("traded", "period", "front", "delivery"))
class Product(_Product):
    pass


_OHLC = namedtuple("OHLC", (
    "product",
    "open",
    "high",
    "low",
    "close",
    "settlement",
    "volume",
    "open_interest"
))
class OHLC(_OHLC):
    pass


_ohlcfield_lookup = {}

class OHLCField(enum.Enum):
    """
    A field in an OHLC object. Used to specify which field to load or
    to perform an operation on.
    """
    OPEN = ("open",)
    HIGH = ("high",)
    LOW = ("low",)
    CLOSE = ("close",)
    settlement = ("settlement",)
    volume = ("volume",)
    OPEN_INTEREST = ("open_interest",)

    def __init__(self, tag):
        self.tag = tag
        _ohlcfield_lookup[tag.lower()] = self

    def get_value(self, ohlc):
        return getattr(ohlc, self.tag)

    @staticmethod
    def by_tag(tag):
        return _ohlcfield_lookup[tag.lower()]


class OHLCSeries(Series):
    """
    A series of OHLC data where a continuous front contract or a contract
    with a specified delivery date is provided.
    """

    def __init__(self, contract=None, data=None, *args, **kwargs):
        assert contract, "contract is required"  # TODO Check instanceof
        super().__init__(*args, **kwargs)
        self.contract = contract
        self.data = data or []

    def __str__(self):
        items = []
        items.append(f"curve=\"{self.curve}\"")
        items.append(f"contract=\"{self.contract}\"")
        if self.has_data():
            items.append(f"begin=\"{self.begin().isoformat()}\"")
            items.append(f"end=\"{self.end().isoformat()}\"")
        else:
            items.append("EMPTY")
        return f"<OHLCSeries: {', '.join(items)}>"

    def begin(self):
        if self.data:
            return self.data[0].date
        else:
            raise ValueError("OHLCSeries has no values")

    def end(self):
        if self.data:
            return self.resolution >> self.data[-1].date
        else:
            raise ValueError("OHLCSeries has no values")


class OHLCData:
    """
    A collection of OHLC data provided in a list. Can contain all sorts
    of contracts (yearly, monthly, weekly etc.) for a specific market.
    """

    def __init__(self, curve=None, data=None):
        self.curve = curve
        self.data = data or []

    def __str__(self):
        return f"<OHLCData: curve=\"{self.curve}\", items={len(self.data)}>"

    def __iter__(self):
        return (item for item in self.data or [])

    def has_data(self):
        return bool(self.data)