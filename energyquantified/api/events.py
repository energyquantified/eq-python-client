import uuid
import websocket
import threading
import json
import queue
import time
import os
from energyquantified.events import (
    MessageType,
    EventCurveOptions,
    EventFilterOptions,
    ConnectionEvent,
    EventFilters,
)
from energyquantified.events.connection_event import TIMEOUT, UNKNOWN_ERROR
import random
from energyquantified.parser.events import parse_event_options, parse_event, parse_filters
import atexit
from socket import timeout
from websocket import (
    WebSocketException,
    WebSocketConnectionClosedException,
    WebSocketProtocolException,
    WebSocketBadStatusException,
    WebSocketPayloadException,
)

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
    def __init__(self, ws_url, api_key, last_id_file=None):
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
        self._latest_filters = None
        # Last event id
        self._last_id = None
        self._last_id_file = last_id_file
        if last_id_file is not None:
            self._last_id_lock = threading.Lock()
            self._last_id_timestamp = None
            # Check fille access and try to create if not exists
            self._setup_last_id_file()

            def save_id():
                self._last_id_to_file(write_interval_s=0)

            atexit.register(save_id)

    def _setup_last_id_file(self):
        """
        Check read/write access to file and create if not exists.
        """
        if self._last_id_file is None:
            return
        # Lock
        if os.path.exists(self._last_id_file):
            # Raise error if path exists but it's not a file
            if not os.path.isfile(self._last_id_file):
                raise FileNotFoundError(
                    f"Path last_id_file: '{self._last_id_file}' exists but it is not a file"
                    )
            # Read-access
            if not os.access(self._last_id_file, os.R_OK):
                raise PermissionError(f"Missing read-access to last_id_file: '{self._last_id_file}'")
            # Write-access
            if not os.access(self._last_id_file, os.W_OK):
                raise PermissionError(f"Missing write-access to last_id_file: {self._last_id_file}")
            # Set last id
            self._last_id = self._last_id_from_file()
        else:
            # Try to create parent dirs if not exists
            parent_dir = os.path.dirname(self._last_id_file)
            if not parent_dir:
                parent_dir = "."
            else:
                # Create parent dirs if not exists
                os.makedirs(parent_dir, exist_ok=True)
            if not os.access(parent_dir, os.W_OK):
                    raise PermissionError(
                        f"last_id_file: '{self._last_id_file}' does not exist "
                        f"and missing write-access to parent directory: '{parent_dir}'"
                        )
            # Create file
            with open(self._last_id_file, "w") as f:
                json.dump({"last_id": ""}, f)

    def _set_last_id(self, last_id):
        # Set and return if the current id is None
        if self._last_id is None:
            self._last_id = last_id
            return
        # Check if the new last_id is greater than the current
        # last_id format: str of timestamp and a seq. number separated by dash
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

    def _last_id_from_file(self):
        if self._last_id_file is None:
            return None
        last_id = None
        # Block other access to file
        self._last_id_lock.acquire()
        with open(f"{self._last_id_file}", "r") as f:
            data = json.load(f)
            last_id = data.get("last_id")
        self._last_id_lock.release()
        return last_id

    def _last_id_to_file(self, last_id=None, write_interval_s=120):
        # Ignore if user didn't provide a file path
        if self._last_id_file is None:
            return
        if last_id is None:
            if self._last_id is None:
                return
            last_id = self._last_id
        # Don't write if less than 'write_interval_s' since last
        if self._last_id_timestamp is not None and time.time() < self._last_id_timestamp + write_interval_s:
            return
        # Block other access to file
        self._last_id_lock.acquire()
        with open(self._last_id_file, "r+") as f:
            try:
                data = json.load(f)
            except Exception as e:
                data = {}
            current_last_id = data.get("last_id")
            # Only overwrite if new last_id is greater
            if not current_last_id or current_last_id <= last_id:
                data["last_id"] = last_id
                # Write from start of file
                f.seek(0,0)
                #f.truncate()
                json.dump(data, f)
                # Truncate in case the new data is shorter
                f.truncate()
        self._last_id_timestamp = time.time()
        self._last_id_lock.release()

    def _on_open(self, _ws):
        self._last_connection_event = None
        # Reset reconnect counter on successfull connection
        with self._remaining_reconnect_attempts_lock:
            self._remaining_reconnect_attempts = self._max_reconnect_attempts
        # Flag events
        self._is_connected.set()
        self._done_trying_to_connect.set()
        # Send the last active filters
        if self._latest_filters is not None:
            self._messages.put((MessageType.INFO, "Successfully reconnected to the server, setting previous filters.."))
            try:
                self._ws.send(json.dumps(self._latest_filters))
            except Exception as e:
                self._messages.put((MessageType.ERROR, f"Failed to set previous filters after reconnecting, cause: {e}"))

    def _on_message(self, _ws, message):
        print(f"msg: {message}")
        try:
            msg = json.loads(message)
            msg_tag = msg.pop("type")
            if not MessageType.is_valid_tag(msg_tag):
                # Convert message to info
                if msg_tag.lower() == "message":
                    msg_type = MessageType.INFO
                else:
                    raise ValueError(f"Unknown message type: '{message}'")
            else:
                msg_type = MessageType.by_tag(msg_tag)
            if msg_type == MessageType.EVENT:
                data = parse_event(msg)
                self._set_last_id(data.event_id)
                self._last_id_to_file(last_id=data.event_id)
            elif msg_type == MessageType.FILTERS:
                data = parse_filters(msg)
            elif msg_type == MessageType.INFO:
                data = msg["message"]
            elif msg_type == MessageType.ERROR:
                data = msg
            else:
                raise ValueError(f"Unknown MessageType: {msg_type} for message: {message}")
        except Exception as e:
            msg_type = MessageType.ERROR
            data = f"Failed to parse message: '{message}' from stream, cause: {e}"
        finally:
            self._messages.put((msg_type, data))

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
            self._last_id_to_file(write_interval_s=0)


    def _on_error(self, _ws, error):
        if not isinstance(error, (timeout, ConnectionError, WebSocketException)):
            self._messages.put((MessageType.ERROR, getattr(error, "strerror", str(error))))
            return
        # Set _last_connection_event (only if not already)
        if self._last_connection_event is not None:
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

    def _stream_url(self, include_last_id=True):
        if not include_last_id or self._last_id is None:
            return self._ws_url
        return f"{self._ws_url}/?last-id={self._last_id}"

    def connect(self, last_id=None, timeout=10, max_retries=5):
        """
        Connect to the curve update events stream.

        :param last_id: ID of the latest event received. Used for excluding older events.\
                Takes priority over the id from a potential last_id file.
        :type last_id: str, optional
        :param timeout: The time in seconds to wait for a connection to be established.\
                Also used as the minimum wait-time inbetween reconnect attempts. Defaults to 5.
        :type timeout: int, optional
        :param max_retries: The number of reconnect attempts after each disconnect. The counter\
                is reset whenever a connection is established. Defaults to 5.
        :type max_retries: int, optional
        :return: The obj instance this method was invoked upon, so the APi can be used fluently
        :rtype: :py:class:`energyquantified.events.CurveUpdateEventAPI`
        """
        self._max_reconnect_attempts = max_retries
        # Reset flags
        self._should_not_connect.clear()
        self._done_trying_to_connect.clear()
        self._last_connection_event = None
        #self._connection_closed_by_user.clear()
        # Overwrite potential last_id from file
        if last_id is not None:
            self._last_id = last_id
        # Close if already set
        if self._ws is not None:
            self._ws.close()
        websocket.setdefaulttimeout(timeout)
        self._ws = websocket.WebSocketApp(
            self._stream_url(),
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
                        # Update stream url if this is the first dc after connection
                        self._ws.url = self._stream_url()
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
        while True:
            if not self._is_connected.is_set():
                try:
                    # Block=False since not connected
                    msg = self._messages.get(block=False)
                    yield msg
                    self._messages.task_done()
                except queue.Empty:
                    # Wait if trying to (re)connect
                    self._done_trying_to_connect.wait()
                    # Yield DC ConnectionEvent if not connected and not retrying
                    # ^ either if never connected or exceeded max reconnect attempts
                    if self._should_not_connect.is_set():
                        yield (MessageType.DISCONNECTED, self._last_connection_event)
                        # Wait up to 2 seconds before next iteration. Breaks early if
                        # a new connection has been established (in case of incoming events)
                        self._is_connected.wait(2)
            else:
                try:
                    msg = self._messages.get(timeout=timeout)
                    yield msg
                    self._messages.task_done()
                except queue.Empty:
                    # If connection dropped while waiting for a message 
                    if not self._is_connected.is_set():
                        continue
                    yield (MessageType.TIMEOUT, None)

    def subscribe(self, filters, request_id=None, fill_last_id=False):
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

        :param filters: The filters. Can be a single filter or a list of filters.
        :type filters: list[:py:class:`energyquantified.events.EventFilterOptions` | \
            :py:class:`energyquantified.events.EventCurveOptions`]
        :param request_id: Preset id for the response
        :type request_id: ``uuid.UUID`` (v4), optional
        :param fill_last_id: If last_id is not set in the filters, this can be set to\
            True in order to use subscribe to events after the last_id saved in memory.\
            Does nothing if last_id is set in the filters. Defaults to False.
        :type fill_last_id: bool
        """
        # Validate filters
        assert isinstance(filters, EventFilters)
        is_valid, errors = filters.validate()
        assert is_valid, f"Invalid filters: {filters} for reasons: {errors}"
        # Create message
        subscribe_message = {"action": "filter.set"}
        # TODO request_id from filters OR from params?
        # # Add request id if set
        # if filters.has_request_id():
        #     subscribe_message["id"] = str(request_id)
        # TODO ^request_id from filters OR from params?
        # Add or fill last_id
        if filters.has_last_id():
            subscribe_message["last_id"] = filters.last_id
        elif fill_last_id:
            if self._last_id is not None:
                subscribe_message["last_id"] = self._last_id 
        # Add options for filtering events
        if filters.has_options():
            # TODO must this default to something? or allowed to not send filters?
            event_options = list(options.to_dict() for options in filters.options)
            subscribe_message["filters"] = event_options
        # Update latest filters before setting id # TODO do this in response instead?
        self._latest_filters = subscribe_message
        # Validate and set request id
        if request_id is not None:
            # Assert that request id is an uuid and correct version
            _assert_uuid4(request_id)
            subscribe_message["id"] = str(request_id)
        subscribe_message = json.dumps(subscribe_message)
        self._ws.send(subscribe_message)

    def send_get_filters(self, request_id=None):
        """
        Send a message to the stream requesting the currently active filters.
        When the server responds with the filters it will be added to the
        message queue that is accessible through
        :py:meth:`get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>`,
        and the first element of the message will have ``MessageType.FILTERS``.

        The server responds with a message that includes the filters and a unique
        id. The id in the response can be manually chosen by supplying the
        ``request_id`` parameter with an id, which can be useful if you want to
        be certain that the filters you get in return are for a specific request.
        ``request_id`` must be a uuid.UUID object in version 4.

        Create a uuid as shown below:

            >>> import uuid
            >>> get_filters_id = uuid.uuid4()

        Preset the request_id when requesting the active filters:
            >>> import uuid
            >>> get_filters_id = uuid.uuid4()
            >>> send_get_filters(request_id=get_filters_id)

        Find the response related to your message by comparing the id:

            >>> import uuid
            >>> from energyquantified.events import MessageType
            >>> get_filters_id = uuid.uuid4()
            >>> send_get_filters(request_id=get_filters_id)
            >>> # Compare ID while reading from the stream
            >>> for msg_type, msg in eq.events.get_next():
            >>>     if msg_type == MessageType.FILTERS:
            >>>         if msg.request_id == get_filters_id:
            >>>             # ID match so we know which message the response regards

        :param request_id: Preset id for the response
        :type request_id: ``uuid.UUID`` (v4), optional
        """
        msg = {"action": "filter.get"}
        if request_id is not None:
            # Assert uuid and version
            _assert_uuid4(request_id)
            msg["id"] = str(request_id)
        self._ws.send(json.dumps(msg))

    def sub2(self, last_id, request_id=None):
        msg = {
            "action": "events.get",
            "last_id": last_id,
        }
        if request_id is not None:
            msg["id"] = str(request_id)

        print(f"sending msg: {msg}")
        self._ws.send(json.dumps(msg))

def _assert_uuid4(id):
    """
    Asserts that an id is a valid uuid v4.

    :param id: The id
    :type id: ``uuid.UUID``
    """
    assert isinstance(id, uuid.UUID), (
        "Optionally parameter request_id must be type uuid if set"
    )
    assert id.version == 4, (
        f"Expected uuid version 4 but found: {id.version}"
    )