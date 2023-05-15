Curve update events
===========

This page shows how to load curve events. The examples below expects you to have an initialized
instance of the client called ``eq``.

Operations described here are available under ``eq.events.*``


Prerequisites
---------------------

Curve events
~~~~~~~~~~~~~~

A curve event (:py:class:`~energyquantified.events.events.CurveUpdateEvent`) is created whenever
data for a :py:class:`~energyquantified.metadata.Curve` is changed. Events provide information
about what kind of operation was done (e.g., delete or update) on the curve, timestamps of
the first and last affected values, and the total number of affected values. It also includes an
:py:class:`~energyquantified.metadata.Instance` if relevant.


If values were updated at 15-minute frequency for Germany's consumption normal at
``2023-01-01 01:15`` and ``2023-01-01 01:45``, the following event would be produced:

    >>> <CurveUpdateEvent:
    >>>     event_id="123"
    >>>     curve="DE Consumption MWh/h 15min Normal",
    >>>     event_type=EventType.UPDATE,
    >>>     begin="2023-01-01 01:15,
    >>>     end="2023-01-01 02:00",
    >>>     num_values=2>

WebSocket and filters
~~~~~~~~~~~~~~

Curve events are streamed in real-time from EQ's WebSocket API, accessible from ``eq.events``. In order
to receive events from the stream, one must first send a filter - specifying which curves to receive
events for. Filters are specified in two ways:

- :py:class:`~energyquantified.events.event_options.EventCurveOptions`: By curve a list of curves
- :py:class:`~energyquantified.events.event_options.EventFilterOptions`: Providing search filters similar
  to the curve search

The filters can be updated on the fly while listening to the stream, due to websockets
bidirectional communication protocol.

Message and event types
~~~~~~~~~~~~~~

Data from the stream is not limited to events, but can be informational or error messages. Accessing
new events with :py:meth:`eq.events.get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>` will
get you a tuple of two objects;

#. A :py:class:`~energyquantified.events.events.MessageType` describing the second item
#. The event or message received (e.g., :py:class:`~energyquantified.events.events.CurveUpdateEvent`)


If the latest message is a curve event the pair will look like: (``MessageType.EVENT``,
:py:class:`~energyquantified.events.events.CurveUpdateEvent`), and if it is just a simple message
from the server it would be (``MessageType.INFO``, "Hello, client.").

Quickstart
---------------------

Connect to the stream and subscribe to events
~~~~~~~~~~~~~~

Connect to the stream by calling
:py:meth:`eq.events.connect() <energyquantified.api.CurveUpdateEventAPI.connect>`. Note that this
blocks program execution until a connection to the stream has been established, or exceeded max attempts
at doing so.

    >>> eq.events.connect()

After successfully connecting to the stream you will immediately start to receive messages. Handle messages as
they come with :py:meth:`eq.events.get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>`:

    >>> eq.events.connect()
    >>> for msg_type, data in eq.events.get_next():
    >>>     if msg_type == MessageType.INFO:
    >>>         print(f"New message from the stream: {data}")

Note that you **must subscribe with a filter in order to start receiving events**. The example below
illustrates how to subscribe to events that concern actual-data in Germany:

    >>> from energyquantified.events.event_options import EventFilterOptions
    >>> from energyquantified.events.events import MessageType
    >>> eq.events.connect()
    >>> # Create filter for actual-data in Germany
    >>> filter = EventFilterOptions()
    >>>             .set_areas("DE")
    >>>             .set_data_types("ACTUAL")
    >>> # Subscribe with the filter
    >>> eq.events.subscribe(filter)
    >>> for msg_type, data in eq.events.get_next():
    >>>     if msg_type == MessageType.EVENT:
    >>>         print(f"New event: {data}")
    >>>     elif msg_type == MessageType.INFO:
    >>>         print(f"New message from the stream: {data}")

Network error and reconnecting
~~~~~~~~~~~~~~

The client will automactically try to reconnect to the stream if the connection drops, unless the
user manually closes it with :py:meth:`eq.events.close() <energyquantified.api.CurveUpdateEventAPI.close>`.


If the client exceeds the maximum number of reconnect attempts to the stream, you start to get
``MessageType.UNAVAILABLE`` from ``eq.events.get_next()``. Handling five consecutive
``MessageType.UNAVAILABLE`` messages causes ``eq.events.get_next()`` to break the loop. If you want
to reconnect then this is your signal, and please wait one minute before retrying by including
a sleep as shown below: # TODO
    
    >>> from energyquantified.events.events import MessageType
    >>> import time
    >>> eq.events.connect()
    >>> for msg_type, data in eq.events.get_next():
    >>>     if msg_type == MessageType.UNAVAILABLE:
    >>>         # Wait 60 seconds before reconnecting
    >>>         time.sleep(60)
    >>>         # Try to reconnect
    >>>         eq.events.connect()

Note that you can always access previously received and unhandled events in ``eq.events.get_next()``,
regardless of connection status.

Closing the connection manually with
:py:meth:`eq.events.close() <energyquantified.api.CurveUpdateEventAPI.close>` causes ``eq.events.get_next()``
to yield ``MessageType.DISCONNECTED`` messages. # TODO max 5 (same as unavailable)

Reconnecting with the same instance of :py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`
automatically subscribes with the last used filters.

Putting it all together, you will end up with something like this:

    >>> import time
    >>> from energyquantified.events.event_options import EventFilterOptions
    >>> from energyquantified.events.events import MessageType
    >>> eq.events.connect()
    >>> # Create filter for actual-data in Germany
    >>> filter = EventFilterOptions()
    >>>             .set_areas("DE")
    >>>             .set_data_types("ACTUAL")
    >>> # Subscribe with the filter
    >>> eq.events.subscribe(filter)
    >>> for msg_type, data in eq.events.get_next():
    >>>     if msg_type == MessageType.EVENT:
    >>>         print(f"New event: {data}")
    >>>     elif msg_type == MessageType.INFO:
    >>>         print(f"New message from the stream: {data}")
    >>>     elif msg_type == MessageType.UNAVAILABLE:
    >>>         time.sleep(60)
    >>>         eq.events.connect()


Message types
---------------------

Method reference: :py:meth:`eq.events.get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>`

Events and messages received from the server is added to a queue. Loop over the queue
and access the items with ``eq.events.get_next()``. Note that ``eq.events.get_next()``
consumes items from the queue, so each item can only be accessed once.

The items accessed through ``get_next()`` is not limited to
:py:class:`~energyquantified.events.events.CurveUpdateEvent` items - it also includes server messages and more.
Therefore, items accessed through ``get_next()`` are tuples of two objects;
(1) :py:class:`~energyquantified.events.events.MessageType` describing the second item and
(2) the event or message received (e.g., :py:class:`~energyquantified.events.events.CurveUpdateEvent`).

The message types and the related data types is as following:

``MessageType.EVENT``
    The message includes a new curve event. The second element in the tuple is
    a :py:class:`~energyquantified.events.events.CurveUpdateEvent` object.

``MessageType.INFO``:
    A text message has been received from the server. The second element in the tuple
    is a string containing the message.

``MessageType.FILTERS``:
    A list of currrently active filters on the stream. The elements in the list are
    :py:class:`~energyquantified.events.event_options.EventFilterOptions` and
    :py:class:`~energyquantified.events.event_options.EventCurveOptions` objects.

``MessageType.TIMEOUT``:
    This can only occur if the ``timeout`` in ``get_next()`` is set, and means that ``timeout``
    number of seconds have passed since the last time a message was received. The timer resets
    for every new message in ``get_next()``. The second element in the tuple is always ``None``
    and can be ignored.

``MessageType.DISCONNECTED``:
    # TODO update
    The connection to the stream has dropped. The second element in the tuple is a
    :py:class:`~energyquantified.events.events.DisconnectedEvent` object with ``status_code`` and
    ``message``. If the user manually closes the connection with
    :py:meth:`eq.events.close() <energyquantified.api.CurveUpdateEventAPI.close>`, then neither
    ``status_code`` nor ``message`` will be set. The second element in the tuple is
    always ``None`` and can be ignored.

``MessageType.UNAVAILABLE``:
    This means that the connection dropped and the client exceeded the maximum number of attempts at
    reconnecting to the stream. The second element is going to be a
    :py:class:`~energyquantified.events.events.UnavailableEvent` object, with ``status_code`` and
    ``server_message`` from when the connection first dropped.

Check the ``MessageType`` and act accordingly:
        
        >>> import time
        >>> from energyquantified.events.events import MessageType
        >>> eq.events.connect()
        >>> for msg_type, event in ws.get_next():
        >>>     # If you want to ignore disconnect events
        >>>     if msg_type == MessageType.DISCONNECTED:
        >>>         time.sleep(60)
        >>>         eq.events.connect()
        >>>     if msg_type == MessageType.DISCONNECTED:
        >>>         continue
        >>>     if msg_type == MessageType.EVENT:
        >>>         # Act on event ..
        >>>     elif msg_type == MessageType.INFO:
        >>>         print(f"Info message from server: {event})

``get_next()`` is blocking, which means that 

#. get_next(): blocking, timeout

``eq.events.get_next()`` is blocking while waiting for new messages from the stream. If you might want to
act when the stream is quiet (e.g., changing filters), supply the ``timeout`` parameter with the number of
seconds to wait for an event.

    >>> eq.events.connect()
    >>> for msg_type, data in eq.events.get_next(timeout=10):
    >>>     # If 10 seconds pass since the last event

#.  Note that you will not receive b4 filters

#. auto reconnect

#. keyboardinterrrupt to exit



Closing the connection
---------------------

Method reference: :py:meth:`eq.events.close() <energyquantified.api.CurveUpdateEventAPI.close>`


Remembering received events
---------------------

Events are available on the stream server a short amount of time after they are created. Every
:py:class:`~energyquantified.events.events.CurveUpdateEvent` is uniquely identified by their
``event_id`` attribute. The API supports requesting older events. Note that the stream server
**keeps only a limited number of events** and there is no guarantee that you will receive all events.

Network error and missed events
~~~~~~~~~~~~~~

The client always keeps track of the most recent event received by storing the ``event_id``
in-memory. If you for any reason lose connection the stream, with the exception of manually closing
(i.e., calling :py:meth:`eq.events.close() <energyquantified.api.events.CurveUpdateEventAPI.close>`) it,
the client automatically tries to reconnect and requests all events since the last received ``event_id``.


Request all events since last session
~~~~~~~~~~~~~~

Getting events that were streamed after you were last connected to the stream can be done in one of two
ways; (1) supplying the ``last_id`` parameter in
:py:meth:`eq.events.connect() <energyquantified.api.events.CurveUpdateEventAPI.connect>`
with the ``event_id`` from the last :py:class:`~energyquantified.events.events.CurveUpdateEvent` you
received, or (2) by supplying the ``last_id_file`` parameter with a file path when initializing
:py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`. The two options are briefly described
in the following subsections. ID parameterized in ``connect()`` takes priority over the last id file.

Connecting with an ID
^^^^^^^^^^^^^^

When connecting to the stream, you can supply the ``last_id`` parameter
:py:meth:`eq.events.connect() <energyquantified.api.events.CurveUpdateEventAPI.connect>`
with the ``event_id`` from the last :py:class:`~energyquantified.events.events.CurveUpdateEvent` you
received, to include all events since. Note that the stream server **keeps only a limited number of
events** and there is no guarantee that you will receive all events.


Storing last event id in a file
^^^^^^^^^^^^^^

The simplest way to request events missed while not connected is to supply the ``last_id_file``
param with a file path when initializing
:py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`:

        >>> from energyquantified import EnergyQuantified
        >>> eq = EnergyQuantified(
        >>>     api_key="aaaa-bbbb-cccc-dddd,
        >>>     last_id_file="last_id_file.json", # file path
        >>> )

The file path can include parent directories (which will also be created):
    
        >>> from energyquantified import EnergyQuantified
        >>> eq = EnergyQuantified(
        >>>     api_key="aaaa-bbbb-cccc-dddd,
        >>>     last_id_file="folder_name/last_id_file.json",
        >>> )

The client regurarly updates the file at a defined interval (0.5/min), if the connection
closes, and when execution of the program is terminated (for any reason). The next time you
connect to the stream, assuming the same file path for ``last_id_file``, you will receive
all (available) events that you missed since last session.

The ID used when the last id file is updated is the ``event_id`` from the latest event received
from the stream, **regardless of it being accessed or not**. Consequently, it is important that
you loop over messages with ``eq.events.get_next()`` after closing the connection to make sure
that you have accessed every event received.

Load data for an event
---------------------

Method reference: :py:meth:`event.load_data() <energyquantified.events.events.CurveUpdateEvent.load_data>`


Filter events
---------------------

Method reference: :py:meth:`eq.events.subscribe() <energyquantified.api.events.CurveUpdateEventAPI.subscribe>`

In order to start receving events you must first subscribe with one or more filters. Simply create
a filter and pass it along when calling ``subscribe``. 

    >>> from energyquantified.events.event_options import EventFilterOptions
    >>> # First connect
    >>> eq.events.connect()
    >>> # Create filter and subscribe
    >>> filter = EventFilterOptions()
    >>> eq.events.subscribe(filter)

Filter types
~~~~~~~~~~~~~~

Choose between two types of filters when subscribing to events; (1) 
:py:class:`~energyquantified.events.event_options.EventCurveOptions` for filtering by exact curve names,
useful for when you want events for a specific selection of curves, and (2)
:py:class:`~energyquantified.events.event_options.EventFilterOptions` for filtering by a number of less
specific variables, such as the area of a curve.

EventCurveOptions
^^^^^^^^^^^^^^
TODO briefly describe this filter
TODO example of this filter
TODO describe methods here or only docstrings in the class?
``begin``:
    Start of the range to receive events for. Events overlapping begin/end (even partially) is
    considered to match.

    :py:meth:`set_begin() <energyquantified.events.event_options.EventCurveOptions.set_begin>`
``end``:
    Start of the range to receive events for. Events overlapping begin/end (even partially) is
    considered to match.
``event_types``:
    Set the event types
``curve_names``:
    Set curve names.

    :py:meth:`set_curve_names() <energyquantified.events.event_options.EventCurveOptions.set_curve_names>`

EventFilterOptions
^^^^^^^^^^^^^^

You can subscribe with a single filter or a list
of filters that may include a combination of both
:py:class:`~energyquantified.events.event_options.EventCurveOptions` and
:py:class:`~energyquantified.events.event_options.EventFilterOptions`. You will receive events matching
at least one of the filters. Each variable in a filter can be set with multiple values,
and an event is considered a match if the related variable match at least one of the values. For example,
creating a filter with two areas is going to match all events with either or both:

    >>> from energyquantified.events.event_options import EventFilterOptions
    >>> filter = EventFilterOptions().set_areas(["DE", "FR"])
    >>> # Matches all events for Germany and/or France

However, events must match all set variables. In the example below we still filter for Germany and/or France,
but limit the results to those with ``ACTUAL`` data-type. A forecast curve (i.e., data-type=``FORECAST``)
for germany would not be match becuase of the incorrect data type. The example below matches matches events
that is for Germany and/or France, **and** has the ``ACTUAL`` data-type.

    >>> from energyquantified.events.event_options import EventFilterOptions
    >>> filter = EventFilterOptions()
    >>> filter.set_areas(["DE", "FR"])
    >>> filter.set_data_types("actual")
    >>> # Matches all events for Germany and/or France that concern actual-data

Update filters
~~~~~~~~~~~~~~

Overwrite your currently active filters by calling
:py:meth:`set_curve_names() <energyquantified.events.event_options.EventCurveOptions.set_curve_names>`
with your new filters. Filters can also be updated while already connected to the stream.

    >>> from energyquantified.events.event_options import EventCurveOptions, EventFilterOptions
    >>> # Setting one filter
    >>> filter_0 = EventFilterOptions().set_areas("GB")
    >>> eq.events.subscribe(filter_0)
    >>> # Multiple filters
    >>> filter_1 = EventFilterOptions().set_areas("DE").set_data_types(["ACTUAL", "FORECAST"])
    >>> filter_2 = EventCurveOptions().set_curve_names("DE Consumption MWh/h 15min Normal")
    >>> new_filters = [filter_1, filter_2]
    >>> eq.events.subscribe(new_filters)

The stream server responds with the active filters once they have been successfully updated on the
server. The response can be found among the other messages in ``eq.events.get_next()``, and has
the ``FILTERS`` ``MessageType``. The example below shows the result from subscribing two times with
different filters:

    >>> from energyquantified.events.event_options import EventCurveOptions, EventFilterOptions
    >>> from energyquantified.events.events import MessageType
    >>> # Setting first filter
    >>> filter_1 = EventFilterOptions().set_areas("GB")
    >>> eq.events.subscribe(filter_1)
    >>> # Create some new filters and overwrite existing
    >>> filter_2 = EventFilterOptions().set_areas("DE").set_data_types(["ACTUAL", "FORECAST"])
    >>> filter_3 = EventCurveOptions().set_curve_names("DE Consumption MWh/h 15min Normal")
    >>> eq.events.subscribe([filter_2, filter_3])
    >>> for msg_type, data in eq.events.get_next():
    >>>     if msg_type == MessageType.FILTERS:
    >>>         print(data)
    [<EventFilterOptions: areas=[<Area: GB>]>]
    [<EventFilterOptions: areas=[<Area: DE>], data_types=[ACTUAL, FORECAST]>, <EventCurveOptions: curve_names=['de consumption mwh/h 15min normal']>]

Query for current filters
~~~~~~~~~~~~~~

Although you automatically get a message every time the filters are updatedF, it is also possible to
manually request the currently active filters with
:py:meth:`send_get_filters() <energyquantified.api.events.CurveUpdateEventAPI.send_get_filters>`.
The response with the filters will be put in a message queue that is accessible from
``eq.events.get_next()``, similar to the example above.

# "Reconnects with the same filters" also here?

disconnect / auto reconnect

#. TODO dc events (closed by user ?but also on close?)
#. TODO UnavailableEvent with status_code, server_message and message