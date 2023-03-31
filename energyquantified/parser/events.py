from datetime import datetime

from energyquantified.events.events import EventType, CurveUpdateEvent
from energyquantified.events.event_options import EventCurveOptions, EventFilterOptions
from energyquantified.time import to_timezone
from .metadata import parse_curve, parse_instance

def parse_event(json):
    # Curve
    curve = parse_curve(json["curve"])
    begin = json.get("begin")
    if begin is not None:
        begin = datetime.fromisoformat(begin)
        begin = to_timezone(begin, curve.timezone)
    # End # TODO localize?
    end = json.get("end")
    if end is not None:
        end = datetime.fromisoformat(end)
        end = to_timezone(end, curve.timezone)
    # Instance
    instance = json.get("instance")
    if instance is not None:
        instance = parse_instance(instance, curve=curve)
    return CurveUpdateEvent(
        json["id"],
        curve,
        EventType.by_tag(json["event_type"]),
        begin=begin,
        end=end,
        instance=instance,
        num_values=json.get("values_changed"),
    )

def parse_event_options(json):
    print(f"JSON: {json}")
    # Event type
    curve_names = json.get("curve_names")
    # Either EventCurveOptions or EventFilterOptions
    if curve_names is not None:
        print("parse curve")
        return _parse_curve_options(json, curve_names)
    print("parse filter")
    return _parse_filter_options(json)

def _parse_curve_options(json, curve_names):
    print("start parse curve")
    # EventCurveOptions
    options = EventCurveOptions().set_curve_names(curve_names)
    return _parse_shared_options(json, options)

def _parse_filter_options(json):
    print("start parse filter")
    # EventFilterOptions
    options = EventFilterOptions()
    _parse_shared_options(json, options)
    # q  (freetext)
    q = json.get("q")
    if q is not None:
        options.set_q(q)
    # Areas
    areas = json.get("areas")
    if areas is not None:
        options.set_areas(areas)
    # Data types
    data_types = json.get("data_types")
    if data_types is not None:
        options.set_data_types(data_types)
    # Commodities
    commodities = json.get("commodity")
    if commodities is not None:
        options.set_commodities(commodities)
    # Categories
    categories = json.get("category")
    if categories is not None:
        options.set_categories(categories)
    # Exact categories
    exact_categories = json.get("exact_category")
    if exact_categories is not None:
        options.set_exact_categories(exact_categories)
    # Location
    location = json.get("location")
    if location is not None:
        options.set_location(location)
    return options
    

def _parse_shared_options(json, options):
    # Variables in both CurveOption and FilterOptions
    # Event type
    event_types = json.get("event_types")
    print(json)
    if event_types is not None:
        options.set_event_types(*event_types)
    # Begin
    begin = json.get("begin")
    if begin is not None:
        options.set_begin(begin)
    # End
    end = json.get("end")
    if end is not None:
        options.set_end(end)
    return options