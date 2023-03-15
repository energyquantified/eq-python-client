
import websocket
import threading
import json
import queue
import time
import os
from energyquantified.events.events import MessageType, DisconnectEvent
from energyquantified.events.event_options import EventCurveOptions, EventFilterOptions
from energyquantified.parser.events import parse_event_options, parse_event
import atexit

class CurveUpdateEventAPI:

    def __init__(self, api_key, last_id_file):
        self._api_key = api_key
        self._ws = None
        self._wst = None
        self._messages = queue.Queue()
        self._is_connected = threading.Event()
        self._is_connected.clear()
        self._latest_filters = None
        # Last event id
        self._last_id_file = last_id_file
        self._last_id = None
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
        self._is_connected.set()
        if self._latest_filters is not None:
            self._messages.put((MessageType.INFO, "Successfully reconnected to the server, setting previous filters.."))
            self._ws.send(self._latest_filters)

    def _on_message(self, _ws, message):
        msg = json.loads(message)
        msg_type = MessageType.by_tag(msg.pop("type"))
        if msg_type == MessageType.EVENT:
            data = parse_event(msg)
            self._set_last_id(data.event_id)
            self._last_id_to_file(last_id=data.event_id)
        elif msg_type == MessageType.FILTERS:
            data = list(parse_event_options(options) for options in msg["filters"])
        elif msg_type == MessageType.INFO or MessageType.MESSAGE:
            data = msg["message"]
        else:
            raise ValueError(f"Failed to parse message: '{message}' with type: '{msg_type}'")
        self._messages.put((msg_type, data))

    def _on_close(self, _ws, status_code, msg):
        if self._is_connected.is_set():
            self._is_connected.clear()
            self._messages.put((MessageType.DISCONNECT, DisconnectEvent(status_code=status_code, message=msg)))
            self._last_id_to_file(write_interval_s=0)
            if status_code is not None:
                self.subscribe(reconnect_delay=10, max_retries=5)

    def _on_error(self, _ws, error):
        print(f"on_error, error: {error}")

    def _on_ping(self, _ws, msg):
        #print(f"on_ping, msg: {msg}")
        pass
        
    def _on_pong(self, _ws, msg):
        #print(f"on_pong, msg: {msg}")
        pass

    def subscribe(self, reconnect_delay=5, max_retries=5):
        """
        Subscribe to the curve update events stream.

        Args:
            reconnect_delay (int, optional): The time in seconds to wait inbetween (re)connect attempts. Defaults to 5.
            max_retries (int, optional): Maximum number of attempts to (re)connect before closing the connection.
             The attempts counter reset when a connection is established.  Defaults to 5.

        Returns:
            CurveUpdateEventAPI: Returns the instance once connected to the stream server.
        """
        last_id = self._last_id
        if last_id is None:
            last_id = ""
        # Close if already set
        if self._ws is not None:
            self._ws.close()
        self._ws = websocket.WebSocketApp(
            f"ws://localhost:8080/events/curves/?last-id={last_id}",
            header={
                "X-API-KEY": self._api_key
            },
            on_open=self._on_open,
            on_message=self._on_message,
            on_close=self._on_close,
            on_error=self._on_error,
            on_ping=self._on_ping,
            on_pong=self._on_pong)
        
        def _ws_thread():
            retry_counter = 0
            while not self._is_connected.is_set():
                if retry_counter == max_retries:
                    self._messages.put((MessageType.UNAVAILABLE, "Exceeded max retry attempts"))
                    os._exit(1)
                self._ws.run_forever()
                self._is_connected.wait(reconnect_delay)
                retry_counter += 1

        self._wst = threading.Thread(target=_ws_thread)
        self._wst.daemon = True
        self._wst.start()

        while not self._is_connected.is_set():
            time.sleep(1)
        
        return self

    def close(self):
        """
        Close the stream connection.
        """
        self._ws.close()

    def get_next(self, timeout=5):
        """
        Wait at most 'timeout' seconds for a new message. The wait is blocking.

        Args:
            timeout (int, optional): The maximum number of seconds to wait. Defaults to 5.

        Yields:
            tuple(MessageType, Union[CurveUpdateEvent, DisconnectEvent, str, ..]): 
                Yields a tuple of two elements - MessageType at index 0 describes the second item.
        """
        while True:
            try:
                msg = self._messages.get(timeout=timeout)
                yield msg
                self._messages.task_done()
            except queue.Empty:
                if not self._is_connected.is_set():
                    yield (MessageType.UNAVAILABLE, "Could not receive data from server")
                else:
                    yield (MessageType.TIMEOUT, None)

    def set_filters(self, *filters):
        """
        Set new filters for the curve update events stream.

        Args:
            *filters: (EventFilterOptions, EventCurveOptions, required): Filters to use.

        """
        assert all(isinstance(eventOptions, (EventFilterOptions, EventCurveOptions)) for eventOptions in filters)
        filter_list = list(eventFilter.to_dict() for eventFilter in filters)
        filters_msg = json.dumps(
            {"action": "filter.set",
            "filters": filter_list})
        # TODO set latest here or confirm after get_filters()?
        self._latest_filters = filters_msg
        self._ws.send(filters_msg)

    def send_get_filters(self):
        """
        Request the curently active filters from the stream.
        """
        self._ws.send(json.dumps({"action": "filter.get"}))
