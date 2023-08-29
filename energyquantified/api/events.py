import uuid
import websocket
import threading
import json
import queue
import sys
import time
import logging
import os
import re
from energyquantified.events import (
    EventCurveOptions,
    EventFilterOptions,
    ConnectionEvent,
    CurveUpdateEvent,
    EventType,
    TimeoutEvent,
)
from energyquantified.events.responses import (
    CurvesSubscribeResponse,
    CurvesFiltersResponse,
)
from energyquantified.events.messages import (
    RequestCurvesSubscribe,
    RequestCurvesFilters,
    ServerMessageMessage,
    ServerMessageCurveEvent,
    ServerResponse,
    ServerResponseCurvesSubscribe,
    ServerResponseCurvesFilters,
    ServerResponseError,
    ServerMessageType,
)
from energyquantified.events.callback import Callback, SUBSCRIBE_CURVES, GET_CURVE_FILTERS
from energyquantified.events.connection_event import TIMEOUT
import random
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

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


class EventsAPI:
    """
    The curve events API client.

    Wraps the Energy Quantified websocket API for curve events. Handles validation,
    network errors, and parsing of API responses.

    :param ws_url: The root URL for the events websocket API
    :type ws_url: str
    :param api_key: The API key for your user account
    :type api_key: str

    **Basic usage:**

    Access these operation via an instance of the
    :py:class:`energyquantified.EnergyQuantified` class:

        >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd)

    Connect to the stream and subscribe to curve events:

        >>> # Connect
        >>> events = eq.events.connect()
        >>> # Subscribe to curve events in Germany
        >>> filters = EventFilterOptions(areas=[Area.DE])
        >>> eq.events.subscribe_curve_events(filters=filters)
        >>> # Loop over events as they come
        >>> for event in events.get_next():
        >>>     # Handle events

    """

    def __init__(self, ws_url, api_key):
        self._ws_url = ws_url
        self._api_key = api_key
        self._ws = None
        self._wst = None
        self._messages = queue.Queue()
        self._is_connected = threading.Event()
        self._last_connection_event = ConnectionEvent(
            event_type=EventType.DISCONNECTED,
            status_code=1000,
            message="Not connected to the server"
        )
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
        Creates a 'last_id'-file if the file does not already exist. If exists, update
        last_id in memory with the value from the file.
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

    def _last_id_to_file(self, last_id=None, write_interval_s=30):
        """
        Saves the last_id to disk if the file path exists, last_id (or self._last_id)
        is not None, and it's at least 'write_interval_s' seconds since last save.

        :param last_id: The id (defaults to self._last_id if None)
        :type last_id: str, optional
        :param write_interval_s: The minimum number of seconds since last write, defaults to 30
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
            data["last_id"] = last_id
            # Write from start of file
            f.seek(0,0)
            json.dump(data, f)
            # Truncate in case the new data is shorter
            f.truncate()
        self._last_id_timestamp = time.time()

    def _on_open(self, _ws):
        """
        Callback function that is called whenever a new websocket connection is established.
        """
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
                self._ws.send(json.dumps(self._latest_curves_subscribe_message))

    def _on_message(self, _ws, message):
        """
        Callback func that is called whenever there is a new message on the ws.
        """
        with self._messages_lock:
            message_json = json.loads(message)
            #print(f"msg: {message_json}")
            msg_type_tag = ServerMessageType.tag_from_json(message_json)
            if not ServerMessageType.is_valid_tag(msg_type_tag):
                # Unkown type, skip. Might be a new type that is not supported in this version.
                return
            msg_obj = ServerMessageType.by_tag(msg_type_tag).model.from_message(message_json)
            # Check type
            if isinstance(msg_obj, ServerMessageMessage):
                self._message_handler(msg_obj.message)
            elif isinstance(msg_obj, ServerMessageCurveEvent):
                if self._is_subscribed_curves.is_set():
                    event = msg_obj.event
                    self._messages.put(event)
            elif isinstance(msg_obj, ServerResponse):
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
                    if callback.latest and subscribe_response.status:
                        self._is_subscribed_curves.set()
                elif isinstance(msg_obj, ServerResponseCurvesFilters):
                    filters_response = CurvesFiltersResponse(
                        status=msg_obj.status,
                        data=msg_obj.data,
                        errors=msg_obj.errors,
                    )
                    callback.callback(filters_response)
                elif isinstance(msg_obj, ServerResponseError):
                    # Should only really happen if server fails to parse 'type' (so shouldnt happen)
                    # TODO what if callback exists for request_id?
                    self._error_handler(". ".join[[err.capitalize() for err in msg_obj.errors]])
                else:
                    # Might be a new response type that is not supported in this version. Skip.
                    pass
            else:
                # Might be a new type with parser not implemented in this version. Skip.
                pass

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
            self._error_handler(getattr(error, "strerror", str(error)))
            return
        #  self._last_connection_event should only be set once for each time connecting
        if self._last_connection_event is not None:
           return
        if isinstance(error, timeout):
            self._last_connection_event = ConnectionEvent(
                event_type=EventType.DISCONNECTED,
                status=TIMEOUT,
                message=str(error)
            )
        elif isinstance(error, ConnectionError):
            # TODO if Errno111 -> only use message (not status code)
            status_code = error.errno
            error_message = error.strerror
            self._last_connection_event = ConnectionEvent(
                event_type=EventType.DISCONNECTED,
                status_code=status_code,
                message=error_message
            )
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
                event_type=EventType.DISCONNECTED,
                status_code=status_code,
                message=str(error),
            )

    def connect(self, last_id_file=None, timeout=10, reconnect_attempts=5):
        """
        Connect to the curve update events stream.

        To keep track of the last event received in between sesssions, supply
        the ``last_id_file`` parameter with a file path. The file will be
        created for you if it does not already exist. The id from the last
        event received will be stored in the file, and the client will
        automatically request old events (starting from the saved id) the next
        time you connect. This is useful in the case of disconnects or
        unexpected terminations.

            >>> eq.events.connect(last_id_file="last_id_file.json")

        The file can also be created inside a folder (which will be created for
        you if it does not already exist):

            >>> eq.events.connect(
            >>>     last_id_file="folder_name/last_id_file.json"
            >>> )

        Optionally supply the ``timeout`` parameter with an integer to change the
        default number of seconds to wait for a connection to be established
        before failing. It is not recommended to change this too low, as
        connecting always takes a certain amount of time at minimum.

        The client tries to automatically reconnect if the connections drops.
        The number of reconnect attempts can be set through the
        ``reconnect_attempts`` parameter.

        :param last_id_file: A file path to a file that keeps track of the last\
                       event id received from the curve events stream
        :type last_id_file: str, optional
        :param timeout: The time in seconds to wait for a connection to be\
            established. Also used as the minimum wait-time inbetween reconnect\
                attempts. Defaults to 10.
        :type timeout: int, optional
        :param reconnect_attempts: The number of reconnect attempts after each\
            disconnect. The counter is reset whenever a connection is\
                established. Defaults to 5.
        :type reconnect_attempts: int, optional
        :return: The obj instance this method was invoked upon, so the API\
            can be used fluently
        :rtype: :py:class:`energyquantified.events.EventsAPI`
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
        log.debug("Subscribing to events at url: %s", self._ws_url)
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
        self._last_connection_event = ConnectionEvent(
            event_type=EventType.DISCONNECTED,
            status_code=1000,
            message="Connection closed by user"
        )
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
        Default callback function for handling a subscribe response.

        :param response: The response from subscribing to curve events
        :type response: :py:class:`energyquantified.events.CurvesSubscribeResponse`
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

        First make sure to connect
        (see :py:meth:`connect() <energyquantified.api.EventsAPI.connect>`):

            >>> eq = EnergyQuantified(
            >>>     api_key="aaaa-bbbb-cccc-dddd
            >>> )
            >>> eq.events.connect(last_id_file="last_id_file.json")

        Create a filter and subscribe:

            >>> filters = [
            >>>     EventFilterOptions(event_types="CURVE_UPDATE")
            >>> ]
            >>> eq.events.subscribe_curve_events(filters=filters)

        If a custom callback function is not provided, the default ``on_curves_subscribe``
        logs when a response is received.

        :param filters: The filters. Can be a single filter or a list of filters.
        :type filters: list[:py:class:`energyquantified.events.EventFilterOptions`, \
            :py:class:`energyquantified.events.EventCurveOptions`]
        :param last_id: ID of the latest event received. Used for ex-/including older events.\
                Takes priority over the id from a potential last_id file. Set to "keep"\
                in order to use the last id from memory.
        :type last_id: str, optional
        :param callback: Set a custom callback function to handle the subscribe response. Defaults to\
            :py:meth:`on_curves_subscribed() <energyquantified.api.EventsAPI.on_curves_subscribed>`.
        :type callback: Callable, optional
        :return: The obj instance this method was invoked upon, so the APi can be used fluently
        :rtype: :py:class:`energyquantified.events.EventsAPI`
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
            # Use id from memory if 'keep'
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
        return self

    def on_curves_filters(response):
        """
        Default callback function for handling a filters response.

        :param response: The response from requesting active curve event filters
        :type response: :py:class:`energyquantified.events.CurvesFiltersResponse`
        """
        if response.ok:
            filters = response.data.filters
            log.info("Active curve event filters: %s" % filters)
        else:
            errors = response.errors
            log.error("Failed to get active curve event filters: %s" % errors)

    def get_curve_filters(self, callback=on_curves_filters):
        """
        Request the active curve event filters.

        First make sure to connect
        (see :py:meth:`connect() <energyquantified.api.EventsAPI.connect>`):

            >>> from energyquantified import EnergyQuantified
            >>> eq = EnergyQuantified(
            >>>     api_key="aaaa-bbbb-cccc-dddd
            >>> )
            >>> eq.events.connect(last_id_file="last_id_file.json")

        Request the active curve event filters:

            >>> eq.events.get_curve_filters()

        If a custom callback function is not provided, the default ``on_curves_filters``
        logs when a response is received. The callback function must take in one parameter
        of type :py:class:`CurvesFiltersResponse <energyquantified.events.CurvesFiltersResponse>`.

        :param callback: Set a custom callback function to handle the subscribe response. Defaults to\
            :py:meth:`on_curves_filters() <energyquantified.api.EventsAPI.on_curves_filters>`.
        :type callback: Callable, optional
        :return: The obj instance this method was invoked upon, so the APi can be used fluently
        :rtype: :py:class:`energyquantified.events.EventsAPI`
        """
        request_id = uuid.uuid4()
        get_filters_msg = RequestCurvesFilters(request_id).to_message()
        with self._messages_lock:
            for _, obj in self._callbacks.items():
                if obj.callback_type == GET_CURVE_FILTERS:
                    obj.latest = False
            # Callback
            callback = Callback(callback, callback_type=GET_CURVE_FILTERS, latest=True)
            self._callbacks[request_id] = callback
        # Send msg
        msg = json.dumps(get_filters_msg)
        self._ws.send(msg)
        return self

    def get_next(self, timeout=None):
        """
        Returns a generator over new events, and blocks while waiting for new.

        Every event returned is one of the following types:
        1: :py:class:`energyquantified.events.CurveUpdateEvent`
        2: :py:class:`energyquantified.events.ConnectionEvent`
        3: :py:class:`energyquantified.events.TimeoutEvent`

        The ``event_type`` attribute is common for all events (type:
        :py:class:`EventType <energyquantified.events.EventType>`) and is
        used to check the type of an event.

        :py:class:`CurveUpdateEvent <energyquantified.events.CurveUpdateEvent>`
        is the model that describes change in data for a curve.
        :py:class:`ConnectionEvent <energyquantified.events.ConnectionEvent>`
        describes a new event related to the connection.

        >>> for event in eq.events.get_next(timeout=10):
        >>>     if event.event_type == EventType.CURVE_UPDATE:
        >>>         # Data in a curve is updated, let's load the new data
        >>>         data = event.load_data()
        >>>         continue
        >>>
        >>>     if event.event_type == EventType.DISCONNECTED::
        >>>         # Not connected
        >>>         log.error("Disconnected")
        >>>         # Wait a short moment before reconnecting
        >>>         time.sleep(10)
        >>>         eq.events.connect()
        >>>         continue
        >>>
        >>>     if event.event_type == EventType.TIMEOUT:
        >>>         # Nothing happened in the last 10 (timeout param) seconds
        >>>         # Use this event to act in between events during quiet times
        >>>         pass

        :param timeout: The number of seconds to wait (blocking) for a\
            new message, yielding a ``TimeoutEvent`` if no new event occurs.\
                Waits indefinetly if timeout is None. Defaults to None.
        :type timeout: int, optional
        :yield: A generator of events. Blocks while waiting for a new event.
        :rtype: :py:class:`energyquantified.events.CurveUpdateEvent`,\
            :py:class:`energyquantified.events.ConnectionEvent`,\
            :py:class:`energyquantified.events.TimeoutEvent`
        """
        last_event_timestamp = None
        while True:
            with self._messages_lock:
                try:
                    event = self._messages.get_nowait()
                    self._messages.task_done()
                except queue.Empty:
                    event = None
            # Yield event from queue
            if event is not None:
                last_event_timestamp = time.time()
                # Update last_id if curve event
                if isinstance(event, CurveUpdateEvent):
                    self._update_last_id(event.event_id)
                    self._last_id_to_file(event.event_id)
                yield event
                continue
            # Empty event queue
            # Check if connected (TimeoutEvent) or not (wait)
            if self._is_connected.is_set():
                if timeout is not None:
                    if last_event_timestamp is None:
                        last_event_timestamp = time.time()
                    else:
                        current_timestamp = time.time()
                        if current_timestamp - last_event_timestamp >= timeout:
                            last_event_timestamp = current_timestamp
                            yield TimeoutEvent()
                time.sleep(0.1)
            # Not connected
            else:
                # Reset last_event_timestamp
                if timeout is not None:
                    last_event_timestamp = None
                # Wait if currently trying to connect
                self._done_trying_to_connect.wait()
                # If stopped trying to connect (or never started), yield
                # ConnectionEvent
                if self._should_not_connect.is_set():
                    yield self._last_connection_event.copy()
                    # Wait up to two seconds. Break early if connected.
                    # ^This is the interval at which ConnectionEvents are sent
                    self._is_connected.wait(2)
