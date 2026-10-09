from dataclasses import dataclass
from datetime import datetime

from energyquantified.metadata import Curve

from ..time import Frequency
from ..utils.pandas import (
    trade_ohlc_series_list_to_pandas_dataframe,
    trade_ohlc_series_to_pandas_dataframe,
)
from ..utils.polars import (
    trade_ohlc_series_list_to_polars_dataframe,
    trade_ohlc_series_to_polars_dataframe,
)

@dataclass(frozen=True)
class TradeContract:
    """
    A tradable delivery contract, identified by the length of its delivery
    interval (``period``) and the start of that interval (``delivery``).

    :param period: The length of the delivery interval
    :type period: Frequency
    :param delivery: The beginning of the delivery interval
    :type delivery: datetime
    """

    period: Frequency
    delivery: datetime

    def as_dataframe_column_header(self) -> str:
        """
        Get this contract in a format fitting for a ``pandas.DataFrame`` or
        a ``polars.DataFrame`` column header.

        :return: A contract column header for a data frame
        :rtype: str
        """
        return f"{self.period.tag} {self.delivery.isoformat(sep=' ')}"

    def __str__(self):
        return (
            f"<TradeContract: period={self.period}, "
            f"delivery={self.delivery.isoformat(sep=' ')}>"
        )

    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class TradeOHLC:
    """
    OHLC statistics for the trades of one contract within one bucket of
    trading time.

    ``traded_at`` is the beginning of the trading-time bucket. It is not the
    contract's delivery time.
    """

    traded_at: datetime
    open: float
    high: float
    low: float
    close: float
    vwap: float
    volume: float
    count: int

    def __str__(self):
        return (
            f"<TradeOHLC: traded_at={self.traded_at.isoformat(sep=' ')}, "
            f"open={self.open}, high={self.high}, low={self.low}, "
            f"close={self.close}, vwap={self.vwap}, volume={self.volume}, "
            f"count={self.count}>"
        )

    def __repr__(self):
        return self.__str__()


class TradeOHLCSeries:
    """
    A series of OHLC values for one trade contract.

    :param curve: The curve holding this series
    :type curve: Curve, optional
    :param contract: The delivery contract these values were traded for
    :type contract: TradeContract, optional
    :param frequency: The frequency of the trading-time buckets
    :type frequency: Frequency, optional
    :param unit: The unit of the price fields
    :type unit: str, optional
    :param denominator: The denominator of the price fields
    :type denominator: str, optional
    :param data: The OHLC values
    :type data: list[TradeOHLC], optional
    """

    def __init__(
        self,
        curve: Curve | None = None,
        contract: TradeContract | None = None,
        frequency: Frequency | None = None,
        unit: str | None = None,
        denominator: str | None = None,
        data: list[TradeOHLC] | None = None,
    ):
        self.curve = curve
        self.contract = contract
        self.frequency = frequency
        self.unit = unit
        self.denominator = denominator
        self.data = data or []

    @property
    def name(self) -> str | None:
        return self.curve.name if self.curve else None

    def has_data(self) -> bool:
        return bool(self.data)

    def begin(self) -> datetime:
        if not self.data:
            raise ValueError("TradeOHLCSeries has no values")
        return self.data[0].traded_at

    def end(self) -> datetime:
        if not self.data:
            raise ValueError("TradeOHLCSeries has no values")
        return self.frequency.shift(self.data[-1].traded_at, 1)

    def to_pandas_dataframe(self):
        """
        Convert this TradeOHLCSeries to a ``pandas.DataFrame`` with one row per
        trading-time bucket and columns for the contract (``period`` and
        ``delivery``), the ``traded_at`` bucket, and the OHLC fields.

        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return trade_ohlc_series_to_pandas_dataframe(self)

    def to_pd_df(self):
        """
        Alias for :meth:`TradeOHLCSeries.to_pandas_dataframe`.

        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return self.to_pandas_dataframe()

    def to_polars_dataframe(self):
        """
        Convert this TradeOHLCSeries to a ``polars.DataFrame`` with one row per
        trading-time bucket and columns for the contract (``period`` and
        ``delivery``), the ``traded_at`` bucket, and the OHLC fields.

        :return: A DataFrame
        :rtype: polars.DataFrame
        :raises ImportError: When polars is not installed on the system
        """
        return trade_ohlc_series_to_polars_dataframe(self)

    def to_pl_df(self):
        """
        Alias for :meth:`TradeOHLCSeries.to_polars_dataframe`.

        :return: A DataFrame
        :rtype: polars.DataFrame
        :raises ImportError: When polars is not installed on the system
        """
        return self.to_polars_dataframe()

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item: int | slice):
        return self.data[item]

    def __str__(self):
        parts = [f"frequency={self.frequency}"]
        if self.curve:
            parts.append(f'curve="{self.curve}"')
        if self.contract:
            parts.append(f"contract={self.contract}")
        if self.unit:
            parts.append(f'unit="{self.unit}"')
        if self.denominator:
            parts.append(f'denominator="{self.denominator}"')
        parts.append(f"items={len(self.data)}")
        return f"<TradeOHLCSeries: {', '.join(parts)}>"

    def __repr__(self):
        return self.__str__()


class TradeOHLCSeriesList(list):
    """
    An immutable collection of trade OHLC series, one per delivery contract.

    The curve, frequency, unit, and denominator are shared by every series in
    the list, as the API returns them once for the whole response.

    :param elements: The trade OHLC series
    :type elements: iterable
    :param curve: The curve holding these series
    :type curve: Curve, optional
    :param frequency: The frequency of the trading-time buckets
    :type frequency: Frequency, optional
    :param unit: The unit of the price fields
    :type unit: str, optional
    :param denominator: The denominator of the price fields
    :type denominator: str, optional
    """

    def __init__(
        self,
        elements=(),
        curve: Curve | None = None,
        frequency: Frequency | None = None,
        unit: str | None = None,
        denominator: str | None = None,
    ):
        super().__init__(elements)
        # --- Public members ---
        #: The curve holding these trade OHLC series
        self.curve = curve
        #: The frequency of the trading-time buckets
        self.frequency = frequency
        #: The unit of the price fields
        self.unit = unit
        #: The denominator of the price fields
        self.denominator = denominator

    def __str__(self):
        parts = [f"frequency={self.frequency}"]
        if self.curve:
            parts.append(f'curve="{self.curve}"')
        if self.unit:
            parts.append(f'unit="{self.unit}"')
        if self.denominator:
            parts.append(f'denominator="{self.denominator}"')
        parts.append(f"items={len(self)}")
        return f"<TradeOHLCSeriesList: {', '.join(parts)}>"

    def __repr__(self):
        return self.__str__()

    def to_pandas_dataframe(self):
        """
        Convert this TradeOHLCSeriesList to a ``pandas.DataFrame`` with one row
        per contract and trading-time bucket and columns for the contract
        (``period`` and ``delivery``), the ``traded_at`` bucket, and the OHLC
        fields.

        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return trade_ohlc_series_list_to_pandas_dataframe(self)

    def to_pd_df(self):
        """
        Alias for :meth:`TradeOHLCSeriesList.to_pandas_dataframe`.

        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return self.to_pandas_dataframe()

    def to_polars_dataframe(self):
        """
        Convert this TradeOHLCSeriesList to a ``polars.DataFrame`` with one row
        per contract and trading-time bucket and columns for the contract
        (``period`` and ``delivery``), the ``traded_at`` bucket, and the OHLC
        fields.

        :return: A DataFrame
        :rtype: polars.DataFrame
        :raises ImportError: When polars is not installed on the system
        """
        return trade_ohlc_series_list_to_polars_dataframe(self)

    def to_pl_df(self):
        """
        Alias for :meth:`TradeOHLCSeriesList.to_polars_dataframe`.

        :return: A DataFrame
        :rtype: polars.DataFrame
        :raises ImportError: When polars is not installed on the system
        """
        return self.to_polars_dataframe()

    def append(self, value):
        raise NotImplementedError("TradeOHLCSeriesList does not support append")

    def extend(self, iterable):
        raise NotImplementedError("TradeOHLCSeriesList does not support extend")

    def insert(self, index, value):
        raise NotImplementedError("TradeOHLCSeriesList does not support insert")

    def remove(self, value):
        raise NotImplementedError("TradeOHLCSeriesList does not support remove")

    def pop(self, index=-1):
        raise NotImplementedError("TradeOHLCSeriesList does not support pop")

    def clear(self):
        raise NotImplementedError("TradeOHLCSeriesList does not support clear")

    def __setitem__(self, key, value):
        raise NotImplementedError("TradeOHLCSeriesList does not support __setitem__")

    def __delitem__(self, key):
        raise NotImplementedError("TradeOHLCSeriesList does not support __delitem__")

    def __add__(self, rhs):
        raise NotImplementedError("TradeOHLCSeriesList does not support __add__")

    def __iadd__(self, rhs):
        raise NotImplementedError("TradeOHLCSeriesList does not support __iadd__")

    def __mul__(self, rhs):
        raise NotImplementedError("TradeOHLCSeriesList does not support multiply")

    def __rmul__(self, rhs):
        raise NotImplementedError("TradeOHLCSeriesList does not support multiply")

    def __imul__(self, rhs):
        raise NotImplementedError("TradeOHLCSeriesList does not support multiply")
