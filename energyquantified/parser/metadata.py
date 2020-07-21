import pytz
from dateutil import parser

from ..exceptions import ParseException
from ..metadata import (
    Curve, Instance, Area, DataType, CurveType, Place, PlaceType
)
from ..time import Frequency, Resolution, UTC, to_timezone
from ..time.timezone import LOCAL_TZ


def parse_resolution(json):
    """
    Parse a JSON response from the server into a Resolution object.
    """
    frequency = Frequency.by_tag(json.get("frequency"))
    timezone = pytz.timezone(json.get("timezone"))
    return Resolution(frequency, timezone)


def parse_curve(json):
    """
    Parse a JSON response from the server into a Curve object.
    """
    name = json.get("name")
    curve_type = CurveType.by_tag(json.get("curve_type"))
    area = Area.by_tag(json.get("area"))
    categories = json.get("categories")
    resolution = json.get("resolution")
    frequency = Frequency.by_tag(resolution.get("frequency"))
    timezone = pytz.timezone(resolution.get("timezone"))
    unit = json.get("unit")
    denominator = json.get("denominator")
    data_type = DataType.by_tag(json.get("data_type"))
    source = json.get("source")

    area_sink = json.get("area_sink")
    if area_sink:
        area_sink = Area.by_tag(area_sink)

    place = json.get("place")
    if place:
        place = parse_place(place)

    instance_issued_timezone = json.get("instance_issued_timezone")
    if instance_issued_timezone:
        instance_issued_timezone = pytz.timezone(instance_issued_timezone)

    return Curve(
        name,
        curve_type=curve_type,
        instance_issued_timezone=instance_issued_timezone,
        area=area,
        area_sink=area_sink,
        place=place,
        frequency=frequency,
        timezone=timezone,
        categories=categories,
        unit=unit,
        denominator=denominator,
        data_type=data_type,
        source=source
    )


def parse_instance_list(json, curve=None):
    """
    Parse a JSON list-resonse from the server into a list of Instance objects.
    """
    if not isinstance(json, list):
        raise ParseException(
            f"Expected list of Instance JSON objects, found: {type(json)}"
        )
    return [parse_instance(json_obj) for json_obj in json]


def parse_instance(json, curve=None):
    """
    Parse a JSON resonse from the server into an Instance object.
    """
    # Find timezone
    if curve and curve.instance_issued_timezone:
        timezone = curve.instance_issued_timezone
    else:
        timezone = UTC
    # Parse the issue date
    issued = to_timezone(
        parser.isoparse(json.get("issued")),
        tz=timezone
    )
    tag = json.get("tag") or ""
    scenarios = json.get("scenarios") or None
    # Created and modified
    created = json.get("created") or None
    if created:
        created = to_timezone(
            parser.isoparse(created),
            tz=LOCAL_TZ
        )
    modified = json.get("modified") or None
    if modified:
        modified = to_timezone(
            parser.isoparse(modified),
            tz=LOCAL_TZ
        )
    return Instance(
        issued,
        tag,
        scenarios=scenarios,
        created=created,
        modified=modified
    )


def parse_place(json):
    """
    Parse a JSON resonse from the server into a Place object.
    """
    kind = PlaceType.by_tag(json.get("type"))
    key = json.get("key")
    name = json.get("name")
    unit = json.get("unit")
    fuels = json.get("fuels") or []
    location = json.get("location") or None

    area = json.get("area")
    if area:
        area = Area.by_tag(area)

    children = json.get("children")
    if children:
        children = [parse_place(p) for p in children]

    curves = json.get("curves")
    if curves:
        curves = [parse_curve(c) for c in curves]

    return Place(
        kind,
        key,
        name,
        unit=unit,
        fuels=fuels,
        area=area,
        location=location,
        children=children,
        curves=curves,
    )