from dataclasses import dataclass
from enum import Enum
from typing import Optional
from energyquantified.events import CurveUpdateEvent


_stream_message_lookup = {}

class StreamMessageType(Enum):
    FIELD_NAME = "type"

    MESSAGE = ("message")
    ERROR = ("error")
    CURVES_EVENT = ("curves.event")
    CURVES_SUBSCRIBE = ("curves.subscribe")
    CURVES_FILTERS = ("curves.filters")

    def __init__(self, tag, model):
        self.tag = tag
        self.model = model
        _stream_message_lookup[tag.lower()] = self

    # @staticmethod # TODO move parser to parser class instead?
    # def from_json(json_obj):
    #     val = json_obj.get(StreamMessageType.FIELD_NAME)
    #     if val is None:
    #         raise ValueError("")
    #     raise ValueError()

    @staticmethod
    def is_valid_tag(tag):
        return tag.lower() in _stream_message_lookup

    @staticmethod
    def by_tag(tag):
        return _stream_message_lookup[tag.lower()]

# class StreamMessage:
#     class Field(Enum):
#         MESSAGE_TYPE = ("type",
#                         [
#                             StreamMessageType.MESSAGE,
#                             StreamMessageType.ERROR,
#                             StreamMessageType.CURVES_EVENT,
#                             StreamMessageType.CURVES_SUBSCRIBE,
#                             StreamMessageType.CURVES_FILTERS,
#                          ])
#         # REQUEST_ID = ("request_id", # Only if response
#         #               [
                          
#         #               ])

#         def __init__(self, key, values):
#             self.key = key
#             self.values = values

class StreamMessage:
    def __init__(self):
        pass

    @classmethod
    def from_json(cls):
        raise NotImplementedError

class StreamMessageMessage(StreamMessage):
    MESSAGE: str

@dataclass(frozen=True)
class StreamMessageEvent(StreamMessage):
    EVENT: CurveUpdateEvent

@dataclass(frozen=True)
class StreamMessageResponse(StreamMessage):
    STATUS: lambda x: True if isinstance(x, str) and x.lower() == "ok" else False

class StreamMessageResponseCurvesSubscribe(StreamMessageResponse):
    def __init__(self):
        pass

# @dataclass(frozen=True)
# class StreamMessage:
#     TYPE: str

#     @classmethod
#     def from_json(cls):
#         raise NotImplementedError

# @dataclass(frozen=True)
# class StreamMessageMessage(StreamMessage):
#     MESSAGE: str

# @dataclass(frozen=True)
# class StreamMessageEvent(StreamMessage):
#     EVENT: CurveUpdateEvent

# @dataclass(frozen=True)
# class StreamMessageResponse(StreamMessage):
#     STATUS: lambda x: True if isinstance(x, str) and x.lower() == "ok" else False
#     DATA:

# @dataclass(frozen=True)
# class StreamMessageResponseCurvesSubscribe(StreamMessageResponse):
#     pass


# class StreamMessage:
#     class Fields:
#         TYPE = "123"

# class StreamMessageMessage:
#     pass

# @dataclass(frozen=True)
# class StreamMessage:
#     TYPE: str

# class StreamMessage:
#     pass

# @dataclass(frozen=True)
# class StreamMessageResponse:
#     TYPE: str 
#     @staticmethod
#     def from_json(json: str):
#         raise NotImplementedError
       
# @dataclass(frozen=True)
# class StreamMessageResponse:
#     def __init__(self, status, data=None, errors=None):
#         self.type = "" # TODO
#         if True:
#             self.data = self._parse_data(data)
#         else:
#             self.errors = errors

#     def _parse_data(self, data):
#         return data
    

        
