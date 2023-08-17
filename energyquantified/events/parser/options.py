from energyquantified.events import EventCurveOptions, EventFilterOptions

def _parse_event_options(json):
    # Event type
    curve_names = json.get("curve_names")
    # Either EventCurveOptions or EventFilterOptions
    if curve_names is not None:
        return _parse_curve_options(json, curve_names)
    return _parse_filter_options(json)

def _parse_curve_options(json, curve_names):
    # EventCurveOptions
    options = EventCurveOptions().set_curve_names(curve_names)
    return _parse_shared_options(json, options)

def _parse_filter_options(json):
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
    commodities = json.get("commodities")
    if commodities is not None:
        options.set_commodities(commodities)
    # Categories
    categories = json.get("categories")
    if categories is not None:
        options.set_categories(categories)
    # Exact categories
    exact_categories = json.get("exact_categories")
    if exact_categories is not None:
        options.set_exact_categories(exact_categories)
    return options


def _parse_shared_options(json, options):
    # Variables in both CurveOption and FilterOptions
    # Event type
    event_types = json.get("event_types")
    if event_types is not None:
        options.set_event_types(event_types)
    # Begin
    begin = json.get("begin")
    if begin is not None:
        options.set_begin(begin)
    # End
    end = json.get("end")
    if end is not None:
        options.set_end(end)
    return options