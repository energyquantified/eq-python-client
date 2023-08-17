# from dataclasses import dataclass
# from enum import Enum
# from typing import Optional
# from energyquantified.events import CurveUpdateEvent, CurveEventFilters, EventCurveOptions, EventFilterOptions
# import uuid

# STREAM_MESSAGE_TYPE_FIELD = "type"



# _response_status_lookup = {}

# class _ResponseStatus(Enum):
#     OK = ("OK", "Ok")
#     ERROR = ("ERROR", "Error")

#     def __init__(self, tag, label):
#         self.tag = tag
#         self.label = label
#         _response_status_lookup[tag.lower()] = self
    
#     def __str__(self):
#         return self.name

#     def __repr__(self):
#         return self.__str__()

#     @staticmethod
#     def is_valid_tag(tag):
#         return isinstance(tag, str) and tag.lower() in _response_status_lookup

#     @staticmethod
#     def by_tag(tag):
#         return _response_status_lookup[tag.lower()]


# class StreamMessage:

#     @staticmethod
#     def from_message(_):
#         raise NotImplementedError

# class StreamMessageMessage(StreamMessage):
#     MESSAGE_KEY = "message"

#     def __init__(self, message):
#         self.message = message

#     @staticmethod
#     def from_message(json):
#         msg = json.get(StreamMessageMessage.MESSAGE_KEY)
#         if msg is None:
#             raise ValueError(f"Failed to parse StreamMessageMessage because field '{StreamMessageMessage.MESSAGE_KEY}' is missing")
#         return StreamMessageMessage(msg)


# class StreamMessageCurveEvent(StreamMessage):
#     EVENT_KEY = "event"

#     def __init__(self, event):
#         self.event = event

#     @staticmethod
#     def from_message(json):
#         event = json.get(StreamMessageCurveEvent.EVENT_KEY)
#         if event is None:
#             raise ValueError(f"Failed to parse StreamMessageEvent because field '{StreamMessageCurveEvent.EVENT_KEY}' is missing")
#         # TODO parse event
#         return StreamMessageCurveEvent(event)


# class _StreamMessageResponse(StreamMessage):
#     REQUEST_ID_KEY = "request_id"
#     STATUS_KEY = "status"
#     DATA_KEY = "data"
#     ERRORS_KEY = "errors"

#     def __init__(self):
#         self.request_id = None
#         self.status = None
#         self.data = None
#         self.errors = None

#     @staticmethod
#     def from_message(_):
#         raise NotImplementedError

#     def _parse_message(self, json):
#         self._set_status(json)
#         self._set_request_id(json)
#         if not self.status:
#             self._set_errors(json)
#         else:
#             self._set_data(json)

#     def _set_request_id(self, json):
#         # TODO how to handle if server failed to parse request_id (and how to know)
#         request_id = json.get(self.REQUEST_ID_KEY)
#         if request_id is None:
#             raise ValueError(f"Failed parsing StreamMessageResponse due to missing field '{self.REQUEST_ID_KEY}'")
#         self.request_id = uuid.UUID(request_id, version=4)

#     def _set_status(self, json):
#         status_tag = json.get(self.STATUS_KEY)
#         if not _ResponseStatus.is_valid_tag():
#             raise ValueError(f"Failed parsing StreamMessageResponse due to invalid status: {status_tag}")
#         self.status = _ResponseStatus.by_tag(status_tag) == _ResponseStatus.OK

#     def _set_data(self, _):
#         raise NotImplementedError

#     def _set_errors(self, json):
#         errors = json.get(self.ERRORS_KEY)
#         if errors is None:
#             raise ValueError(f"Failed parsing stream response due to missing field '{self.ERRORS_KEY}'")
#         if not isinstance(errors, list):
#             raise ValueError(f"Failed parsing stream response, expected field '{self.ERRORS_KEY}' to be a list")
#         if not all(isinstance(err, str) for err in errors):
#             raise ValueError(f"Failed parsing stream response, expected all elements in field '{self.ERRORS_KEY}' to be strings")
#         self.errors = errors

# class StreamMessageResponseError(_StreamMessageResponse):

#     @staticmethod
#     def from_message(json):
#         response_obj = StreamMessageResponseError()
#         response_obj._parse_message(json)

#     def _set_data(self, _):
#         raise ValueError(f"Data should not be set for message with type error")


# class StreamMessageResponseCurvesSubscribe(_StreamMessageResponse):
#     DATA_FILTERS_KEY = "filters"
#     DATA_LAST_ID_KEY = "last_id"

#     @staticmethod
#     def from_message(json):
#         response_obj = StreamMessageResponseCurvesSubscribe()
#         response_obj._parse_message(json)

#     def _set_data(self, json):
#         data_obj = json.get(self.DATA_KEY)
#         if data_obj is None:
#             raise ValueError(f"Failed parsing response from stream, missing field '{self.DATA_KEY}'")
#         data = CurveEventFilters()
#         # Last id
#         last_id = data_obj.get(self.DATA_LAST_ID_KEY)
#         data.set_last_id(last_id)
#         # Filters
#         filters = _parse_event_options(data_obj.get(self.DATA_FILTERS_KEY))
#         data.set_filters(filters)
#         self.data = data


# class StreamMessageResponseCurvesFilters(_StreamMessageResponse):
#     DATA_FILTERS_KEY = "filters"

#     @staticmethod
#     def from_message(json):
#         response_obj = StreamMessageResponseCurvesFilters()
#         response_obj._parse_message(json)

#     def _set_data(self, json):
#         data_obj = json.get(self.DATA_KEY)
#         if data_obj is None:
#             raise ValueError(f"Failed parsing response from stream, missing field '{self.DATA_KEY}'")
#         # Parse filters
#         filters = data_obj.get(self.DATA_FILTERS_KEY)
#         filters = [_parse_event_options(filter for filter in filters)]
#         self.data = [_parse_event_options(filter for filter in filters)]


# _stream_message_type_lookup = {}

# class StreamMessageType(Enum):
#     # Messages
#     MESSAGE = ("message", StreamMessageMessage)
#     CURVES_EVENT = ("curves.event", StreamMessageCurveEvent)
#     # Responses
#     ERROR = ("error", StreamMessageResponseError)
#     CURVES_SUBSCRIBE = ("curves.subscribe", StreamMessageResponseCurvesSubscribe)
#     CURVES_FILTERS = ("curves.filters", StreamMessageResponseCurvesFilters)

#     def __init__(self, tag, model):
#         self.tag = tag
#         self.model = model
#         _stream_message_type_lookup[tag.lower()] = self

#     def __str__(self):
#         return self.tag

#     def __repr__(self):
#         return self.__str__()

#     @staticmethod
#     def is_valid_tag(tag):
#         return isinstance(tag, str) and tag.lower() in _stream_message_type_lookup

#     @staticmethod
#     def by_tag(tag):
#         return _stream_message_type_lookup[tag.lower()]

#     @staticmethod
#     def tag_from_json(json):
#         return json.get(STREAM_MESSAGE_TYPE_FIELD)


# def _parse_event_options(json):
#     # Event type
#     curve_names = json.get("curve_names")
#     # Either EventCurveOptions or EventFilterOptions
#     if curve_names is not None:
#         return _parse_curve_options(json, curve_names)
#     return _parse_filter_options(json)

# def _parse_curve_options(json, curve_names):
#     # EventCurveOptions
#     options = EventCurveOptions().set_curve_names(curve_names)
#     return _parse_shared_options(json, options)

# def _parse_filter_options(json):
#     # EventFilterOptions
#     options = EventFilterOptions()
#     _parse_shared_options(json, options)
#     # q  (freetext)
#     q = json.get("q")
#     if q is not None:
#         options.set_q(q)
#     # Areas
#     areas = json.get("areas")
#     if areas is not None:
#         options.set_areas(areas)
#     # Data types
#     data_types = json.get("data_types")
#     if data_types is not None:
#         options.set_data_types(data_types)
#     # Commodities
#     commodities = json.get("commodities")
#     if commodities is not None:
#         options.set_commodities(commodities)
#     # Categories
#     categories = json.get("categories")
#     if categories is not None:
#         options.set_categories(categories)
#     # Exact categories
#     exact_categories = json.get("exact_categories")
#     if exact_categories is not None:
#         options.set_exact_categories(exact_categories)
#     return options


# def _parse_shared_options(json, options):
#     # Variables in both CurveOption and FilterOptions
#     # Event type
#     event_types = json.get("event_types")
#     if event_types is not None:
#         options.set_event_types(event_types)
#     # Begin
#     begin = json.get("begin")
#     if begin is not None:
#         options.set_begin(begin)
#     # End
#     end = json.get("end")
#     if end is not None:
#         options.set_end(end)
#     return options