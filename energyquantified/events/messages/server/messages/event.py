from energyquantified.events.messages.server.base import _BaseServerMessage
from energyquantified.parser.events import parse_curve_event

class ServerMessageCurveEvent(_BaseServerMessage):
    EVENT_KEY = "event"

    def __init__(self, event):
        self.event = event

    @staticmethod
    def from_message(json):
        event_json = json.get(ServerMessageCurveEvent.EVENT_KEY)
        if event_json is None:
            raise ValueError(
                f"Failed to parse StreamMessageEvent because field '{ServerMessageCurveEvent.EVENT_KEY}' "
                f"is missing"
            )
        event = parse_curve_event(event_json)
        return ServerMessageCurveEvent(event)