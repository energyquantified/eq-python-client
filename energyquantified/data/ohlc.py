from collections import namedtuple
from dataclasses import dataclass
from datetime import date
import enum

from .base import Series
from ..metadata import ContractPeriod, OHLCField
from ..time import Frequency



@dataclass(frozen=True)
class Product:
    """
    An energy product description with a trading date and the
    contract in detail.
    """
    traded: date
    period: ContractPeriod
    front: int
    delivery: date

    def __str__(self):
        return (
            f"<Product: traded={self.traded.isoformat()}, "
            f"period={self.period.name}, "
            f"front={self.front}, "
            f"delivery={self.delivery.isoformat()}>"
        )

    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class OHLC:
    """
    A summary for a trading day on a contract.
    """
    product: Product
    open: float
    high: float
    low: float
    close: float
    settlement: float
    volume: float
    open_interest: float

    def get_field(self, field):
        """
        Get an OHLC field from this object.

        :param field: A OHLC field
        :type field: OHLCField | str
        :raises ValueError: When the `field` parameter isn't a valid OHLC field
        :return: The value on the given OHLC field or None if it isn't set
        :rtype: float
        """
        if isinstance(field, str) and OHLCField.is_valid_tag(field):
            return getattr(self, field, default=None)
        elif isinstance(field, OHLCField):
            return getattr(self, field.tag, default=None)
        else:
            raise ValueError(f'Unknown field: {field}')

    def __str__(self):
        return (
            f"<OHLC: {self.product}, "
            f"open={self.open or ''}, "
            f"high={self.high or ''}, "
            f"low={self.low or ''}, "
            f"close={self.close or ''}, "
            f"settlement={self.settlement or ''}, "
            f"volume={self.volume or ''}, "
            f"open_interest={self.open_interest or ''}>"
        )

    def __repr__(self):
        return self.__str__()


class OHLCSeries(Series):
    """
    A series of OHLC data where a continuous front contract or a contract
    with a specified delivery date is provided.
    """

    def __init__(self, contract=None, data=None, *args, **kwargs):
        assert contract, "contract is required"
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


class OHLCList(list):
    """
    A collection of OHLC data provided in a list. Can contain all sorts
    of contracts (yearly, monthly, weekly etc.) for a specific market.
    """

    def __init__(self, elements, curve=None):
        super().__init__(elements)
        # --- Public members ---
        #: The current page
        self.curve = curve

    def __str__(self):
        return f"<OHLCData: curve=\"{self.curve}\", items={len(self)}>"

    def has_data(self):
        return bool(self.data)