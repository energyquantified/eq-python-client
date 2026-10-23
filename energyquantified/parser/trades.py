from datetime import datetime
from typing import Any

from dateutil import parser
from pytz.tzinfo import BaseTzInfo

from energyquantified.metadata import Curve

from ..data import (
    TradeContract,
    TradeOHLC,
    TradeOHLCSeries,
    TradeOHLCSeriesList,
)
from ..exceptions import ParseException
from ..time import Frequency, to_timezone
from .metadata import parse_curve


def parse_trade_contract_list(
    json: list[dict[str, Any]], timezone: BaseTzInfo | None = None
) -> list[TradeContract]:
    """Parse a list of trade contract JSON objects."""
    if not isinstance(json, list):
        raise ParseException(
            f"Expected list of trade contract JSON objects, found: {type(json)}"
        )

    contracts: list[TradeContract] = []
    for index, item in enumerate(json):
        try:
            contracts.append(parse_trade_contract(item, timezone=timezone))
        except Exception as exc:
            raise ParseException(
                f"Failed to parse trade contract at index {index}: {item}"
            ) from exc
    return contracts


def parse_trade_contract(
    json: dict[str, Any], timezone: BaseTzInfo | None = None
) -> TradeContract:
    """Parse a trade contract JSON object."""
    period: Frequency = Frequency.by_tag(json.get("period"))
    delivery: datetime = parser.isoparse(json.get("delivery"))
    if timezone:
        delivery = to_timezone(delivery, tz=timezone)
    return TradeContract(period=period, delivery=delivery)


def parse_trade_ohlc_series_list(json: dict[str, Any]) -> TradeOHLCSeriesList:
    """
    Parse the trade OHLC response envelope into a list of trade OHLC series,
    one per delivery contract.
    """
    if not isinstance(json, dict):
        raise ParseException(
            f"Expected trade OHLC series JSON object, found: {type(json)}"
        )

    curve_json: dict[str, Any] | None = json.get("curve")
    curve: Curve | None = parse_curve(curve_json) if curve_json else None
    timezone: BaseTzInfo | None = curve.timezone if curve else None

    frequency_tag: str | None = json.get("frequency")
    frequency: Frequency | None = (
        Frequency.by_tag(frequency_tag) if frequency_tag else None
    )
    unit: str | None = json.get("unit")
    denominator: str | None = json.get("denominator")

    data: list[dict[str, Any]] | None = json.get("data")
    if data is None:
        data = []
    if not isinstance(data, list):
        raise ParseException(
            f"Expected list of trade OHLC series JSON objects, found: {type(data)}"
        )

    series: list[TradeOHLCSeries] = []
    for index, item in enumerate(data):
        try:
            series.append(
                _parse_trade_ohlc_series(
                    item,
                    curve=curve,
                    frequency=frequency,
                    unit=unit,
                    denominator=denominator,
                    timezone=timezone,
                )
            )
        except Exception as exc:
            raise ParseException(
                f"Failed to parse trade OHLC series at index {index}: {item}"
            ) from exc

    return TradeOHLCSeriesList(
        series,
        curve=curve,
        frequency=frequency,
        unit=unit,
        denominator=denominator,
    )


def _parse_trade_ohlc_series(
    json: dict[str, Any],
    curve: Curve | None = None,
    frequency: Frequency | None = None,
    unit: str | None = None,
    denominator: str | None = None,
    timezone: BaseTzInfo | None = None,
) -> TradeOHLCSeries:
    """Parse one contract's entry in the trade OHLC response envelope."""
    contract_json: dict[str, Any] | None = json.get("trade_contract")
    contract: TradeContract | None = (
        parse_trade_contract(contract_json, timezone=timezone)
        if contract_json
        else None
    )
    data: list[TradeOHLC] = _parse_trade_ohlc_data(json.get("data"), timezone=timezone)

    return TradeOHLCSeries(
        curve=curve,
        contract=contract,
        frequency=frequency,
        unit=unit,
        denominator=denominator,
        data=data,
    )


def _parse_trade_ohlc_data(
    json: list[dict[str, Any]], timezone: BaseTzInfo | None = None
) -> list[TradeOHLC]:
    if not json:
        return []

    data: list[TradeOHLC] = []
    for index, item in enumerate(json):
        try:
            traded_at: datetime = parser.isoparse(item.get("traded_at"))
            if timezone:
                traded_at = to_timezone(traded_at, tz=timezone)
            data.append(
                TradeOHLC(
                    traded_at=traded_at,
                    open=item.get("open"),
                    high=item.get("high"),
                    low=item.get("low"),
                    close=item.get("close"),
                    vwap=item.get("vwap"),
                    volume=item.get("volume"),
                    count=item.get("count"),
                )
            )
        except Exception as exc:
            raise ParseException(
                f"Failed to parse data[{index}] in trade OHLC JSON response: {item}"
            ) from exc
    return data
