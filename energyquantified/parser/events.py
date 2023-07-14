from energyquantified.events import EventType, CurveUpdateEvent, EventCurveOptions, EventFilterOptions, EventFilters, SubscribeResponse
from energyquantified.time import to_timezone
from .metadata import parse_curve, parse_instance
from dateutil.parser import isoparse
import json

def parse_server_message(msg):
    # Load json
    


#  with self._messages_lock:
#             try:
#                 msg = json.loads(message)
#             except Exception as e:
#                 self._messages.put((MessageType.ERROR, f"Failed to parse message: {message}, exception: {e}"))
#                 return
#             if msg["type"].lower() == "curves.subscribe":
#                 self._handle_message_subscribe_curves(msg)
#                 return
#             if not MessageType.is_valid_tag(msg["type"]):
#                 self._messages.put((MessageType.ERROR, f"Unknown message type: {msg.get('type')}"))
#                 return
#             msg_type = MessageType.by_tag(msg["type"])
#             if msg_type == MessageType.CURVE_EVENT:
#                 if self._is_subscribed_curves.is_set():
#                     obj = parse_event(msg)
#                     self._update_last_id(obj.event_id)
#                     self._last_id_to_file(obj.event_id)
#             elif msg_type == MessageType.MESSAGE:
#                 obj = msg["message"]
#             elif msg_type == MessageType.ERROR:
#                 # TODO Can this ever happen?
#                 obj = msg
#             else:
#                 self._messages.put((MessageType.ERROR, f"Missing handler for MessageType {msg_type}"))
#                 return
#             self._messages.put((msg_type, obj))


def parse_event(json):
    # Curve
    curve = parse_curve(json["curve"])
    begin = json.get("begin")
    if begin is not None:
        begin = isoparse(begin)
        begin = to_timezone(begin, curve.timezone)
    end = json.get("end")
    if end is not None:
        end = isoparse(end)
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

def parse_subscribe_response(json):
    if json["status"].upper() == "OK":
        response = SubscribeResponse(
            True,
            filters=parse_filters(json["obj"]["filters"]),
            last_id=json["obj"]["last_id"],
        )
    else:
        response = SubscribeResponse(
            False,
            errors=json["errors"],
        )
    return response

def parse_filters(json):
    event_filters = EventFilters()
    last_id = json.get("last_id")
    if last_id is not None:
        event_filters.set_last_id(last_id)
    options = [parse_event_options(option) for option in json["filters"]]
    event_filters.set_options(options)
    return event_filters

def parse_event_options(json):
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