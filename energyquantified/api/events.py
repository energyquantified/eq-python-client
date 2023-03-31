
import websocket
import threading
import json
import queue
import time
import os
from energyquantified.events import (MessageType,
                                     UnavailableEvent,
                                     DisconnectedEvent,
                                     EventCurveOptions,
                                     EventFilterOptions,
                                     ConnectionEvent,
                                     WebSocketError)
from energyquantified.parser.events import parse_event_options, parse_event
import atexit
from socket import timeout

BASE_URL = f"ws://localhost:8080/events/curves"
#TEST_URL = f"ws://192.168.1.199/events/curves"

class CurveUpdateEventAPI:
    """
    The curve events API client.

    Wraps the Energy Quantified websocket API for curve events. Handles validation,
    network errors, and parsing of API responses.
    
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
        >>> for msg_type, event in ws.get_next():
        >>>     if msg_type == MessageType.EVENT:
        >>>         # Optionally load event data from API
        >>>         data = event.load_data()

    At least one filter (of type
    :py:class:`energyquantified.events.event_options.EventFilterOptions`
    or :py:class:`energyquantified.events.event_options.EventFilterOptions`)
    must be set in order to receive curve events:

        >>> from energyquantified import EnergyQuantified
        >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd)
        >>> ws_client = eq.events.connect()
        >>> from energyquantified.events.event_options import EventFilterOptions
        >>> To receive all UPDATE-events for Germany
        >>> filter = EventFilterOptions().set_areas("DE").set_event_types("UPDATE")
        >>> ws_client.subscribe(filter)
        
    To keep track of the last event received between sesssions, supply the
    **last_id_file** parameter with a file path. The file will be created 
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

    def __init__(self, api_key, last_id_file=None):
        self._api_key = api_key
        self._ws = None
        self._wst = None
        self._messages = queue.Queue()
        self._is_connected = threading.Event()
        #self._is_connecting = threading.Event()
        #self._not_connecting = threading.Event()
        #self._done_try_connecting = threading.Event()
        #self._done_try_connecting.set()
        #self._should_try_connect = threading.Event()
        #self._should_try_connect.set()
        self._last_connection_event = ConnectionEvent(status_code=1000, message="Not connected to the server")
        self._should_not_connect = threading.Event()
        self._done_trying_to_connect = threading.Event()
        self._done_trying_to_connect.set()
        #self._connection_closed_by_user = threading.Event()
        self._reconnect_counter = 0
        self._reconnect_counter_lock = threading.Lock()
        #self._is_connected.clear()
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
        if self._last_id is None or last_id > self._last_id:
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
        # TODO docs write_interval_s: minimum time since last write
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
        with self._reconnect_counter_lock:
            self._reconnect_counter = -1
        # Flag events
        self._is_connected.set()
        self._done_trying_to_connect.set()
        # Send the last active filters
        if self._latest_filters is not None:
            self._messages.put((MessageType.INFO, "Successfully reconnected to the server, setting previous filters.."))
            try:
                self._ws.send(self._latest_filters)
            except Exception as e:
                print(f"Failed to send filters after reconnecting, e: {e}")

    def _on_message(self, _ws, message):
        msg = json.loads(message)
        msg_tag = msg.pop("type")
        if not MessageType.is_valid_tag(msg_tag):
            # Convert message to info
            if msg_tag.lower() == "message":
                msg_type = MessageType.INFO
            else:
                raise ValueError(f"Failed to parse message '{message}': unkown message type")
        else:
            msg_type = MessageType.by_tag(msg_tag)
        if msg_type == MessageType.EVENT:
            data = parse_event(msg)
            self._set_last_id(data.event_id)
            self._last_id_to_file(last_id=data.event_id)
        elif msg_type == MessageType.FILTERS:
            data = list(parse_event_options(options) for options in msg["filters"])
        elif msg_type == MessageType.INFO:
            try:
                data = msg["message"]
            except Exception as e:
                print(f"e: {e}")
                raise e
        else:
            raise ValueError(f"Failed to parse message: '{message}' with type: '{msg_type}'")
        self._messages.put((msg_type, data))

    def _on_ping(self, _ws, *args):
        print(f"on_ping: {args}")
    def _on_pong(self, _ws, *args):
        print(f"on_pong: {args}")

    def _on_close(self, _ws, status_code, msg):
        print(f"on close, status_code: {status_code}, msg: {msg}")
        if self._is_connected.is_set():
            self._is_connected.clear()
            if self._last_connection_event is not None:
                self._last_connection_event = ConnectionEvent(status_code=status_code, message=msg)
            # TODO self._last_connection_event = ConnectionEvent(status_code=status_code, message=msg) 
            #self._messages.put((MessageType.DISCONNECTED, DisconnectedEvent(status_code=status_code, message=msg)))
            #self._messages.put((MessageType.UNAVAILABLE, UnavailableEvent(status_code=status_code, server_message=msg)))
            self._last_id_to_file(write_interval_s=0)
            #if status_code is not None:
                #self.connect(timeout=3, max_retries=3)

    def _on_error(self, _ws, error):
        print(f"on_error: {error}")
        print(error.__dict__)
        print(dir(error))
        if isinstance(error, (ConnectionRefusedError, timeout)):
            #self._done_try_connecting.set()
            # TODO
            pass
        #print(f"on_error, error: {error}, type: {type(error)}")
        #import traceback
        #print(traceback.extract_stack(error))

    def _stream_url(self, include_last_id=True):
        url = BASE_URL
        # Return base path of not including last_id
        if not include_last_id:
            return url
        # last_id default to '$'
        last_id = self._last_id if self._last_id is not None else "$"
        return f"{BASE_URL}/?last-id={last_id}"

    def connect(self, last_id=None, timeout=3, max_retries=3):
        """
        Connect to the curve update events stream.

        Args:
            timeout (int, required): The time in seconds to wait inbetween (re)connect attempts. Defaults to 5.
            max_retries (int, optional): Maximum number of attempts to (re)connect before closing the connection.
             The attempts counter reset when a connection is established.  Defaults to 5.

        Returns:
            CurveUpdateEventAPI: Returns the instance once connected to the stream server.
        """
        # Reset flags
        self._should_not_connect.clear()
        self._done_trying_to_connect.clear()
        self._last_connection_event = None
        #self._connection_closed_by_user.clear()
        # Overwrite potential last_id from file
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
            on_ping=self._on_ping,
            on_pong=self._on_pong,)
    
        def _ws_thread():
            while not self._should_not_connect.is_set():
                start_time = time.time()
                # Blocking until dc
                self._ws.run_forever()
                # Safely acquire the reconnect_counter
                with self._reconnect_counter_lock:
                    # Update stream url if this is the first dc after connection
                    if self._reconnect_counter == -1:
                        self._ws.url = self._stream_url()
                    # Increment counter
                    self._reconnect_counter += 1
                    reconnect_counter = self._reconnect_counter
                # Stop trying if max attemps exceeded
                if reconnect_counter >= max_retries:
                    #if self._last_connection_event is not None:
                    #    self._last_connection_event = ConnectionEvent()
                    # TODO dont queue
                    #self._messages.put((MessageType.UNAVAILABLE, "Exceeded max reconnect attempts"))
                    # Exceeded max retries, should not try to reconnect
                    self._should_not_connect.set()
                    self._done_trying_to_connect.set()
                    return
                # Wait up to delta seconds longer than the default websocket timeout
                delta = 0.5
                time.sleep(delta + max(0, timeout - (time.time() - start_time)))

        self._wst = threading.Thread(target=_ws_thread)
        self._wst.daemon = True
        self._wst.start()

        self._done_trying_to_connect.wait()
        return self

    def close(self):
        """
        Close the stream connection (if open) and disable automatic reconnecting.
        """
        self._last_connection_event = ConnectionEvent(status_code=1000, message="Connection closed by user")
        self._should_not_connect.set()
        #self._connection_closed_by_user.set()
        self._ws.close()

    def get_next(self, timeout=None):
        """
        Loop over received messages, and blocks while waiting for new.

        :param timeout: The number of seconds to wait (blocking) for a new message,\
                yielding a MessageType.TIMEOUT if the timeout occurs. Waits indefinetly\
                if timeout is None. Defaults to None.
        :type timeout: int, optional
        :yield: A tuple of two items; the first item is a MessageType describing the\
                second item
        :rtype: Tuple[MessageType, Union[CurveUpdateEvent, DisconnectedEvent str, None]]
        """
        remaining_dc_events = 5
        while True:
            # if self.is_connecting: time.sleep(0.1) continue
            if not self._is_connected.is_set():
                #self._messages.empty
                try:
                    self._messages.empty
                    msg = self._messages.get(block=False)
                    yield msg
                    self._messages.task_done()
                except queue.Empty:
                    if not self._done_trying_to_connect.is_set():
                        # Wait while trying to (re)connect
                        self._done_trying_to_connect.wait()
                    else:
                        # Stop get_next() loop if no action from user
                        if remaining_dc_events == 0:
                            return
                        yield (MessageType.DISCONNECTED, self._last_connection_event)
                        # Decrement dc events counter if user doesn't try to reconnect
                        if self._should_not_connect.is_set():
                            remaining_dc_events -= 1
                        # TODO replace sleep with event.wait(2) - so it can break earlier
                        time.sleep(2)
            else:
                remaining_dc_events = 5
                try:
                    msg = self._messages.get(timeout=timeout)
                    yield msg
                    self._messages.task_done()
                except queue.Empty:
                    # If connection dropped while waiting for a message 
                    if not self._is_connected.is_set():
                        continue
                    yield (MessageType.TIMEOUT, None)

    def subscribe(self, filters):
        """
        Subscribe to curve events matching any of the filters.

        :param filters: The filters to use. Can be a single filter or a list of filters.
        :type filters: Union[EventFilterOptions, EventCurveOptions, List[Union[EventFilterOptions, EventCurveOptions]]]
        """
        if not isinstance(filters, (list, tuple, set)):
            filters = [filters]
        assert all(isinstance(eventOptions, (EventFilterOptions, EventCurveOptions)) for eventOptions in filters)
        filter_list = list(eventFilter.to_dict() for eventFilter in filters)
        filters_msg = json.dumps(
            {"action": "filter.set",
            "filters": filter_list},)
        print(f"filters_Msg: {filters_msg}")
        # TODO set latest here or confirm after get_filters()?
        self._latest_filters = filters_msg
        # TODO try/catch or not?
        print("sending new")
        self._ws.send(filters_msg)
        # try:
        #     self._ws.send(filters_msg)
        # except Exception as e:
        #     pass

    def send_get_filters(self):
        """
        Request the curently active filters from the stream.
        """
        # TODO try/catch or not?
        self._ws.send(json.dumps({"action": "filter.get"}))
