import uuid
import websocket
import threading
import json
import queue
import time
import logging
import os
import re
from energyquantified.events import (
    MessageType,
    EventCurveOptions,
    EventFilterOptions,
    ConnectionEvent,
    CurveEventFilters,
    CurveUpdateEvent,
)
from energyquantified.events.events import TimeoutEvent
from energyquantified.events.responses import CurvesSubscribeResponse, CurvesFiltersResponse
#from energyquantified.events.messages.requests import RequestCurvesSubscribe, RequestCurvesFilters
# from energyquantified.events.server_message import (
    # StreamMessageType,
    # StreamMessageResponseCurvesSubscribe,
    # StreamMessageResponseCurvesFilters,
    # StreamMessageResponseError,
    # StreamMessageMessage,
    # StreamMessageCurveEvent,
# )
from energyquantified.events.messages import (
    RequestCurvesSubscribe,
    RequestCurvesFilters,
    ServerMessageMessage,
    ServerMessageCurveEvent,
    _ServerResponse,
    ServerResponseCurvesSubscribe,
    ServerResponseCurvesFilters,
    ServerResponseError,
    ServerMessageType,
)
from energyquantified.events.callback import Callback, SUBSCRIBE_CURVES, GET_CURVE_FILTERS
from energyquantified.events.connection_event import TIMEOUT, UNKNOWN_ERROR
import random
from energyquantified.parser.events import parse_event_options, parse_curve_event, parse_filters#, parse_subscribe_response
import atexit
from socket import timeout
from websocket import (
    WebSocketException,
    WebSocketConnectionClosedException,
    WebSocketProtocolException,
    WebSocketBadStatusException,
    WebSocketPayloadException,
)
from energyquantified.events.callback import Callback, SUBSCRIBE_CURVES
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


class CurveUpdateEventAPI:
    """
    The curve events API client.

    Wraps the Energy Quantified websocket API for curve events. Handles validation,
    network errors, and parsing of API responses.
    
    :param ws_url: The root URL for the curve events websocket API
    :type ws_url: str
    :param api_key: The API key for your user account
    :type api_key: str, required
    :param last_id_file: A file path to a file that keeps track of the last\
                       event id received from the curve events stream
    :type last_id_file: str, optional

    **Basic usage:**

    Access these operation via an instance of the
    :py:class:`energyquantified.EnergyQuantified` class:

        >>> from energyquantified import EnergyQuantified
        >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd)

    Establishing a connection and connecting to the stream:

        >>> from energyquantified import EnergyQuantified
        >>> from energyquantified.events.events import MessageType
        >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd)
        >>> events = eq.events.connect()
        >>> # Loop over events as they come
        >>> for msg_type, event in events.get_next():
        >>>     if msg_type == MessageType.EVENT:
        >>>         # Optionally load event data from API
        >>>         data = event.load_data()

    At least one filter (of type
    :py:class:`energyquantified.events.EventFilterOptions`
    or :py:class:`energyquantified.events.EventFilterOptions`)
    must be set in order to receive curve events:

        >>> from energyquantified import EnergyQuantified
        >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd)
        >>> ws_client = eq.events.connect()
        >>> from energyquantified.events.event_options import EventFilterOptions
        >>> To receive all UPDATE-events for Germany
        >>> filter = EventFilterOptions().set_areas("DE").set_event_types("UPDATE")
        >>> ws_client.subscribe(filter)
        
    To keep track of the last event received between sesssions, supply the
    ``last_id_file`` parameter with a file path. The file will be created
    for you if it does not already exist. This is useful in the case of
    a disconnect or an unexpected termination.
        
        >>> from energyquantified import EnergyQuantified
        >>> eq = EnergyQuantified(
        >>>     api_key="aaaa-bbbb-cccc-dddd,
        >>>     last_id_file="last_id_file.json"
        >>> )
    
    The file can also be created inside a folder (which will be created for you):
    
        >>> from energyquantified import EnergyQuantified
        >>> eq = EnergyQuantified(
        >>>     api_key="aaaa-bbbb-cccc-dddd,
        >>>     last_id_file="folder_name/last_id_file.json"
        >>> )
    """
    def __init__(self, ws_url, api_key):
        self._ws_url = ws_url
        self._api_key = api_key
        self._ws = None
        self._wst = None
        self._messages = queue.Queue()
        self._is_connected = threading.Event()
        self._last_connection_event = ConnectionEvent(status_code=1000, message="Not connected to the server")
        self._should_not_connect = threading.Event()
        # Should not try until connect() invoked
        self._should_not_connect.set()
        self._done_trying_to_connect = threading.Event()
        self._done_trying_to_connect.set()
        self._max_reconnect_attempts = 3
        self._remaining_reconnect_attempts = 1
        self._remaining_reconnect_attempts_lock = threading.Lock()
        # Subscribe
        self._callbacks = {}
        self._is_subscribed_curves = threading.Event()
        self._messages_lock = threading.Lock()
        self._latest_curves_subscribe_message = None
        # Last event id
        self._last_id = None
        self._last_id_timestamp = None
        # Last event id file
        self._last_id_file_path = None
        self._last_id_file_lock = threading.Lock()
        self._last_id_file_updated = None
        self._last_id_file_atexit = None
        # Message handlers
        self._message_handler = lambda msg: log.info("Message from server: %s" % msg)
        # TODO what if response.request_id is in callbacks? 
        self._error_handler = lambda err: log.error(err)

    def set_message_handler(self, func):
        self._message_handler = func

    def set_error_handler(self, func):
        self._error_handler = func

    def _setup_last_id_file(self):
        """
        Finds last_id if the file exists with correct access.
        Creates the file if not.
        """
        if os.path.exists(self._last_id_file_path):
            # Raise error if path exists but it's not a file
            if not os.path.isfile(self._last_id_file_path):
                raise FileNotFoundError(
                    f"Path last_id_file: '{self._last_id_file_path}' exists but it is not a file"
                    )
            # Read-access
            if not os.access(self._last_id_file_path, os.R_OK):
                raise PermissionError(f"Missing read-access to last_id_file: '{self._last_id_file_path}'")
            # Write-access
            if not os.access(self._last_id_file_path, os.W_OK):
                raise PermissionError(f"Missing write-access to last_id_file: {self._last_id_file_path}")
            # Find from file and set
            with open(self._last_id_file_path, "r") as f:
                data = json.load(f)
                # Default to None
                self._last_id = data.get("last_id")

        else:
            # Try to create parent dirs if not exists
            parent_dir = os.path.dirname(self._last_id_file_path)
            if not parent_dir:
                parent_dir = "."
            else:
                # Create parent dirs if not exists
                os.makedirs(parent_dir, exist_ok=True)
            if not os.access(parent_dir, os.W_OK):
                    raise PermissionError(
                        f"last_id_file: '{self._last_id_file_path}' does not exist "
                        f"and missing write-access to parent directory: '{parent_dir}'"
                        )
            # Create file
            with open(self._last_id_file_path, "w") as f:
                json.dump({"last_id": ""}, f)

    def _update_last_id(self, last_id, force_update=False):
        """
        Updates the last event id in memory.

        :param last_id: The new id
        :type last_id: str
        :param force_update: Overwrites the current last_id without comparing if True.\
                            Saves the greates of the two id's if False. Defaults to False.
        :type force_update: bool, optional
        """
        if force_update:
            self._last_id = last_id
            return
        # Nothing to update if the new id is None
        if last_id is None:
            return
        # No need to compare if the current last_id is None
        if self._last_id is None:
            self._last_id = last_id
            return
        # At this point we know neither are None. Time to keep compare and keep
        # the greatest of the two id's.
        # last_id format: str of timestamp (millis) and a seq. number separated by dash
        # format: ^\\d{13}-{1}\\d+$
        current_id = self._last_id.split("-")
        new_id = last_id.split("-")
        # First compare timestamps
        current_timestamp = int(current_id[0])
        new_timestamp = int(new_id[0])
        if new_timestamp > current_timestamp:
            self._last_id = last_id
        elif new_timestamp == current_timestamp:
            # Compare sequence number if equal timestamps
            current_n = int(current_id[1])
            new_n = int(new_id[1])
            if new_n > current_n:
                self._last_id = last_id

    def _last_id_to_file(self, last_id=None, write_interval_s=120):
        """
        Saves the last_id to disk if the file path exists, last_id is not None,
        and it's at least 'write_interval_s' seconds since last save.

        :param last_id: The id
        :type last_id: str, optional
        :param write_interval_s: The minimum number of seconds since last write, defaults to 120
        :type write_interval_s: int, optional
        """
        # Ignore if user didn't provide a file path
        if self._last_id_file_path is None:
            return
        if last_id is None:
            if self._last_id is None:
                return
            # Fallback to 
            last_id = self._last_id
        # Don't write if less than 'write_interval_s' since last
        if self._last_id_timestamp is not None and time.time() < self._last_id_timestamp + write_interval_s:
            return
        # Block other access to file
        with open(self._last_id_file_path, "r+") as f:
            try:
                data = json.load(f)
            except Exception as e:
                data = {}
            data["last_curve_event_id"] = last_id
            # Write from start of file
            f.seek(0,0)
            #f.truncate()
            json.dump(data, f)
            # Truncate in case the new data is shorter
            f.truncate()
        self._last_id_timestamp = time.time()

    def _on_open(self, _ws):
        self._last_connection_event = None
        # Reset reconnect counter on successfull connection
        with self._remaining_reconnect_attempts_lock:
            self._remaining_reconnect_attempts = self._max_reconnect_attempts
        # Flag events
        self._is_connected.set()
        self._done_trying_to_connect.set()
        # Send the last active filters
        if self._latest_curves_subscribe_message is not None:
            if self._last_id is not None:
                self._latest_curves_subscribe_message["last_id"] = self._last_id
                log.info("Reconnected to the stream, sending %s to subscribe with previous filters" % self._latest_curves_subscribe_message)
                #self._messages.put((MessageType.INFO, "Successfully reconnected to the server, setting previous filters.."))
                self._ws.send(json.dumps(self._latest_curves_subscribe_message))

    # def _on_message(self, _ws, message):
    #     print(f"msg: {message}")
    #     try:
    #         msg = json.loads(message)
    #         msg_tag = msg.pop("type")
    #         if not MessageType.is_valid_tag(msg_tag):
    #             # Convert message to info
    #             if msg_tag.lower() == "message":
    #                 msg_type = MessageType.INFO
    #             else:
    #                 raise ValueError(f"Unknown message type: '{message}'")
    #         else:
    #             msg_type = MessageType.by_tag(msg_tag)
    #         if msg_type == MessageType.EVENT:
    #             data = parse_event(msg)
    #             self._set_last_id(data.event_id)
    #             self._last_id_to_file(last_id=data.event_id)
    #         elif msg_type == MessageType.FILTERS:
    #             if not self._filters_is_active.is_set():
    #                 request_id = json.get("request_id")
    #                 try:
    #                     request_id_uuid = uuid.UUID(request_id, version=4)
    #                     if request_id_uuid == self._latest_filters_uuid:
    #                         data = parse_filters(msg)
    #                 except Exception as _:
    #                     data = f"Failed to parse request id from server message,"
    #                     return
    #                 finally:
                    

    #         elif msg_type == MessageType.INFO:
    #             data = msg["message"]
    #         elif msg_type == MessageType.ERROR:
    #             data = msg
    #         else:
    #             raise ValueError(f"Unknown MessageType: {msg_type} for message: {message}")
    #     except Exception as e:
    #         msg_type = MessageType.ERROR
    #         data = f"Failed to parse message: '{message}' from stream, cause: {e}"
    #     finally:
    #         self._messages.put((msg_type, data))

    # def _on_message(self, _ws, message):
    #     print(f"msg: {message}")
    #     try:
    #         msg = json.loads(message)
    #         msg_type = msg["type"]
    #         if not MessageType.is_valid_tag(msg_type):
    #             if msg_type.lower() == "message":
    #                 msg_type = MessageType.INFO
    #             else:
    #                 raise ValueError(f"Failed to parse MessageType from {msg_type}")
    #         else:
    #             msg_type = MessageType.by_tag(msg_type)
    #         # TODO wip start
    #         # if response is type subscribe
    #         # parse subscribe response
    #         # 
    #         # TODO wip end
    #         if MessageType == MessageType.ERROR:
    #             if msg["code"] == "json failed ..":
    #                 pass # SubscribeResponse
    #             elif msg["code"] == "too many filters ..":
    #                 pass # SubscribeResponse
    #             elif msg["code"] == "bad last_id ..":
    #                 pass # SubscribeResponse
    #             else:
    #                 pass # Unknown?
    #         elif msg_type == MessageType.FILTERS:
    #             request_id = msg.get("request_id")

    #             last_id = msg.get("last_id")
    #             filters = parse_filters(msg)
    #             response = SubscribeResponse(True, filters, last_id=last_id)

    #     except Exception as e:
    #         f"Failed to parse message: {message} from stream, cause: {e}"
    #     # TODO
    #     if subscribe or sub errror:
    #         callback = self._callbacks[msg["request_id"]]
    #         if callback:
    #             if callback.latest and not msg_error:
    #                 # set events active
    #                 pass
    #             callback.callback(to_response(msg))
    #     # TODO

    # def _on_message(self, _ws, message):
    #     log.debug("")
    #     log.debug(message)
    #     log.debug("")
    #     with self._messages_lock:
    #         try:
    #             msg = json.loads(message)
    #         except Exception as e:
    #             self._messages.put((MessageType.ERROR, f"Failed to parse message: {message}, exception: {e}"))
    #             return
    #         if msg["type"].lower() == "curves.subscribe":
    #             self._handle_message_subscribe_curves(msg)
    #             return
    #         if not MessageType.is_valid_tag(msg["type"]):
    #             self._messages.put((MessageType.ERROR, f"Unknown message type: {msg.get('type')}"))
    #             return
    #         msg_type = MessageType.by_tag(msg["type"])
    #         if msg_type == MessageType.CURVE_EVENT:
    #             if self._is_subscribed_curves.is_set():
    #                 obj = parse_event(msg)
    #                 self._update_last_id(obj.event_id)
    #                 self._last_id_to_file(obj.event_id)
    #         elif msg_type == MessageType.MESSAGE:
    #             obj = msg["message"]
    #         elif msg_type == MessageType.ERROR:
    #             # TODO Can this ever happen?
    #             obj = msg
    #         else:
    #             self._messages.put((MessageType.ERROR, f"Missing handler for MessageType {msg_type}"))
    #             return
    #         self._messages.put((msg_type, obj))

    # def _on_message(self, _ws, message):
    #     log.debug("")
    #     log.debug(message)
    #     log.debug("")
    #     with self._messages_lock:
    #         try:
    #             json = json.loads(message)
    #         except Exception as e:
    #             self._messages.put((MessageType.ERROR, f"Failed to parse message: {message}, exception: {e}"))
    #             return
    #         # TODO
    #         #server_msg = 
    #         if json["type"].lower() == "curves.subscribe":
    #             self._handle_message_subscribe_curves(json)
    #             return
    #         if not MessageType.is_valid_tag(json["type"]):
    #             self._messages.put((MessageType.ERROR, f"Unknown message type: {json.get('type')}"))
    #             return
    #         msg_type = MessageType.by_tag(json["type"])
    #         if msg_type == MessageType.CURVE_EVENT:
    #             if self._is_subscribed_curves.is_set():
    #                 obj = parse_event(json)
    #                 self._update_last_id(obj.event_id)
    #                 self._last_id_to_file(obj.event_id)
    #         elif msg_type == MessageType.MESSAGE:
    #             obj = json["message"]
    #         elif msg_type == MessageType.ERROR:
    #             # TODO Can this ever happen?
    #             obj = json
    #         else:
    #             self._messages.put((MessageType.ERROR, f"Missing handler for MessageType {msg_type}"))
    #             return
    #         self._messages.put((msg_type, obj))

    def _on_message(self, _ws, message):
        #log.debug(message)
        with self._messages_lock:
            # TODO probably want to stop execution if this fails
            try:
                message_json = json.loads(message)
            except Exception as e:
                self._messages.put((MessageType.ERROR, f"Failed to parse message: {message}, exception: {e}"))
                return
            msg_type_tag = ServerMessageType.tag_from_json(message_json)
            if not ServerMessageType.is_valid_tag(msg_type_tag):
                # Unkown type, skip. Might be a new type that is not supported in this version.
                pass
            msg_obj = ServerMessageType.by_tag(msg_type_tag).model.from_message(message_json)
            # Check type
            if isinstance(msg_obj, ServerMessageMessage):
                self._message_handler(msg_obj.message)
            elif isinstance(msg_obj, ServerMessageCurveEvent):
                if self._is_subscribed_curves.is_set():
                    event = msg_obj.event
                    self._update_last_id(event.event_id)
                    self._last_id_to_file(event.event_id)
                    self._messages.put(event)
            elif isinstance(msg_obj, _ServerResponse):
                callback = self._callbacks.pop(msg_obj.request_id, None)
                if callback is None:
                    return
                if isinstance(msg_obj, ServerResponseCurvesSubscribe):
                    subscribe_response = CurvesSubscribeResponse(
                        status=msg_obj.status,
                        data=msg_obj.data,
                        errors=msg_obj.errors,
                    )
                    callback.callback(subscribe_response)
                    if callback.latest and subscribe_response.subscribe_ok:
                        self._is_subscribed_curves.set()
                elif isinstance(msg_obj, ServerResponseCurvesFilters):
                    filters_response = CurvesFiltersResponse(
                        status=msg_obj.status,
                        data=msg_obj.data,
                        errors=msg_obj.errors,
                    )
                    callback.callback(filters_response)
                elif isinstance(msg_obj, ServerResponseError):
                    # TODO what to do here?
                    # Should only really happen if server fails to parse 'type' (so shouldnt happen)
                    # TODO what if callback exists for request_id?
                    self._error_handler(". ".join[[err.capitalize() for err in msg_obj.errors]])
                else:
                    # Might be a new type that is not supported in this version. Skip.
                    pass
            else:
                # Might be a new type that is not supported in this version. Skip.
                pass
            # if isinstance(msg_obj, ServerResponseCurvesSubscribe):
            #     callback = self._callbacks.pop(msg_obj.request_id, None)
            #     if callback is not None:
            #         subscribe_response = SubscribeResponse(
            #             subscribe_ok=msg_obj.status,
            #             last_id=msg_obj.data.last_id,
            #             filters=msg_obj.data.filters,
            #             errors=msg_obj.errors,
            #         )
            #         callback.callback(subscribe_response)
            #         if callback.latest and subscribe_response.subscribe_ok:
            #             self._is_subscribed_curves.set()
            # elif isinstance(msg_obj, ServerResponseCurvesFilters):
            #     callback = self._callbacks.pop(msg_obj.request_id, None)
            #     if callback is not None:
            #         pass
            # elif isinstance(msg_obj, ServerResponseError):
            #     pass
            # else:
            #     # Unkown type, skip. Might be a new type that is not supported in this version.
            #     pass
            # TODO
            # if message_json["type"].lower() == "curves.subscribe":
            #     self._handle_message_subscribe_curves(message_json)
            #     return
            # if not MessageType.is_valid_tag(message_json["type"]):
            #     self._messages.put((MessageType.ERROR, f"Unknown message type: {message_json.get('type')}"))
            #     return
            # msg_type = MessageType.by_tag(message_json["type"])
            # if msg_type == MessageType.CURVE_EVENT:
            #     if self._is_subscribed_curves.is_set():
            #         obj = parse_event(message_json)
            #         self._update_last_id(obj.event_id)
            #         self._last_id_to_file(obj.event_id)
            # elif msg_type == MessageType.MESSAGE:
            #     obj = message_json["message"]
            # elif msg_type == MessageType.ERROR:
            #     # TODO Can this ever happen?
            #     obj = message_json
            # else:
            #     self._messages.put((MessageType.ERROR, f"Missing handler for MessageType {msg_type}"))
            #     return
            # self._messages.put((msg_type, obj))

    # def _handle_message_subscribe_curves(self, msg):
    #     # Parse uuid from request_id
    #     request_id = msg["request_id"]
    #     try:
    #         request_id = uuid.UUID(request_id, version=4)
    #     except ValueError as e:
    #         self._messages.put((MessageType.ERROR, f"Failed to parse uuid from message: {msg}, error: {e}"))
    #         return
    #     # TODO do we want to pop? Would be nice to keep latest in case of a disconnect (to 
    #     # automatically reconnect with previous filters)
    #     callback = self._callbacks.pop(request_id, None)
    #     #callback = self._callbacks.get(request_id) TODO
    #     if callback is not None:
    #         subscribe_response = parse_subscribe_response(msg)
    #         callback.callback(subscribe_response)
    #         if callback.latest and subscribe_response.subscribe_ok:
    #             # TODO use a lock when calling the callback and flagging is_subscribed_curves
    #             self._is_subscribed_curves.set()

    # def _handle_message_subscribe_curves(self, msg):
    #     # Parse uuid from request_id
    #     request_id = msg["request_id"]
    #     try:
    #         request_id = uuid.UUID(request_id, version=4)
    #     except ValueError as e:
    #         self._messages.put((MessageType.ERROR, f"Failed to parse uuid from message: {msg}, error: {e}"))
    #         return
    #     # TODO do we want to pop? Would be nice to keep latest in case of a disconnect (to 
    #     # automatically reconnect with previous filters)
    #     callback = self._callbacks.pop(request_id, None)
    #     #callback = self._callbacks.get(request_id) TODO
    #     if callback is not None:
    #         subscribe_response = parse_subscribe_response(msg)
    #         callback.callback(subscribe_response)
    #         # TODO use lock here or outer?
    #         if callback.latest and subscribe_response.subscribe_ok:
    #             self._is_subscribed_curves.set()

    def _on_close(self, _ws, status_code, msg):
        # last_connection_event should only be set once for each time connecting
        if self._last_connection_event is None:
            # Network error if no status_code
            if status_code is None:
                # 1005 if first close frame, no status code and NOT closed by user. Source:
                #   https://www.rfc-editor.org/rfc/rfc6455.html#section-7.1.5
                status_code = 1005
            self._last_connection_event = ConnectionEvent(status_code=status_code, message=msg)
        if self._is_connected.is_set():
            self._is_connected.clear()
            with self._last_id_file_lock:
                self._last_id_to_file(write_interval_s=0)

    def _on_error(self, _ws, error):
        if not isinstance(error, (timeout, ConnectionError, WebSocketException)):
            # TODO raise error instead of returning? or create connection event?
            # self._messages.put((MessageType.ERROR, getattr(error, "strerror", str(error))))
            print(f"on er: {error}")
            self._error_handler(getattr(error, "strerror", str(error)))
            return
        # Set _last_connection_event (only if not already)
        if self._last_connection_event is not None:
           print(f"hm: {error}")
           return
        if isinstance(error, timeout):
            self._last_connection_event = ConnectionEvent(status=TIMEOUT, message=str(error))
        elif isinstance(error, ConnectionError):
            # TODO if Errno111 -> only use message (not status code)
            status_code = error.errno
            error_message = error.strerror
            self._last_connection_event = ConnectionEvent(status_code=status_code, message=error_message)
        elif isinstance(error, WebSocketException):
            # Type of exception
            if hasattr(error, "status_code"):
                # At the time of writing, WebSocketBadStatusException is the only
                #   WebsocketException with this attribute
                status_code = error.status_code
            elif isinstance(error, WebSocketBadStatusException):
                status_code = error.status_code
            elif isinstance(error, WebSocketProtocolException):
                status_code = 1002
            elif isinstance(error, WebSocketPayloadException):
                status_code = 1007
            elif isinstance(error, WebSocketConnectionClosedException):
                # Abnormal (https://www.rfc-editor.org/rfc/rfc6455.html#section-7.2)
                status_code = 1006
            else:
                # Default to abnormal (no close frame received)
                # (https://www.rfc-editor.org/rfc/rfc6455.html#section-7.2)
                status_code = 1006
            # Create the connection event
            self._last_connection_event = ConnectionEvent(
                    status_code=status_code,
                    message=str(error),
                )

    @property
    def last_id(self):
        return self._last_id

    def connect(self, last_id_file=None, timeout=10, reconnect_attempts=5):
        """
        Connect to the curve update events stream.

        To keep track of the last event received between sesssions, supply the
        ``last_id_file`` parameter with a file path. The file will be created
        for you if it does not already exist. This is useful in the case of
        a disconnect or an unexpected termination.

        Optionally supply the ``timeout`` parameter with an integer to change the
        default number of seconds to wait for a connection to be established before
        failing.

        The client tries to automatically reconnect if the connections drops. The
        number of reconnect attempts can be changed with the ``reconnect_attempts``
        parameter.

        >>> from energyquantified import EnergyQuantified
        >>> eq = EnergyQuantified(
        >>>     api_key="aaaa-bbbb-cccc-dddd
        >>> )
        >>> eq.events.connect(last_id_file="last_id_file.json")
    
        The file can also be created inside a folder (which will be created for you if
        it does not already exist):
    
        >>> from energyquantified import EnergyQuantified
        >>> eq = EnergyQuantified(
        >>>     api_key="aaaa-bbbb-cccc-dddd
        >>> )
        >>> eq.events.connect(last_id_file="folder_name/last_id_file.json")

        :param last_id_file: A file path to a file that keeps track of the last\
                       event id received from the curve events stream
        :type last_id_file: str, optional
        # TODO last_id moved to subscribe_curves_..(..)
        :param last_id: ID of the latest event received. Used for excluding older events.\
                Takes priority over the id from a potential last_id file.
        :type last_id: str, optional
        :param timeout: The time in seconds to wait for a connection to be established.\
                Also used as the minimum wait-time inbetween reconnect attempts. Defaults to 5.
        :type timeout: int, optional
        :param reconnect_attempts: The number of reconnect attempts after each disconnect.\
                The counter is reset whenever a connection is established. Defaults to 5.
        :type reconnect_attempts: int, optional
        :return: The obj instance this method was invoked upon, so the APi can be used fluently
        :rtype: :py:class:`energyquantified.events.CurveUpdateEventAPI`
        """
        assert self._should_not_connect.is_set(), (
            "'connect()' invoked while already connected. "
            "Please close the existing connection first by calling 'close()'"
        )
        # Last id file
        with self._last_id_file_lock:
            # Unregister if previously registered for atexit
            atexit.unregister(self._last_id_file_atexit)
            self._last_id_file_path = last_id_file
            if last_id_file is not None:
                # Find last_id from file or create file if not exists
                self._setup_last_id_file()

                def save_id():
                    self._last_id_to_file(write_interval_s=0)

                # Store the method in a variable so it can be unregistered later
                self._last_id_file_atexit = save_id
                atexit.register(self._last_id_file_atexit)
        self._max_reconnect_attempts = reconnect_attempts
        # Reset flags
        self._should_not_connect.clear()
        self._done_trying_to_connect.clear()
        self._last_connection_event = None
        # Close if already set
        if self._ws is not None:
            self._ws.close()
        websocket.setdefaulttimeout(timeout)
        print(f"ws url: {self._ws_url}")
        self._ws = websocket.WebSocketApp(
            self._ws_url,
            header={
                "X-API-KEY": self._api_key
            },  
            on_open=self._on_open,
            on_message=self._on_message,
            on_close=self._on_close,
            on_error=self._on_error,
        )

        def _ws_thread():
            while not self._should_not_connect.is_set():
                # Decrement reconnect counter
                with self._remaining_reconnect_attempts_lock:
                    self._remaining_reconnect_attempts -= 1
                # Blocking until dc (ping timeout to detect local network error)
                self._ws.run_forever(ping_interval=15, ping_timeout=10)
                # Reset flag and last connection event
                self._done_trying_to_connect.clear()
                # Safely acquire the reconnect_counter
                with self._remaining_reconnect_attempts_lock:
                    # Stop if no more attempts
                    if self._remaining_reconnect_attempts <= 0:
                        self._should_not_connect.set()
                        self._done_trying_to_connect.set()
                        return
                    elif self._remaining_reconnect_attempts == self._max_reconnect_attempts:
                        # TODO what? x1 (first dc after connect)
                        pass
                # Wait delta longer than the default ws timeout,
                # plus a random amount of time to spread traffic
                time.sleep(timeout + 0.5 + random.uniform(1,5))

        self._wst = threading.Thread(target=_ws_thread)
        self._wst.daemon = True
        self._wst.start()

        self._done_trying_to_connect.wait()
        return self

    def close(self):
        """
        Close the stream connection (if open) and disables automatic reconnect.
        """
        self._last_connection_event = ConnectionEvent(status_code=1000, message="Connection closed by user")
        self._should_not_connect.set()
        if self._ws is not None:
            self._ws.close()

    def disconnect(self):
        """
        Close the stream connection (if open) and disables automatic reconnect.
        """
        self.close()

    def on_curves_subscribed(response):
        """
        Default callback for how to handle a subscribe response.

        :param response: The response for the subscribe message
        :type response: SubscribeResponse
        """
        if response.ok:
            filters = response.data.filters
            last_id = response.data.last_id
            log.info("Subscribe OK - from id %s with filters %s" % (last_id, filters))
        else:
            errors = response.errors
            log.error("Failed to subscribe - %s" % errors)

    def subscribe_curve_events(self, filters=None, last_id=None, callback=on_curves_subscribed):
        """
        Send a filter or a list of filters to the stream, subscribing to
        curve events matching any of the filters.
        
        The server responds with the new filters if the subscribe was successful,
        and the response is added to the message queue that can be accessed through
        :py:meth:`get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>`.
        The message will have the ``MessageType.FILTERS`` type. The response also
        includes a unique id that can be preset by supplying the ``request_id``
        parameter with an id in the call to subscribe. The id must be a ``uuid``
        object in version 4 format, created as shown in the code snippet below:

        # TODO update doc (remove uuid)
            >>> import uuid
            >>> subscribe_id = uuid.uuid4()

        Subscribe with the preset request id:

            >>> import uuid
            >>> subscribe_id = uuid.uuid4()
            >>> filters = ...
            >>> subscribe(filters, request_id=subscribe_id)

        Find out when you are successfully subscribed with the provided filters
        by comparing your id with with the id's of new messages:

            >>> import uuid
            >>> from energyquantfied.events import MessageType
            >>> subscribe_id = uuid.uuid4()
            >>> filters = ...
            >>> subscribe(filters, request_id=subscribe_id)
            >>> # Compare ID while reading from the stream
            >>> for msg_type, msg in eq.events.get_next():
            >>>     if msg_type == MessageType.FILTERS:
            >>>         if msg.request_id == subscribe_id:
            >>>             # ID match so we know the filters are set

        # TODO last_id=None, options: "keep"

        :param filters: The filters. Can be a single filter or a list of filters.
        :type filters: list[:py:class:`energyquantified.events.EventFilterOptions` | \
            :py:class:`energyquantified.events.EventCurveOptions`]
        :param request_id: Preset id for the response
        :type request_id: ``uuid.UUID`` (v4), optional
        # TODO params
        :param fill_last_id: If last_id is not set in the filters, this can be set to\
            True in order to use subscribe to events after the last_id saved in memory.\
            Does nothing if last_id is set in the filters. Defaults to False.
        :type fill_last_id: bool
        """
        # Validate filters
        if not isinstance(filters, list):
            filters = [filters]
        for curve_filter in filters:
            assert isinstance(curve_filter, (EventCurveOptions, EventFilterOptions)), (
                f"Invalid filter type, expected EventCurveOptions or EventFilterOptions "
                f"but found {type(curve_filter)}"
            )
            is_valid, errors = curve_filter.validate()
            assert is_valid, (
                f"Invalid filter {curve_filter}, "
                f"errors: {errors}"
            )
        # Validate last_id
        if last_id is not None:
            assert isinstance(last_id, str), "param 'last_id' must be None or a str"
            # Use id from memeory if 'keep'
            if last_id.lower() == "keep":
                last_id = self._last_id
            else:
                assert re.fullmatch("^\\d{13}-{1}\\d+$", last_id), (
                    f"Invalid last_id format: {last_id}, "
                    f"expected two numbers separated by a dash ('-'), "
                    f"where the first number is exactly 13 digits long"
                )
        # At least one of 'last_id' and 'filters' must be set
        assert last_id is not None or filters is not None, (
            f"Minimum one of 'last_id' and 'filters' must be set in order to subscribe to curve events"
        )
        # Validation done. Create request id
        request_id = uuid.uuid4()
        subscribe_message = RequestCurvesSubscribe(
            request_id,
            last_id=last_id,
            filters=filters
        ).to_message()
        # Stop receiving events until subscribed with new filters
        with self._messages_lock:
            self._is_subscribed_curves.clear()
            # Clear existing curve events from message queue
            messages = []
            try:
                for msg in self._messages.get(block=False):
                    if not isinstance(msg, CurveUpdateEvent):
                        messages.append(msg)
                    self._messages.task_done()
            except queue.Empty:
                for msg in messages:
                    self._messages.put(msg)
            # Make sure none of the existing callbacks are marked as latest
            for _, obj in self._callbacks.items():
                if obj.callback_type == SUBSCRIBE_CURVES:
                    obj.latest = False
                    # TODO or just del other curves.subscribe callbacks instead?
                    #del self._callbacks[k] #_ / k
            # Callback
            callback = Callback(callback, callback_type=SUBSCRIBE_CURVES, latest=True)
            self._callbacks[request_id] = callback
        # Send msg
        self._latest_curves_subscribe_message = subscribe_message
        self._update_last_id(last_id, force_update=True)
        self._last_id_to_file(write_interval_s=0)
        #log.debug(f"sub msg: {subscribe_message}")
        msg = json.dumps(subscribe_message)
        #log.debug(f"Sending messsage to subscribe curves:\n{msg}")
        self._ws.send(msg)

    # def get_next(self, timeout=None):
    #     """
    #     Returns a generator over messages from the stream, and blocks
    #     while waiting for new messages.
        
    #     Each messages is a tuple of two objects; (1) a
    #     :py:class:`energyquantified.events.MessageType` and (2) one of
    #     (:py:class:`energyquantified.events.CurveUpdateEvent`,
    #     :py:class:`energyquantified.events.ConnectionEvent`, str, None). The
    #     ``MessageType`` is used for describing the second element. Example:

    #     >>> for msg_type, msg in enumerate(get_next(3)):
    #     >>>     if msg_type == MessageType.EVENT:
    #     >>>         # Got a new event
    #     >>>         # msg. ...
    #     >>>     elif msg_type == MessageType.INFO:
    #     >>>         # Got an informative message from the server
    #     >>>         # Maybe I want to skip this
    #     >>>     elif msg_type == MessageType.FILTERS:
    #     >>>         # Got the currently active filters on the stream, let's
    #     >>>         # check it out
    #     >>>         print(msg)
    #     >>>     elif msg_type == MessageType.TIMEOUT:
    #     >>>         # No new message or event in the last 'timeout' seconds
    #     >>>         # Maybe I want to change filters soon ..

    #     See also :py:class:`energyquantified.events.MessageType`.

    #     The different message types and what they mean:

    #     What the second element is based on the first element:
    #     ``MessageType.EVENT``:
    #         A new event.

    #         type: :py:class:`energyquantified.events.CurveUpdateEvent`

    #     ``MessageType.INFO``:
    #         An informative message from the stream server.

    #         type: str

    #     ``MessageType.FILTERS``:
    #         A list of filters currently subscribed to.

    #         type: list[:py:class:`energyquantified.events.EventFilterOptions`
    #         | :py:class:`energyquantified.events.EventCurveOptions`]

    #     ``MessageType.ERRORS``:
    #         An error message that could either be from the stream (e.g., after
    #         subscribing with invalid filters), or if something went wrong while
    #         parsing a message.

    #         type: str

    #     ``MessageType.TIMEOUT``:
    #         This means that the client is connected to the stream and no messages has
    #         been received in the last ``timeout`` (i.e., the number supplied to the
    #         ``timeout`` parameter) seconds, and the second element is simply ``None``
    #         and can be ignored. The intention of this message type is to provider users
    #         with a way to act inbetween events (e.g., to change filters).

    #         type: None

    #     ``MessageType.DISCONNECTED``:
    #         This means that the client is neither connected to the stream, nor is it
    #         trying to (re)connect. This happens if
    #         :py:meth:`get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>` is
    #         called before :py:meth:`connect() <energyquantified.api.CurveUpdateEventAPI.connect>`,
    #         if the initial connection failed, or if the connection dropped and the maximum number
    #         of reconnect attempts was exceeded. The
    #         :py:class:`energyquantified.events.ConnectionEvent` describes the cause of the error.
    #         Since this means that the the client will **not** automatically reconnect,
    #         :py:meth:`connect() <energyquantified.api.CurveUpdateEventAPI.connect>` must be manually
    #         invoked in order to reconnect.

    #         type: :py:class:`energyquantified.events.ConnectionEvent`

    #     ``get_next()`` blocks program execution until a new message is available. If the
    #     ``timeout`` parameter is set, a tuple with ``MessageType.TIMEOUT`` is yielded
    #     whenever the timeout is reached. 
            
    #     :param timeout: The number of seconds to wait (blocking) for a new message,\
    #             yielding a MessageType.TIMEOUT if the timeout occurs. Waits indefinetly\
    #             if timeout is None. Defaults to None.
    #     :type timeout: int, optional
    #     :yield: A generator of messages from the stream, blocks while waiting for new
    #     :rtype: tuple
    #     """
    #     # TODO should probably use _messages_lock here
    #     while True:
    #         # Make sure 
    #         if not self._is_connected.is_set():
    #             try:
    #                 # Block=False since not connected
    #                 msg = self._messages.get(block=False)
    #                 yield msg
    #                 self._messages.task_done()
    #             except queue.Empty:
    #                 # Wait if trying to (re)connect
    #                 self._done_trying_to_connect.wait()
    #                 # Yield DC ConnectionEvent if not connected and not retrying
    #                 # ^ either if never connected or exceeded max reconnect attempts
    #                 if self._should_not_connect.is_set():
    #                     yield (MessageType.DISCONNECTED, self._last_connection_event)
    #                     # Wait up to 2 seconds before next iteration. Breaks early if
    #                     # a new connection has been established (in case of incoming events)
    #                     self._is_connected.wait(2)
    #         else:
    #             try:
    #                 msg = self._messages.get(timeout=timeout)
    #                 yield msg
    #                 self._messages.task_done()
    #             except queue.Empty:
    #                 # If connection dropped while waiting for a message 
    #                 if not self._is_connected.is_set():
    #                     continue
    #                 yield (MessageType.TIMEOUT, None)

    def get_next(self, timeout=None):
        """
        Returns a generator over messages from the stream, and blocks
        while waiting for new messages.
        
        Each messages is a tuple of two objects; (1) a
        :py:class:`energyquantified.events.MessageType` and (2) one of
        (:py:class:`energyquantified.events.CurveUpdateEvent`,
        :py:class:`energyquantified.events.ConnectionEvent`, str, None). The
        ``MessageType`` is used for describing the second element. Example:

        >>> for msg_type, msg in enumerate(get_next(3)):
        >>>     if msg_type == MessageType.EVENT:
        >>>         # Got a new event
        >>>         # msg. ...
        >>>     elif msg_type == MessageType.INFO:
        >>>         # Got an informative message from the server
        >>>         # Maybe I want to skip this
        >>>     elif msg_type == MessageType.FILTERS:
        >>>         # Got the currently active filters on the stream, let's
        >>>         # check it out
        >>>         print(msg)
        >>>     elif msg_type == MessageType.TIMEOUT:
        >>>         # No new message or event in the last 'timeout' seconds
        >>>         # Maybe I want to change filters soon ..

        See also :py:class:`energyquantified.events.MessageType`.

        The different message types and what they mean:

        What the second element is based on the first element:
        ``MessageType.EVENT``:
            A new event.

            type: :py:class:`energyquantified.events.CurveUpdateEvent`

        ``MessageType.INFO``:
            An informative message from the stream server.

            type: str

        ``MessageType.FILTERS``:
            A list of filters currently subscribed to.

            type: list[:py:class:`energyquantified.events.EventFilterOptions`
            | :py:class:`energyquantified.events.EventCurveOptions`]

        ``MessageType.ERRORS``:
            An error message that could either be from the stream (e.g., after
            subscribing with invalid filters), or if something went wrong while
            parsing a message.

            type: str

        ``MessageType.TIMEOUT``:
            This means that the client is connected to the stream and no messages has
            been received in the last ``timeout`` (i.e., the number supplied to the
            ``timeout`` parameter) seconds, and the second element is simply ``None``
            and can be ignored. The intention of this message type is to provider users
            with a way to act inbetween events (e.g., to change filters).

            type: None

        ``MessageType.DISCONNECTED``:
            This means that the client is neither connected to the stream, nor is it
            trying to (re)connect. This happens if
            :py:meth:`get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>` is
            called before :py:meth:`connect() <energyquantified.api.CurveUpdateEventAPI.connect>`,
            if the initial connection failed, or if the connection dropped and the maximum number
            of reconnect attempts was exceeded. The
            :py:class:`energyquantified.events.ConnectionEvent` describes the cause of the error.
            Since this means that the the client will **not** automatically reconnect,
            :py:meth:`connect() <energyquantified.api.CurveUpdateEventAPI.connect>` must be manually
            invoked in order to reconnect.

            type: :py:class:`energyquantified.events.ConnectionEvent`

        ``get_next()`` blocks program execution until a new message is available. If the
        ``timeout`` parameter is set, a tuple with ``MessageType.TIMEOUT`` is yielded
        whenever the timeout is reached. 
            
        :param timeout: The number of seconds to wait (blocking) for a new message,\
                yielding a MessageType.TIMEOUT if the timeout occurs. Waits indefinetly\
                if timeout is None. Defaults to None.
        :type timeout: int, optional
        :yield: A generator of messages from the stream, blocks while waiting for new
        :rtype: tuple
        """
        if timeout is not None:
            last_timeout_timestamp = int(time.time())
        while True:
            self._messages_lock.acquire()
            if not self._is_connected.is_set():
                try:
                    # Block=False since not connected
                    msg = self._messages.get_nowait()
                    self._messages.task_done()
                    self._messages_lock.release()
                    yield msg
                except queue.Empty:
                    self._messages_lock.release()
                    # Wait if trying to (re)connect
                    self._done_trying_to_connect.wait()
                    # Yield DC ConnectionEvent if not connected and not retrying
                    # ^ either if never connected or exceeded max reconnect attempts
                    if self._should_not_connect.is_set():
                        yield (self._last_connection_event)
                        # Wait up to 2 seconds before next iteration. Breaks early if
                        # a new connection has been established (in case of incoming events)
                        self._is_connected.wait(2)
            else:
                try:
                    msg = self._messages.get_nowait()
                    self._messages.task_done()
                    self._messages_lock.release()
                    yield msg
                except queue.Empty:
                    self._messages_lock.release()
                    # If connection dropped while waiting for a message 
                    if not self._is_connected.is_set():
                        continue
                    # Yield TimeoutEvent if n seconds since last
                    if timeout is not None:
                        current_timestamp = int(time.time())
                        if current_timestamp - last_timeout_timestamp > timeout:
                            yield TimeoutEvent()
                    time.sleep(1)

    def on_curves_filters(response):
        if response.ok:
            filters = response.data.filters
            log.info("Currently active curve event filters: %s" % filters)
        else:
            errors = response.errors
            log.error("Failed to get currently active curve event filters: %s" % errors)

    def get_curve_filters(self, callback=on_curves_filters):
        request_id = uuid.uuid4()
        get_filters_msg = RequestCurvesFilters(request_id).to_message()
        with self._messages_lock:
            for _, obj in self._callbacks.items(): 
                if obj.callback_type == GET_CURVE_FILTERS:
                    obj.latest = False
                    # TODO or just del the old callbacks?
            # Callback
            callback = Callback(callback, callback_type=GET_CURVE_FILTERS, latest=True)
            self._callbacks[request_id] = callback
        # Send msg
        msg = json.dumps(get_filters_msg)
        #log.debug(f"Sending message to get latest filters:\n{msg}")
        self._ws.send(msg)


    # def send_get_filters(self, request_id=None):
    #     """
    #     Send a message to the stream requesting the currently active filters.
    #     When the server responds with the filters it will be added to the
    #     message queue that is accessible through
    #     :py:meth:`get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>`,
    #     and the first element of the message will have ``MessageType.FILTERS``.

    #     The server responds with a message that includes the filters and a unique
    #     id. The id in the response can be manually chosen by supplying the
    #     ``request_id`` parameter with an id, which can be useful if you want to
    #     be certain that the filters you get in return are for a specific request.
    #     ``request_id`` must be a uuid.UUID object in version 4.

    #     # TODO remove uuid
    #     Create a uuid as shown below:

    #         >>> import uuid
    #         >>> get_filters_id = uuid.uuid4()

    #     Preset the request_id when requesting the active filters:
    #         >>> import uuid
    #         >>> get_filters_id = uuid.uuid4()
    #         >>> send_get_filters(request_id=get_filters_id)

    #     Find the response related to your message by comparing the id:

    #         >>> import uuid
    #         >>> from energyquantified.events import MessageType
    #         >>> get_filters_id = uuid.uuid4()
    #         >>> send_get_filters(request_id=get_filters_id)
    #         >>> # Compare ID while reading from the stream
    #         >>> for msg_type, msg in eq.events.get_next():
    #         >>>     if msg_type == MessageType.FILTERS:
    #         >>>         if msg.request_id == get_filters_id:
    #         >>>             # ID match so we know which message the response regards

    #     :param request_id: Preset id for the response
    #     :type request_id: ``uuid.UUID`` (v4), optional
    #     """
    #     msg = {"action": "filter.get"}
    #     if request_id is not None:
    #         # Assert uuid and version
    #         _assert_uuid4(request_id)
    #         msg["id"] = str(request_id)
    #     self._ws.send(json.dumps(msg))

    # # TODO remove, this is a test
    # def sub2(self, last_id, request_id=None):
    #     msg = {
    #         "action": "events.get",
    #         "last_id": last_id,
    #     }
    #     if request_id is not None:
    #         msg["id"] = str(request_id)

    #     print(f"sending msg: {msg}")
    #     self._ws.send(json.dumps(msg))

# def _assert_uuid4(id):
#     """
#     Asserts that an id is a valid uuid v4.

#     :param id: The id
#     :type id: ``uuid.UUID``
#     """
#     assert isinstance(id, uuid.UUID), (
#         "Optionally parameter request_id must be type uuid if set"
#     )
#     assert id.version == 4, (
#         f"Expected uuid version 4 but found: {id.version}"
#     )