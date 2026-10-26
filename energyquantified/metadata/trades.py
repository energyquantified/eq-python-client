import enum

_trade_ohlc_field_lookup = {}


class TradeOHLCField(enum.Enum):
    """
    A field in a TradeOHLC object. Used to specify which field to extract
    into a time series.

     * ``OPEN`` – The first traded price in the bucket
     * ``HIGH`` – The highest traded price in the bucket
     * ``LOW`` – The lowest traded price in the bucket
     * ``CLOSE`` – The last traded price in the bucket
     * ``VWAP`` – The volume-weighted average price in the bucket
     * ``VOLUME`` – The traded volume in the bucket
     * ``COUNT`` – The number of trades in the bucket
    """

    OPEN = ("open",)
    HIGH = ("high",)
    LOW = ("low",)
    CLOSE = ("close",)
    VWAP = ("vwap",)
    VOLUME = ("volume",)
    COUNT = ("count",)

    def __init__(self, tag):
        self.tag = tag
        _trade_ohlc_field_lookup[tag.lower()] = self

    def get_value(self, trade_ohlc):
        """
        Get the value from a TradeOHLC object for this field.

        :param trade_ohlc: A TradeOHLC object
        :type trade_ohlc: TradeOHLC
        :return: The value for that given trade OHLC field
        :rtype: float, int
        """
        return getattr(trade_ohlc, self.tag, None)

    @staticmethod
    def by_tag(tag):
        """
        Look up a trade OHLC field by tag.

        :param tag: The tag to look up
        :type tag: str
        :return: A TradeOHLCField for this tag
        :rtype: TradeOHLCField
        """
        return _trade_ohlc_field_lookup[tag.lower()]

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a trade OHLC field tag exists or not.

        :param tag: The tag to look up
        :type tag: str
        :return: True if the trade OHLC field tag exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _trade_ohlc_field_lookup

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
