from dataclasses import dataclass
from datetime import date
import enum

from ..time import Frequency


_periods_lookup = {}

class ContractPeriod(enum.Enum):
    """
    Enumerator of contract periods available in for OHLC contracts
    in the API. The contract periods are:

     * ``YEAR`` – Yearly contract period
     * ``MDEC`` – December delivery (for ETS EUA contracts)
     * ``SEASON`` – Summer or Winter (typically for gas contracts)
     * ``QUARTER`` – Quarterly contract period
     * ``MONTH`` – Monthly contract period
     * ``WEEK`` – Weekly contract period
     * ``WEEKEND`` – Weekend contract period
     * ``DAY`` – Daily contract period
    """

    # Contract periods for OHLC data
    YEAR = ("year", Frequency.P1Y)
    MDEC = ("mdec", Frequency.P1Y)
    SEASON = ("season", Frequency.SEASON)
    QUARTER = ("quarter", Frequency.P3M)
    MONTH = ("month", Frequency.P1M)
    WEEK = ("week", Frequency.P1W)
    WEEKEND = ("weekend", Frequency.P1D)
    DAY = ("day", Frequency.P1D)

    def __init__(self, tag, frequency):
        self.tag = tag
        self.frequency = frequency
        _periods_lookup[self.tag.lower()] = self

    @staticmethod
    def by_tag(tag):
        """
        Look up contract periods by tag.

        :param tag: The tag to look up
        :type tag: str
        :return: A ContractPeriod for this tag
        :rtype: ContractPeriod
        """
        return _periods_lookup[tag.lower()]

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a contract period tag exists or not.

        :param tag: The tag to look up
        :type tag: str
        :return: True if the contract period tag exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _periods_lookup

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


_ohlcfield_lookup = {}

class OHLCField(enum.Enum):
    """
    A field in an OHLC object. Used to specify which field to load or
    to perform an operation on.

     * ``OPEN`` – Opening trade for the trading day
     * ``HIGH`` – Highest trade for the trading day
     * ``LOW`` – Lowest trade for the trading day
     * ``CLOSE`` – Closing trade for the trading day
     * ``SETTLEMENT`` – Settlement price for the trading day
     * ``VOLUME`` – Accumulated traded volume for the trading day
     * ``OPEN_INTEREST`` – Total volume of contracts that have
       been entered into and not yet liquidated by an offsetting
       transaction or fulfilled by delivery
    """

    OPEN = ("open",)
    HIGH = ("high",)
    LOW = ("low",)
    CLOSE = ("close",)
    SETTLEMENT = ("settlement",)
    VOLUME = ("volume",)
    OPEN_INTEREST = ("open_interest",)

    def __init__(self, tag):
        self.tag = tag
        _ohlcfield_lookup[tag.lower()] = self

    def get_value(self, ohlc):
        """
        Get the value from an OHLC object for this field.

        :param ohlc: An OHLC object
        :type ohlc: OHLC
        :return: The value for that given OHLC field
        :rtype: float
        """
        return getattr(ohlc, self.tag, default=None)

    @staticmethod
    def by_tag(tag):
        """
        Look up OHLC field by tag.

        :param tag: The tag to look up
        :type tag: str
        :return: An OHLCField for this tag
        :rtype: OHLCField
        """
        return _ohlcfield_lookup[tag.lower()]

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a OHLC field tag exists or not.

        :param tag: The tag to look up
        :type tag: str
        :return: True if the OHLC field tag exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _ohlcfield_lookup

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


@dataclass(frozen=True)
class ContinuousContract:
    """
    Metadata class for keeping track of which contract was queried. Continuous
    contracts are the rolling `N`-front contract – relative to its trading day.

    For instance, a contract with ``period=MONTH``, ``front=1`` is what you
    would typically call a front month contract. ``period=MONTH``, ``front=2``
    is the second closest front contract, and so forth.

    See also :py:class:`SpecificContract`.

    .. py:attribute:: field

        The field to have fetched from the OHLC objects (such as close,
        settlement, open, high, low, volume)

    .. py:attribute:: period

        The contract period (i.e. week, month, quarter)

    .. py:attribute:: front

        The front number (1 is the closest contract, 2 is the second closest,
        and so on)
    """
    period: ContractPeriod
    front: int
    field: OHLCField = None

    def is_continuous(self):
        """
        Check whether this contract instance is continuous.

        :return: True if continuous, otherwise False
        :rtype: bool
        """
        return True

    def is_specific(self):
        """
        Check whether this contract instance is specific.

        :return: True if specific, otherwise False
        :rtype: bool
        """
        return False

    def as_dataframe_column_header(self):
        """
        Create a string fitting for a column header in the a
        ``pandas.DataFrame``.

        :return: A DataFrame column header text for this contract
        :rtype: str
        """
        return f"{self.period.tag} front-{self.front} {self.field.tag}"

    def __str__(self):
        return (
            f"<ContinuousContract: "
            f"period={self.period.name}, "
            f"front={self.front}, "
            f"field={self.field.name if self.field else ''}>"
        )

    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class SpecificContract:
    """
    Metadata class for keeping track of which contract was queried. Specific
    contracts are contracts which goes to delivery on a specific date.

    For instance, a contract with ``period=MONTH``, ``delivery=2020-12-01``
    is the contract for delivery in December 2020.

    See also :py:class:`ContinuousContract`.

    .. py:attribute:: field

        The field to have fetched from the OHLC objects (such as close,
        settlement, open, high, low, volume)

    .. py:attribute:: period

        The contract period (i.e. week, month, quarter)

    .. py:attribute:: delivery

        The delivery date of the contract
    """
    period: ContractPeriod
    delivery: date
    field: OHLCField = None

    def is_continuous(self):
        """
        Check whether this contract instance is continuous.

        :return: True if continuous, otherwise False
        :rtype: bool
        """
        return False

    def is_specific(self):
        """
        Check whether this contract instance is specific.

        :return: True if specific, otherwise False
        :rtype: bool
        """
        return True

    def as_dataframe_column_header(self):
        """
        Create a string fitting for a column header in the a
        ``pandas.DataFrame``.

        :return: A DataFrame column header text for this contract
        :rtype: str
        """
        return f"{self.period.tag} {self.delivery.isoformat()} {self.field.tag}"

    def __str__(self):
        return (
            f"<SpecificContract: "
            f"period={self.period.name}, "
            f"delivery={self.delivery.isoformat()}, "
            f"field={self.field.name if self.field else ''}>"
        )

    def __repr__(self):
        return self.__str__()
