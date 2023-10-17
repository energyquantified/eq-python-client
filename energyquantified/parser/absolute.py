from dateutil import parser
from .metadata import (
    parse_curve,
    parse_instance,
    parse_resolution,
)
from ..metadata import (
    Aggregation,
    Filter,
)
from ..data import (
    AbsoluteResult,
    AbsoluteItem,
)
from ..time import to_timezone


def parse_absolute(json):
    """
    Parse a JSON response from the API into an AbsoluteResult object with
    Curve, Resolution, delivery, Filter, Aggregation, unit and AbsoluteItem's.
    """
    # Parse the Curve
    curve = json.get("curve")
    if curve:
        curve = parse_curve(curve)
    # Parse the Resolution
    resolution = json.get("resolution")
    if resolution:
        resolution = parse_resolution(resolution)
    # Parse the delivery
    delivery = to_timezone(
            parser.isoparse(json.get("delivery")),
            tz=resolution.timezone,
    )
    # Parse the Filter
    filters = json.get("filter")
    if filters is not None:
        filters = Filter.by_tag(filters)
    # Parse the Aggregation
    aggregation = json.get("aggregation")
    if aggregation is not None:
        aggregation = Aggregation.by_tag(aggregation)
    # Parse the unit
    unit = json.get("unit")
    # Parse data
    absolute_items = _parse_items(json.get("items"), curve=curve)
    return AbsoluteResult(
        curve=curve,
        resolution=resolution,
        delivery=delivery,
        filters=filters,
        aggregation=aggregation,
        unit=unit,
        items=absolute_items,
    )

def _parse_items(json, curve):
    """
    Parse the items[] part of the json response
    """
    items = []
    for element in json:
        # Parse the instance
        instance = parse_instance(element.get("instance"), curve=curve)
        value = element.get("v")
        items.append(AbsoluteItem(instance=instance, value=value))
    return items