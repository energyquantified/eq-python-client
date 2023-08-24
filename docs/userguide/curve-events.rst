Curve update events
===========

This page shows how to load curve events. The examples below expects you to have an initialized
instance of the client called ``eq``.

Operations described here are available under ``eq.events.*``


Prerequisites
---------------------


Curve events
~~~~~~~~~~~~~~

A curve event (:py:class:`~energyquantified.events.CurveUpdateEvent`) is created whenever
data for a :py:class:`~energyquantified.metadata.Curve` is changed. Events provide information
about what kind of operation was done (e.g., delete or update) on the curve, timestamps of
the first and last affected values, and the total number of affected values. It also includes an
:py:class:`~energyquantified.metadata.Instance` if relevant.


If values were updated at 15-minute frequency for Germany's consumption normal at
``2023-01-01 01:15`` and ``2023-01-01 01:45``, the following event would be produced:

    >>> <CurveUpdateEvent:
    >>>     event_id="123"
    >>>     curve="DE Consumption MWh/h 15min Normal",
    >>>     event_type=EventType.CURVE_UPDATE,
    >>>     begin="2023-01-01 01:15,
    >>>     end="2023-01-01 02:00",
    >>>     num_values=2>


WebSocket and filters
~~~~~~~~~~~~~~

Curve events are streamed in real-time from EQ's WebSocket API. After initializing the
:py:class:`EnergyQuantified <energyquantified.EnergyQuantified>` API client, the
:py:class:`CurveUpdateEventAPI <energyquantified.api.CurveUpdateEventAPI>` is accessible
through ``eq.events``:

    >>> from energyquantified import EnergyQuantified
    >>> eq = EnergyQuantified(...)
    >>> eq.events. # ...

Connect to the stream with :py:meth:`connect() <energyquantified.api.CurveUpdateEventAPI.connect>`:

    >>> from energyquantified import EnergyQuantified
    >>> eq = EnergyQuantified(...)
    >>> eq.events.connect()

After connecting, one must first subscribe with one or more filters in order to receive events.
The filters specify which curves to receive events for. There are two different filter models:

- :py:class:`~energyquantified.events.EventCurveOptions`: Filter by exact curves
- :py:class:`~energyquantified.events.EventFilterOptions`: Search filters similar
  to the curve search

Subscribe with the filters as follows:

    >>> from energyquantified import EnergyQuantified
    >>> eq = EnergyQuantified(...)
    >>> eq.events.connect()
    >>> filters = [
    >>>     EventFilterOptions(areas=["DE", "FR"]),
    >>>     filter_2,
    >>> ]
    >>> eq.events.subscribe(filters)

The filters can be updated on the fly while listening to the stream, due to websockets
bidirectional communication protocol.


Server messages
~~~~~~~~~~~~~~

By default, messages from the server will be logged at the info level. Override the default by
setting a custom callback function with 
:py:meth:`eq.events.set_message_handler() <energyquantified.api.CurveUpdateEventAPI.set_message_handler>`.
The custom function must take in one parameter; the server message which is a string.


Types of events
~~~~~~~~~~~~~~

Events are accessed through :py:meth:`eq.events.get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>`.

Curve event: :py:class:`energyquantified.events.CurveUpdateEvent`:
    Describes change in data for a curve

Connection event: :py:class:`energyquantified.events.ConnectionEvent`:
    Describes an event related to the stream connection (e.g., disconnect)

What is common for all event models is that they all have the ``event_type`` property.


Quickstart
---------------------


Connect to the stream and subscribe to events
~~~~~~~~~~~~~~

Connect to the stream by calling
:py:meth:`eq.events.connect() <energyquantified.api.CurveUpdateEventAPI.connect>`. Note that this
temporarily blocks program execution while trying to establish a connection to the stream.

    >>> eq.events.connect()

Note that you will not immediately start to receive events after connecting to the stream. In order to
receive curve events you must also subscribe. Subscribe to curve events with
:py:meth:`eq.events.subscribe_curve_events() <energyquantified.api.CurveUpdateEventAPI.subscribe_curve_events>`.
The example below illustrates how to subscribing for curve events that concern actual-data in Germany:

    >>> from energyquantified.events import EventFilterOptions
    >>> eq.events.connect()
    >>> filters = [
    >>>     EventFilterOptions(
    >>>         areas="DE",
    >>>         data_types="ACTUAL",
    >>>     )
    >>> ]
    >>> eq.events.subscribe_curve_events(filters=filters)

After subscribing you will automatically start to receive events. These events can be accessed in the generator
:py:meth:`eq.events.get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>`:

    >>> from energyquantified.events import EventFilterOptions
    >>> eq.events.connect()
    >>> # Subscribe to all events for Germany
    >>> filters = [EventFilterOptions(areas="DE")]
    >>> eq.events.subscribe_curve_events(filters=filters)
    >>> for event in eq.events.get_next():
    >>>     # Handle event

Events from :py:meth:`eq.events.get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>`
can be of different types, so you will sometimes get events of different type than
:py:class:`~energyquantified.events.CurveUpdateEvent`. For instance, you will get a
:py:class:`~energyquantified.events.ConnectionEvent` in the case of an unexpected disconnect.
The ``event_type`` attribute is common for all events from ``get_next()``, and may be used to
check the type of an event.

    >>> from energyquantified.events import EventType
    >>> # After connecting and subscribing
    >>> for event in eq.events.get_next():
    >>>     if event.event_type.is_curve_type():
    >>>         # Handle the curve event
    >>>     elif event.event_type.is_connection_type():
    >>>         # Handle connection event
    >>>         if event.event_type == EventType.DISCONNECTED:
    >>>             # Maybe reconect?


:py:class:`energyquantified.events.TimeoutEvent`
^^^^^^^^^^^^^^

:py:meth:`eq.events.get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>` blocks the thread
while waiting for a new message from the stream. If you might want to act when the stream is quiet (e.g.,
changing filters), supply the ``timeout`` parameter with the number of seconds to wait for an event. If
more than ``timeout`` seconds passes before a new event is received, you will get a
:py:class:`energyquantified.events.TimeoutEvent` object. The following code illustrates how
timeout events can be used to change filters:

    >>> eq.events.connect()
    >>> for event in eq.events.get_next(timeout=10):
    >>>     if event.event_type.is_timeout_type():
    >>>         # timeout (10) seconds passed with no new event. Maybe I want to change filter.
    >>>         # Create or update a filter
    >>>         filters = ...
    >>>         eq.events.subscribe_curve_events(filters=filters)

Timeout events can be ignored if you do not intend to act:

    >>> eq.events.connect()
    >>> for event in eq.events.get_next(timeout=10):
    >>>     if event.event_type.is_timeout_type():
    >>>         pass

Or simply omit the ``timeout`` parameter:

    >>> eq.events.connect()
    >>> for event in eq.events.get_next():
    >>>     pass


Network error and reconnecting
~~~~~~~~~~~~~~

The client will automactically try to reconnect to the stream if the connection drops, unless the
user manually closes it with :py:meth:`eq.events.close() <energyquantified.api.CurveUpdateEventAPI.close>`.

If the client is not connected to stream **and** is not trying to (re)connect (**and** all received
events have been handled),
:py:meth:`get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>` will start to yield
:py:class:`ConnectionEvent <energyquantified.events.ConnectionEvent>`'s that describes the cause of the disconnect.
In this situation you need to manually invoke :py:meth:`connect() <energyquantified.api.CurveUpdateEventAPI.connect>`
in order to (re)connect to the stream. Please wait a brief moment before trying to reconnect, by sleeping
the program as shown below:
    
    >>> import time
    >>> from energyquantified.events import EventType
    >>> eq.events.connect()
    >>> for event in eq.events.get_next():
    >>>     if event.event_type == EventType.DISCONNECTED:
    >>>         # Wait 60 seconds before reconnecting
    >>>         time.sleep(60)
    >>>         # Try to reconnect
    >>>         eq.events.connect()

Note that you can access previously received and unhandled events in ``eq.events.get_next()``,
regardless of connection status (you will not see connection events until earlier events have been handled). Keep
in mind that each event is only returned **once** from ``eq.events.get_next()``.

Close the connection by caling 
:py:meth:`eq.events.close() <energyquantified.api.CurveUpdateEventAPI.close>`.This also causes 
:py:meth:`get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>` to yield
:py:class:`ConnectionEvent <energyquantified.events.ConnectionEvent>`'s after all events have been
handled. The reason of a disconnect (e.g., intentionally closed by user, server went down) is described
in the ``ConnectionEvent``.

Reconnecting with the same instance of :py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`
automatically subscribes with the last used filters.

Putting it all together, you will end up with something like this:

    >>> import time
    >>> from energyquantified.events import EventFilterOptions
    >>> eq.events.connect()
    >>> # Create filter for actual-data in Germany
    >>> filter = EventFilterOptions()
    >>>             .set_areas("DE")
    >>>             .set_data_types("ACTUAL")
    >>> # Subscribe with the filter
    >>> eq.events.subscribe(filter)
    >>> for event in eq.events.get_next():
    >>>     if event.event_type.is_curve_type():
    >>>         # New curve event, let's log or print it
    >>>         print(event)
    >>>     elif event.event_type.is_connection_type():
    >>>         # New connection event, let's log or print it
    >>>         print(event)
    >>>         # Have we disconnected?
    >>>         if event.event_type == EventType.DISCONNECTED:
    >>>             # Then let's reconnect (after waiting a brief moment)
    >>>             time.sleep(60)
    >>>             eq.events.connect()
    >>>             # If you were subscribed to curve events prior to disconnecting, then you
    >>>             # will be automatically subscribed with the same filters


Closing the connection
---------------------

Method reference: :py:meth:`eq.events.close() <energyquantified.api.CurveUpdateEventAPI.close>`


Remembering received events
---------------------

Events are available on the stream server a short amount of time after they are created. Every
:py:class:`~energyquantified.events.CurveUpdateEvent` is uniquely identified by their
``event_id`` attribute. The API supports requesting older events. Note that the stream server
**keeps only a limited number of events** and there is no guarantee that you will receive all events.


Network error and missed events
~~~~~~~~~~~~~~

The client always keeps track of the most recent event received by storing the ``event_id``
in-memory. If you for any reason lose connection the stream, with the exception of manually closing
(i.e., calling :py:meth:`eq.events.close() <energyquantified.api.CurveUpdateEventAPI.close>`) it,
the client automatically tries to reconnect and requests all events since the last received ``event_id``.

When reconnecting with the same instance of
:py:class:`EnergyQuantified <energyquantified.EnergyQuantified>` (or during automatic reconnect)
the client will try to subscribe with the last used filters.


Request all events since last session
~~~~~~~~~~~~~~

Getting events that were streamed after you were last connected to the stream can be done in one of two
ways; (1) supplying the ``last_id`` parameter in
:py:meth:`eq.events.connect() <energyquantified.api.CurveUpdateEventAPI.connect>`
with the ``event_id`` from the last :py:class:`~energyquantified.events.CurveUpdateEvent` you
received, or (2) by supplying the ``last_id_file`` parameter with a file path when initializing
:py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`. The two options are briefly described
in the following subsections. ID parameterized in ``connect()`` takes priority over the last id file.


Connecting with an ID
^^^^^^^^^^^^^^

Supply the ``last_id`` parameter in
:py:meth:`eq.events.connect() <energyquantified.api.CurveUpdateEventAPI.connect>`
with the ``event_id`` from the last :py:class:`~energyquantified.events.CurveUpdateEvent` you
received to also receive older events. Note that the stream server **keeps only a limited number of
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

Method reference: :py:meth:`event.load_data() <energyquantified.events.CurveUpdateEvent.load_data>`

Load the data an event describes by calling
:py:meth:`event.load_data() <energyquantified.events.CurveUpdateEvent.load_data>`:

    >>> for msg_type, data in eq.events.get_next():
    >>>     if msg_type == MessageType.EVENT:
    >>>         series = data.load_data()

Note that different events concern different types of data; ``series`` in the example above could
be a :py:class:`~energyquantified.data.Timeseries`, :py:class:`~energyquantified.data.Periodseries`,
or an object of another type.


Filter events
---------------------

Method reference: :py:meth:`eq.events.subscribe() <energyquantified.api.CurveUpdateEventAPI.subscribe>`

In order to start receving events you must first subscribe with one or more filters. Simply create
a filter and pass it along when calling ``subscribe``:

    >>> from energyquantified.events import EventFilterOptions
    >>> # First connect
    >>> eq.events.connect()
    >>> # Create filter and subscribe
    >>> filter = EventFilterOptions()
    >>> eq.events.subscribe(filter)

    >>> from energyquantified import EnergyQuantified
    >>> # First initialize api client and then connect
    >>> eq = EnergyQuantified(...)
    >>> eq.events.connect()
    >>> # Create filters
    >>> filter_1 = EventFilterOptions()
    >>> filter_1.set_areas(["DE", "FR"])
    >>> filter_2 = EventCurveOptions()
    >>> filter_2.set_curve_names([<insert exact curve name here>])
    >>> filters = [filter_1, filter_2]
    >>> # Subscribe with multiple filters ..
    >>> eq.events.subscribe(filters)
    >>> # .. or with a single
    >>> eq.events.subscribe(fitler_1)

You can subscribe with one or multiple filters, and will receive events matching at least one of
the filters. If a variable in a filter has multiple values (e.g., two areas), an event is considered
to match if it matches at least one of the set value:

    >>> from energyquantified.events import EventFilterOptions
    >>> filter = EventFilterOptions().set_areas(["DE", "FR"])
    >>> # Matches all events for Germany and/or France

There is no restriction for the type of filters when subscribing with multiple, so you are free to use
a combination of :py:class:`~energyquantified.events.EventCurveOptions` and
:py:class:`~energyquantified.events.EventFilterOptions`. **Note that the maximum number of filters
allowed is limited to ten (10)**.

Events must match all variables from a filter. In the example below we still filter for Germany and/or France,
but limit the results to those with the ``ACTUAL`` data-type. A forecast curve (i.e., data-type=``FORECAST``)
for germany would not be match becuase of data type mismatch. The example below matches matches events
that is for Germany and/or France, **and** has the ``ACTUAL`` data-type.

    >>> from energyquantified.events import EventFilterOptions
    >>> filter = EventFilterOptions()
    >>> filter.set_areas(["DE", "FR"])
    >>> filter.set_data_types("actual")
    >>> # Matches all events for Germany and/or France that concern actual-data

The implementation of the filters is fluent so setting variables can be chained:

    >>> from energyquantified.events import EventFilterOptions
    >>> filter = EventFilterOptions()
    >>> filter.set_areas(["DE", "FR"]).set_data_types("actual") #.set( .. )
    >>> # Matches all events for Germany and/or France that concern actual-data


Filter types
~~~~~~~~~~~~~~

Choose between two types of filters when subscribing to events; (1) 
:py:class:`~energyquantified.events.EventCurveOptions` for filtering by exact curve names,
useful for when you want events for a specific selection of curves, and (2)
:py:class:`~energyquantified.events.EventFilterOptions` for filtering by a selection of
:py:class:`~energyquantified.data.Curve` attributes, such as
:py:class:`~energyquantified.metadata.Area` or :py:class:`~energyquantified.metadata.DataType`.


EventCurveOptions
^^^^^^^^^^^^^^

See :py:class:`energyquantified.events.EventCurveOptions`

``begin``:
    Start of the range to receive events for. Events overlapping begin/end (even partially) is
    considered to match.

    :py:meth:`set_begin() <energyquantified.events.EventCurveOptions.set_begin>`
``end``:
    Start of the range to receive events for. Events overlapping begin/end (even partially) is
    considered to match.

    :py:meth:`set_begin() <energyquantified.events.EventCurveOptions.set_begin>`
``event_types``:
    Filter by one or more :py:class:`EventType <energyquantified.events.EventType>`'s
    (e.g., ``UPDATE`` or ``DELETE``).

    :py:meth:`set_event_types() <energyquantified.events.EventCurveOptions.set_event_types>`
``curve_names``:
    Exact curve name(s).

    :py:meth:`set_curve_names() <energyquantified.events.EventCurveOptions.set_curve_names>`


EventFilterOptions
^^^^^^^^^^^^^^

See :py:class:`energyquantified.events.EventFilterOptions`

``begin``:
    Start of the range to receive events for. Events overlapping begin/end (even partially) is
    considered to match.

    :py:meth:`set_begin() <energyquantified.events.EventFilterOptions.set_begin>`
``end``:
    Start of the range to receive events for. Events overlapping begin/end (even partially) is
    considered to match.

    :py:meth:`set_begin() <energyquantified.events.EventFilterOptions.set_begin>`
``event_types``:
    Filter by one or more :py:class:`EventType <energyquantified.events.EventType>`'s
    (e.g., ``UPDATE`` or ``DELETE``).

    :py:meth:`set_event_types() <energyquantified.events.EventFilterOptions.set_event_types>`

``q``:
    Freetext search alike the curve search (e.g., "wind power germany")

    :py:meth:`set_q() <energyquantified.events.EventFilterOptions.set_q>`

``areas``:
    Filter by one or more :py:class:`Area <energyquantified.metadata.Area>`'s.

    :py:meth:`set_areas() <energyquantified.events.EventFilterOptions.set_areas>`

``data_types``:
    Filter by one or more :py:class:`DataType <energyquantified.metadata.DataType>`'s.

    :py:meth:`set_data_types() <energyquantified.events.EventFilterOptions.set_data_types>`

``commodities``:
    Filter by commodities.

    :py:meth:`set_commodities() <energyquantified.events.EventFilterOptions.set_commodities>`

``categories``:
    Filter by one or more categories.

    :py:meth:`set_categories() <energyquantified.events.EventFilterOptions.set_categories>`

``exact_categories``:
    Filter by one or more exact categories. An exact category should be a string of categories
    separated by space.

    :py:meth:`set_exact_categories() <energyquantified.events.EventFilterOptions.set_exact_categories>`


Update filters
~~~~~~~~~~~~~~

Update your stream filters by calling
:py:meth:`subscribe() <energyquantified.api.CurveUpdateEventAPI.subscribe>`
with your new filters. Filters can be updated while already connected to the stream.

    >>> from energyquantified.events import EventCurveOptions, EventFilterOptions
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

    >>> from energyquantified.events import EventCurveOptions, EventFilterOptions, MessageType
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

Although you automatically get a message every time the filters are updated, it is also possible to
manually request the currently active filters with
:py:meth:`send_get_filters() <energyquantified.api.CurveUpdateEventAPI.send_get_filters>`.
The response with the filters will be put in a message queue that is accessible from
``eq.events.get_next()``, similar to the example above.


Automic subscribe after reconnect
~~~~~~~~~~~~~~

When reconnecting with the same instance of
:py:class:`EnergyQuantified <energyquantified.EnergyQuantified>` (or if automatic reconnect)
the client will try to subscribe with the last used filters.


Program termination and event id
---------------------

It can be useful to keep track of the ID from the last event handled when exiting the program, in order
to not receive duplicate events next time connecting. If the ``last_id_file`` is set upon initialization
of :py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`, the file will be updated
at program termination with the use of the `atexit <https://docs.python.org/3/library/atexit.html>` module.
However, the ID saved when using a file is the last ID that is added to the message queue, and not
necessarily the last event handled by the user. If you want to keep track of the ID from the last event you
were done handling, the following code may be helpful:
    
    >>> import json
    >>>
    >>> last_id = None
    >>> try:
    >>>     for msg_type, data in get_next():
    >>>         if msg_type == MessageType.EVENT:
    >>>             # your preferred actions, maybe loading a series
    >>>             series = data.load_data()
    >>>             # ...
    >>>             # Done handling the event, let's save the id
    >>>             last_id = data.event_id
    >>> # (optional) catch KeyboardInterrupt to manually stop the script
    >>> catch KeyboardInterrupt as _:
    >>>     save_file()
    >>> catch Exception as e:
    >>>     # Or just save for any unexpected error
    >>>     save_file()
    >>>
    >>> def save_file():
    >>>     with open("backup_last_id_file.json", "w") as f:
    >>>         json.dump({"last_id": last_id}, f)

Or by using `atexit <https://docs.python.org/3/library/atexit.html>`:

    >>> import atexit
    >>> import json
    >>> 
    >>> last_id = None
    >>>
    >>> def save_file():
    >>>     with open("backup_last_id_file.json", "w") as f:
    >>>         json.dump({"last_id": last_id}, f)
    >>>
    >>> atexit.register(save_file)
    >>>
    >>> for msg_type, data in get_next():
    >>>     if msg_type == MessageType.EVENT:
    >>>         # your preferred actions, maybe loading a series
    >>>         series = data.load_data()
    >>>         # ...
    >>>         # Done handling the event, let's save the id
    >>>         last_id = data.event_id


Message and error handlers
~~~~~~~~~~~~~~
todo
