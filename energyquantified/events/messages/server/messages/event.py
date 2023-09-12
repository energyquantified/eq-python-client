from energyquantified.events.messages.server.base import _BaseServerMessage
from energyquantified.events import CurveUpdateEvent, EventType
from energyquantified.parser.metadata import parse_curve, parse_instance
from energyquantified.metadata import CurveType
from dateutil.parser import isoparse
from energyquantified.time import to_timezone


class ServerMessageCurveEvent(_BaseServerMessage):
    EVENT_KEY = "event"

    def __init__(self, event):
        self.event = event

    @staticmethod
    def from_message(json):
        event_json = json.get(ServerMessageCurveEvent.EVENT_KEY)
        if event_json is None:
            raise ValueError(
                f"Failed to parse StreamMessageEvent because "
                f"field '{ServerMessageCurveEvent.EVENT_KEY}' is missing"
            )
        event = _parse_curve_event(event_json)
        return ServerMessageCurveEvent(event)

def _parse_curve_event(json):
    # Curve
    curve = parse_curve(json["curve"])
    # Begin and end
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
        event_type=EventType.by_tag(json["event_type"]),
        begin=begin,
        end=end,
        instance=instance,
        num_values=json.get("values_changed"),
    )