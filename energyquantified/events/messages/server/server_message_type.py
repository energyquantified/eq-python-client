from enum import Enum
from energyquantified.events.messages.server import (
    ServerMessageMessage,
    ServerMessageCurveEvent,
    ServerResponseCurvesFilters,
    ServerResponseCurvesSubscribe,
    ServerResponseError,
)

STREAM_MESSAGE_TYPE_FIELD = "type"

_server_message_type_lookup = {}

class ServerMessageType(Enum):
    # Messages
    MESSAGE = ("message", ServerMessageMessage)
    CURVES_EVENT = ("curves.event", ServerMessageCurveEvent)
    # Responses
    ERROR = ("error", ServerResponseError)
    CURVES_SUBSCRIBE = ("curves.subscribe", ServerResponseCurvesSubscribe)
    CURVES_FILTERS = ("curves.filters", ServerResponseCurvesFilters)

    def __init__(self, tag, model):
        self.tag = tag
        self.model = model
        _server_message_type_lookup[tag.lower()] = self

    def __str__(self):
        return self.tag

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def is_valid_tag(tag):
        return isinstance(tag, str) and tag.lower() in _server_message_type_lookup

    @staticmethod
    def by_tag(tag):
        return _server_message_type_lookup[tag.lower()]

    @staticmethod
    def tag_from_json(json):
        return json.get(STREAM_MESSAGE_TYPE_FIELD)