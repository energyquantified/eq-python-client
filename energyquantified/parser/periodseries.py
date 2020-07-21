from dateutil import parser

from ..data import Period, CapacityPeriod, Periodseries
from ..exceptions import ParseException
from ..time import to_timezone
from .metadata import parse_curve, parse_instance, parse_resolution


def parse_periodseries_list(json):
    """
    Parse a JSON list-response from the API a list of Periodseries objects with
    Curve, Resolution and Instance.
    """
    if not isinstance(json, list):
        raise ParseException(
            f"Expected list of period-based series JSON objects, found: {type(json)}"
        )
    return [parse_periodseries(json_obj) for json_obj in json]


def parse_periodseries(json):
    """
    Parse a JSON response from the API into a Periodseries object with
    Curve, Resolution and Instance.
    """
    # Parse the Resolution
    resolution = json.get("resolution")
    if resolution:
        resolution = parse_resolution(resolution)
    # Parse the Curve
    curve = json.get("curve")
    if curve:
        curve = parse_curve(curve)
    # Parse the instance
    instance = json.get("instance")
    if instance:
        instance = parse_instance(instance, curve=curve)
    # Parse data
    data = _parse_data(json.get("data"), resolution=resolution)

    return Periodseries(
        curve=curve,
        resolution=resolution,
        instance=instance,
        data=data
    )


def _parse_data(json, resolution=None):
    """
    Parse the data[] part of the json response
    """
    # Empty time series
    if not json:
        return []
    # Look at the first element
    element = json[0]
    has_capacity = "capacity" in element
    if has_capacity:
        return _parse_value_capacity_data(json, resolution=resolution)
    else:
        return _parse_value_data(json, resolution=resolution)


def _parse_value_capacity_data(json, resolution=None):
    timezone = resolution.timezone

    data = []
    for element in json:
        begin = to_timezone(
            parser.isoparse(element.get("begin")),
            tz=timezone
        )
        end = to_timezone(
            parser.isoparse(element.get("end")),
            tz=timezone
        )
        value = element.get("v")
        installed = element.get("capacity")
        data.append(CapacityPeriod(begin, end, value, installed))

    return data


def _parse_value_data(json, resolution=None):
    timezone = resolution.timezone

    data = []
    for element in json:
        begin = to_timezone(
            parser.isoparse(element.get("begin")),
            tz=timezone
        )
        end = to_timezone(
            parser.isoparse(element.get("end")),
            tz=timezone
        )
        value = element.get("v")
        data.append(Period(begin, end, value))

    return data