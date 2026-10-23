import warnings

import pytz
from dateutil import parser

from ..exceptions import ParseException
from ..metadata import (
    Area,
    ContinuousContract,
    ContractPeriod,
    Curve,
    CurveType,
    DataType,
    Instance,
    OHLCField,
    Place,
    PlaceType,
    SpecificContract,
    Subscription,
    SubscriptionAccess,
    SubscriptionCollectionPerm,
    SubscriptionType,
)
from ..time import Frequency, Resolution, to_timezone
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
    commodity = json.get("commodity")

    area_sink = json.get("area_sink")
    if area_sink:
        area_sink = Area.by_tag(area_sink)

    place = json.get("place")
    if place:
        place = parse_place(place)

    instance_issued_timezone = json.get("instance_issued_timezone")
    if instance_issued_timezone:
        instance_issued_timezone = pytz.timezone(instance_issued_timezone)

    subscription = json.get("subscription")
    if subscription:
        subscription = parse_subscription(subscription)

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
        source=source,
        commodity=commodity,
        subscription=subscription,
    )


def parse_curves_skip_invalid(json):
    """
    Parse a JSON list of curves into Curve objects. Curves with values
    unknown to this client version (e.g. a new data type or frequency) are
    skipped with a warning instead of failing the whole list.
    """
    return _parse_list_skip_invalid(json, parse_curve, "curve")


def parse_places_skip_invalid(json):
    """
    Parse a JSON list of places into Place objects. Places with values
    unknown to this client version (e.g. a new place type) are skipped
    with a warning instead of failing the whole list.
    """
    return _parse_list_skip_invalid(json, parse_place, "place")


def _parse_list_skip_invalid(json, parse_func, kind):
    items = []
    for item_json in json:
        try:
            items.append(parse_func(item_json))
        except KeyError as e:
            # Lookups of unknown tags and timezones raise KeyError
            warnings.warn(
                f"Skipping {kind} '{item_json.get('name')}' because it could "
                f"not be parsed: {e!r}"
            )
    return items


def parse_instance_list(json, curve=None):
    """
    Parse a JSON list-response from the server into a list of Instance objects.
    """
    if not isinstance(json, list):
        raise ParseException(
            f"Expected list of Instance JSON objects, found: {type(json)}"
        )
    return [parse_instance(json_obj, curve=curve) for json_obj in json]


def parse_instance(json, curve=None):
    """
    Parse a JSON response from the server into an Instance object.
    """
    # Find timezone for issued
    issued = parser.isoparse(json.get("issued"))
    # Localize to issued zone if we have it (from curve)
    if curve and curve.instance_issued_timezone:
        issued = to_timezone(
            issued,
            tz=curve.instance_issued_timezone,
        )
    tag = json.get("tag") or ""
    scenarios = json.get("scenarios") or None
    # Find timezone for created and modified
    if curve and curve.timezone:
        curve_timezone = curve.timezone
    else:
        curve_timezone = LOCAL_TZ
    # Created and modified
    created = json.get("created") or None
    if created:
        created = to_timezone(parser.isoparse(created), tz=curve_timezone)
    modified = json.get("modified") or None
    if modified:
        modified = to_timezone(parser.isoparse(modified), tz=curve_timezone)
    return Instance(
        issued, tag, scenarios=scenarios, created=created, modified=modified
    )


def parse_place(json):
    """
    Parse a JSON response from the server into a Place object.
    """
    kind = PlaceType.by_tag(json.get("type"))
    key = json.get("key")
    name = json.get("name")
    unit = json.get("unit")
    fuels = json.get("fuels") or []
    location = json.get("location") or None
    remit_units = json.get("remit_units") or []

    areas = json.get("areas")
    if areas:
        areas = [Area.by_tag(a) for a in areas]
    else:
        areas = []

    children = json.get("children")
    if children:
        children = parse_places_skip_invalid(children)

    curves = json.get("curves")
    if curves:
        curves = parse_curves_skip_invalid(curves)

    return Place(
        kind,
        key,
        name,
        unit=unit,
        fuels=fuels,
        areas=areas,
        location=location,
        children=children,
        curves=curves,
        remit_units=remit_units,
    )


def parse_contract(json):
    contract_type = json.get("type")

    field = json.get("field")
    if field:
        field = OHLCField.by_tag(field)
    period = ContractPeriod.by_tag(json.get("period"))

    if contract_type == "CONTINUOUS":
        front = json.get("front")
        return ContinuousContract(field=field, period=period, front=front)

    if contract_type == "SPECIFIC":
        delivery = parser.isoparse(json.get("delivery")).date()
        return SpecificContract(field=field, period=period, delivery=delivery)

    raise ParseException(f"Unknown contract.type in JSON: {contract_type}")


def parse_subscription(json):
    """
    Parse a JSON response from the server into a Subscription object.
    """
    access = json.get("access")
    if access is not None:
        access = SubscriptionAccess.by_tag(access)
    stype = json.get("type")
    if stype is not None:
        stype = SubscriptionType.by_tag(stype)
    label = json.get("label")
    package = (
        json.get("package")
        if stype in (SubscriptionType.PACKAGE, SubscriptionType.PACKAGE_AREA)
        else None
    )
    area = json.get("area") if stype == SubscriptionType.PACKAGE_AREA else None
    collection = (
        json.get("collection") if stype == SubscriptionType.COLLECTION else None
    )
    collection_perms = (
        SubscriptionCollectionPerm.by_tag(json.get("collection_perms"))
        if stype == SubscriptionType.COLLECTION
        else None
    )

    return Subscription(
        access=access,
        subscription_type=stype,
        label=label,
        package=package,
        area=area,
        collection=collection,
        collection_perms=collection_perms,
    )
