Curve update events
===================

This page shows how to load curve events that are streamed in real-time from
EQ's WebSocket API. The examples below expects you to have an initialzied
instance of the :py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`
API client called ``eq``.

Operation described here are available under ``eq.events.*``.


Terminology
-----------


Curve events
~~~~~~~~~~~~

Class reference: :py:class:`eq.events.CurveUpdateEvent <energyquantified.events.CurveUpdateEvent>`

Curve events created whenever data in a
:py:class:`~energyquantified.metadata.Curve` changes. Events provide information
about what kind of operation was done (e.g., delete, update) on the curve,
timestamps of the first and last affected values, and the total number of
affected values. It also includes an
:py:class:`~energyquantified.metadata.Instance` if relevant.

If values were updated at 15-minute frequency for Germany's consumption normal at
``2023-01-01 01:15`` and ``2023-01-01 01:45``, the following event would be produced:

.. code-block:: python

    <CurveUpdateEvent:
        event_id="1234567890123-0",
        curve="DE Consumption MWh/h 15min Normal",
        event_type=EventType.CURVE_UPDATE,
        begin="2023-01-01 01:15",
        end="2023-01-01 02:00",
        num_values=2>

Curve events are uniquely identified by the ``event_id`` attribute. Event id's
are strings that consists of two numbers separated by a dash ("-"), where the
first number is exactly 13 digits long and represents the timestamp at which
the event was created. The second number is a serial.


Event types
~~~~~~~~~~~

All events have an :py:class:`EventType <energyquantified.events.EventType>`
at the ``event_type`` attribute. Event types describe what an event means.

    * :py:class:`EventType.CURVE_UPDATE <energyquantified.events.EventType>`:
      Data in a curve is updated

    * :py:class:`EventType.CURVE_DELETE <energyquantified.events.EventType>`:
      Some data in a curve or a whole instance is removed

    * :py:class:`EventType.CURVE_TRUNCATE <energyquantified.events.EventType>`:
      All data in a curve is removed

    * :py:class:`EventType.DISCONNECTED <energyquantified.events.EventType>`:
      Not connected to the push feed (reason described by other attributes in the event)

    * :py:class:`EventType.TIMEOUT <energyquantified.events.EventType>`:
      Filler event that enables users to act in between events during quiet times.
      Timeout events are only generated if the ``timeout`` parameter is set in
      :py:meth:`eq.events.get_next() <energyquantified.api.EventsAPI.get_next>`.


Filters
~~~~~~~

In order to receive events, one must first subscribe to the events of interest.
When subscribing to curve events you must provide a list of filters for which
curves to receive events for.

You will receive events matching **any** of your filters. A filter is considered
a match if all set variables matches the event. A filter with
``areas=[Area.DE, Area.FR]`` and
``data_types=[DataType.ACTUAL, DataType.FORECAST]`` matches curves with
in ``DE`` and/or ``FR`` with ``ACTUAL`` or ``FORECAST`` data type.

You can re-subscribe with new filters on the fly while already listening to the
stream, due to websockets bidirectional communication protocol.


Quickstart
----------

First, we must connect to the WebSockets endpoint:

.. code-block:: python

    eq.events.connect()

Once connected, we can specify our filters and subscribe to them. Here we create
filters for ACTUAL and FORECAST events in DE, FR and GB:

.. code-block:: python

    my_filter = CurveAttributeFilter(
        areas=[Area.DE, Area.FR, Area.GB],
        data_types=[DataType.ACTUAL, DataType.FORECAST],
    )

Subscribe to curve events with the filters:

.. code-block:: python

    # Single filter
    eq.events.subscribe_curve_events(filters=my_filter)

    # Multiple filters
    eq.events.subscribe_curve_events(filters=[
        my_filter,
        another_filter,
        third_filter,
    ])

Then you can loop over incoming events forever:

.. code-block:: python

    # Loop over incoming events (blocking)
    for event in eq.events.get_next():

        if event.event_type == EventType.CURVE_UPDATE:
            # A curve is updated, so we can load its data
            data = event.load_data()
            # Store it in your database?
            continue

        if event.event_type == EventType.DISCONNECTED:
            # Not connected and no more events to process
            break

Putting it all together, this is a minimal example on how to connect, subscribe,
and start listening for curve events:

.. code-block:: python

    import time
    from energyquantified import EnergyQuantified
    from energyquantified.events import EventType, CurveAttributeFilter
    from energyquantified.metadata import Area, DataType

    # Initialize the client
    eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")

    # Connect to the WebSocket endpoint
    eq.events.connect()

    # Create filters for ACTUAL and FORECAST events in DE, FR and GB
    filters = CurveAttributeFilter(
        areas=[Area.DE, Area.FR, Area.GB],
        data_types=[DataType.ACTUAL, DataType.FORECAST],
    )

    # Subscribe to curve events
    eq.events.subscribe_curve_events(filters=filters)

    # Loop over incoming events (blocking)
    for event in eq.events.get_next():

        if event.event_type == EventType.CURVE_UPDATE:
            # A curve is updated, so we can load its data
            print("Curve updated: ", event)
            # Load data
            data = event.load_data()
            # Store it in your database?
            continue

        if event.event_type == EventType.DISCONNECTED:
            # Not connected and no more events
            break


Connecting
----------

Method reference: :py:meth:`eq.events.connect() <energyquantified.api.EventsAPI.connect>`

Connect to the stream by calling
:py:meth:`connect() <energyquantified.api.EventsAPI.connect>`.
Note that this temporarily blocks program execution while trying to connect.

.. code-block:: python

    eq.events.connect()

The client tries to automatically reconnect on network errors. You can override
the number of reconnect attempts by setting the ``reconnect_attempts`` parameter
in connect. The number of attempts reset once if a connection is re-established.

.. code-block:: python

    eq.events.connect(reconnect_attempts=5)


Disconnecting
-------------

Method reference: :py:meth:`eq.events.disconnect() <energyquantified.api.EventsAPI.disconnect>`

Connect to the stream by calling
:py:meth:`disconnect() <energyquantified.api.EventsAPI.disconnect>` or
:py:meth:`close() <energyquantified.api.EventsAPI.close>`. Events received prior
to closing the connection continues to be available in
:py:meth:`get_next() <energyquantified.api.EventsAPI.get_next>`.

.. code-block:: python

    eq.events.disconnect()

Subscribing
-----------

Method reference: :py:meth:`eq.events.subscribe_curve_events() <energyquantified.api.EventsAPI.subscribe_curve_events>`


In order to receive events one must first subscribe with a list of filters,
limiting the events you receive to those of interest. You can update your
filters while already subscribed by calling
:py:meth:`subscribe_curve_events() <energyquantified.api.EventsAPI.subscribe_curve_events>`
with the new filters.

After subscribing, the server responds with a
:py:class:`CurvesSubscribeResponse <energyquantified.events.CurvesSubscribeResponse>`
object. By the default, the response is handled by logging the result. If the
subscribe is successfull it will be logged at the info level, else at error
level including reasons for failure. You can set a custom handler by supplying
``callback`` parameter in
:py:meth:`subscribe_curve_events() <energyquantified.api.EventsAPI.subscribe_curve_events>`
with your own function:

.. code-block:: python

    def on_subscribe(response: CurvesSubscribeResponse):
        if response.ok:
            log.info("subscribed")
        else:
            log.error("something went wrong")

    eq.events.subscribe_curve_events(
        filters=[...],
        callback=on_subscribe
    )


Providing filters
~~~~~~~~~~~~~~~~~

There are two different types of filters for curve events:

    * :py:class:`~energyquantified.events.CurveNameFilter`: Filter by
      curves/curve names

    * :py:class:`~energyquantified.events.CurveAttributeFilter`: Search filters
      similar to the curve search

You can subscribe with a combination of both
:py:class:`CurveNameFilter <energyquantified.events.CurveNameFilter>` and
:py:class:`CurveAttributeFilter <energyquantified.events.CurveAttributeFilter>`.
The maximum number of filters allowed is limited to ten (10). You will receive
events for curves that match **any** of your filters, and a filters is
considered a match if **all set variables** matches the event.

Subscribe to curve events with one or more filters:

.. code-block:: python

    # Single filter
    eq.events.subscribe_curve_events(filters=filter_1)
    # Or with multiple filters
    eq.events.subscribe_curve_events(filters=[
        filter_1,
        ..,
        filter_n
        ]
    )


Both filters support setting the variables in various ways:

.. code-block:: python

    # Through the constructor
    filter_1 = CurveNameFilter(areas=[Area.DE])
    # Through .set_ methods
    filter_1 = CurveNameFilter()
    filter_1.set_areas([Area.DE])
    # And can be used fluently
    filter_1.set_areas(Area.DE).set_data_types(DataType.ACTUAL)

Common variables in both filters are ``event_types``, ``begin`` and ``begin``.


Filter specific curves
^^^^^^^^^^^^^^^^^^^^^^

Class reference: :py:class:`energyquantified.events.CurveNameFilter`

This filter is used to match specific curves through ``curve_names``.

``begin``: :py:meth:`set_begin() <energyquantified.events.CurveNameFilter.set_begin>`
    Start of the range to receive events for. Events partially in the
    begin/end interval is also considered to match.

``end``: :py:meth:`set_end() <energyquantified.events.CurveNameFilter.set_end>`
    End of the range to receive events for. Events partially in the begin/end
    interval is also considered to match.

``event_types``: :py:meth:`set_event_types() <energyquantified.events.CurveNameFilter.set_event_types>`
    Filter by one or more :py:class:`EventType <energyquantified.events.EventType>`'s
    (e.g., ``CURVE_UPDATE`` or ``CURVE_DELETE``)

``curve_names``: :py:meth:`set_curve_names() <energyquantified.events.CurveNameFilter.set_curve_names>`
    Filter by exact curve name(s)


Filter by curve attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^

Class reference: :py:class:`energyquantified.events.CurveAttributeFilter`

This filter is used for filtering curves based on different metadata such as
area or data type.

``begin``: :py:meth:`set_begin() <energyquantified.events.CurveNameFilter.set_begin>`
    Start of the range to receive events for. Events partially in the
    begin/end interval is also considered to match.

``end``: :py:meth:`set_end() <energyquantified.events.CurveNameFilter.set_end>`
    End of the range to receive events for. Events partially in the begin/end
    interval is also considered to match.

``event_types``: :py:meth:`set_event_types() <energyquantified.events.CurveNameFilter.set_event_types>`
    Filter by one or more :py:class:`EventType <energyquantified.events.EventType>`'s
    (e.g., ``CURVE_UPDATE`` or ``CURVE_DELETE``)

``q``: :py:meth:`set_q() <energyquantified.events.CurveAttributeFilter.set_q>`
    Freetext search alike the curve search (e.g., "wind power germany")

``areas``: :py:meth:`set_areas() <energyquantified.events.CurveAttributeFilter.set_areas>`
    Filter by :py:class:`Area <energyquantified.metadata.Area>`'s

``data_types``: :py:meth:`set_data_types() <energyquantified.events.CurveAttributeFilter.set_data_types>`
    Filter by :py:class:`DataType <energyquantified.metadata.DataType>`'s

``commodities``: :py:meth:`set_commodities() <energyquantified.events.CurveAttributeFilter.set_commodities>`
    Filter by commodities

``categories``: :py:meth:`set_categories() <energyquantified.events.CurveAttributeFilter.set_categories>`
    Filter by categories

``exact_categories``: :py:meth:`set_exact_categories() <energyquantified.events.CurveAttributeFilter.set_exact_categories>`
    Filter by one or more exact categories. An exact category is a string of
    categories (order matter) separated by space.


Providing last id
~~~~~~~~~~~~~~~~~

Provide an event id to the optional parameter ``last_id`` in
:py:meth:`subscribe_curve_events() <energyquantified.api.EventsAPI.subscribe_curve_events>`
to ignore events created earlier than the event with the supplied id. You can
subscribe with an id that has a timestamp in the future to only receive events
created after. This id takes priority over the (optional) id from disk (further
described :ref:`here <remember last id>`).


Handling events
---------------

Method reference: :py:meth:`eq.events.get_next() <energyquantified.api.EventsAPI.get_next>`

After subscribing to curve events you will immediately start receiving events
matching your filters. Loop over incoming events:

.. code-block:: python

    for event in eq.events.get_next():
        # Handle event

Events can be of different types, so you may not always get a
:py:class:`~energyquantified.events.CurveUpdateEvent`. For instance, unexpected
you will get a :py:class:`~energyquantified.events.ConnectionEvent` in the case
of an unexpected disconnect, or a
:py:class:`~energyquantified.events.TimeoutEvent` if a timeout occurs. The
different events are described further in this section.

Note that all events have the ``event_type`` property with an
:py:class:`~energyquantified.events.TimeoutEvent`, which can be of use when
deciding how to act.


Loading data data for events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Method reference:
:py:meth:`event.load_data() <energyquantified.events.CurveUpdateEvent.load_data>`

Check if the event represent a curve update and load it's data:

.. code-block:: python

    for event in eq.events.get_next():
        if event.event_type = EventType.CURVE_UPDATE:
            data = event.load_data()

The type of data loaded depends on the curve, and may be a
:py:class:`~energyquantified.data.Timeseries`,
:py:class:`~energyquantified.data.Periodseries`, or some other type.

Note that not all curve events support loading of data, such as events with
type ``CURVE_DELETE`` or ``CURVE_TRUNCATE`` as deleted data no longer exists.


Connection events
~~~~~~~~~~~~~~~~~

Class reference:
:py:class:`ConnectionEvent <energyquantified.events.ConnectionEvent>`

Connection events describe a change or status in the stream connection, and is
primarily used with the ``DISCONNECTED`` event type. This type indicates that
you are not connected, and further details can be found in the connection event.
You will not receive events of this type until after all received curve events
have been processed.

Capture these events like you can see below. In this example we simply break out
of the loop and stop processing events:

.. code-block:: python

    for event in eq.events.get_next():
        if event.event_type == EventType.DISCONNECTED:
            # Not connected and event queue is empty
            print(f"Not connected: {event}")
            break

Optionally you can use the disconnected event to try reconnecting manually. Note
that the client will always try to reconnect a couple of times before it gives
up and emits this event. Once reconnected the client will resubscribe with the
previous filters, and ask for events that occured during downtime.

.. code-block:: python

    import time

    for event in eq.events.get_next():
        if event.event_type == EventType.DISCONNECTED:
            # Not connected and event queue is empty
            print(f"Not connected: {event}")
            # Wait 30 seconds before reconnecting
            time.sleep(30)
            # Try to reconnect
            eq.events.connect()
            continue

Note that you also get events of the ``DISCONNECTED`` type if you never
connected in the first place, so it does not necessarily mean that a disconnect
took place.


Timeouts
~~~~~~~~

Class reference:
:py:class:`TimeoutEvent <energyquantified.events.TimeoutEvent>`

:py:meth:`get_next() <energyquantified.api.EventsAPI.get_next>` is blocking
which means that you cannot act while waiting for a new event. The timeout event
is designed as a filler event that enables users to act in between events during
quiet times. Supply the optional ``timeout`` parameter with the number of
seconds you want to wait for new events. You will then receive a timeout event
whenever the set number of seconds passes without any new event.

.. code-block:: python

    for event in eq.events.get_next(timeout=10):
        if event.event_type == EventType.TIMEOUT:
            print("No events in the last 10 seconds")
            continue

Timeout events can be useful if you intend to execute some code after a certain
amount of time. Setting the timout interval eliminates the risk of being stuck
and unable to act while waiting for the next event, due to the blocking nature
of ``get_next()``.

You can safely ignore this event if you do not find it useful.


Capturing messages and errors
-----------------------------

By default, messages from the server will be logged at info level. Override the
default by setting a custom callback function with
:py:meth:`eq.events.set_message_handler() <energyquantified.api.EventsAPI.set_message_handler>`.
The custom function must take in one parameter; the server message which is a
string.

.. code-block:: python

    def message_handler(message):
        print(f"Message from server: {message}")

    eq.events.set_message_handler(message_handler)

Similarly, you can also override the callback for handling error messages with
:py:meth:`eq.events.set_error_handler() <energyquantified.api.EventsAPI.set_error_handler>`:

.. code-block:: python

    def error_message_handler(error):
        print(f"Error occured: {error}")

    eq.events.set_error_handler(error_message_handler)

You can attach the handlers even before you connect:

.. code-block:: python

    # Set handlers
    eq.events.set_message_handler(message_handler)
    eq.events.set_error_handler(error_message_handler)
    # Connect
    eq.events.connect()


Restarts and network errors
---------------------------

.. _remember last id:

Remember ``last_id`` between processes runs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The client can remember the last event received, and continue where it left off
on restarts.

To enable this feature, supply the ``last_id_file`` parameter in
:py:meth:`eq.events.connect <energyquantified.api.EventsAPI.connect>` with a
file path. Make sure that you have read and write access to the file path.

.. code-block:: python

    eq.events.connect(last_id_file="last_id_file.json")

The client regurarly updates the file at a defined interval (~0.5/min), when
the connection drops, and when execution of the program is terminated (for any
reason). The next time you connect to the stream, assuming the same file path
for ``last_id_file`` and that you have not altered the file, the client will
request all events after the last one you received.

Providing the ``last_id`` parameter to
:py:meth:`subscribe_curve_events() <energyquantified.api.EventsAPI.subscribe_curve_events>`
will override the id from file (and update the file).


Automatic subscribe after reconnect
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When a client reconnects, it will resubscribe with the previous filters, and ask
for events that occured during downtime.

.. code-block:: python

    import time

    for event in eq.events.get_next():
        if event.event_type == EventType.DISCONNECTED:
            # Not connected and event queue is empty
            print(f"Not connected: {event}")
            # Wait 30 seconds before reconnecting
            time.sleep(30)
            # Try to reconnect
            eq.events.connect()
            continue


Server only keeps the most recent events
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While the API supports fetching older events, we only keep the latest ~10.000
(at the time of writing). In most cases that should cover events for the last
10-15 minutes.
