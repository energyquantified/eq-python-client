Curve update events
===================

This page shows how to load curve events from Energy Quantified's WebSocket API
streamed in real-time. The examples below expect you to have an initialized instance
instance of the :py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`
API client called ``eq``.

Operations described here are available under ``eq.events.*``.


Terminology
-----------


Curve events
~~~~~~~~~~~~

Class reference: :py:class:`eq.events.CurveUpdateEvent <energyquantified.events.CurveUpdateEvent>`

Energy Quantified creates curve events whenever data in a
:py:class:`~energyquantified.metadata.Curve` changes. Events provide information
about what kind of operation was done (e.g., delete, update) on the curve,
timestamps of the first and last affected values, and the total number of
affected values. It also includes an
:py:class:`~energyquantified.metadata.Instance` where relevant.

**Example:** If values were updated at a 15-minute frequency for Germany's consumption normal at
``2023-01-01 01:15`` and ``2023-01-01 01:45``, the following event would be produced:

.. code-block:: python

    <CurveUpdateEvent:
        event_id="1234567890123-0",
        curve="DE Consumption MWh/h 15min Normal",
        event_type=EventType.CURVE_UPDATE,
        begin="2023-01-01 01:15",
        end="2023-01-01 02:00",
        num_values=2>

The ``event_id`` attribute uniquely identifies curve events. Event IDs are strings
of two numbers separated by a dash ("-"). The first number is exactly 13 digits
long and represents the creation timestamp for the event.
The second number is a serial, which increments when multiple events are
within the same millisecond.


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
      Not connected to the push feed

    * :py:class:`EventType.TIMEOUT <energyquantified.events.EventType>`:
      Filler event enabling users to act between events during quiet times.
      Timeout events occur when the user provides the ``timeout`` parameter in
      :py:meth:`eq.events.get_next() <energyquantified.api.EventsAPI.get_next>`.


Filters
~~~~~~~

To receive curve events, one must subscribe by providing a list of filters. You
will receive events matching **any** of your filters.

A filter matches if all set variables match the event. For instance, a filter with
``areas=[Area.DE, Area.FR]`` and ``data_types=[DataType.ACTUAL, DataType.FORECAST]``
matches curves for France or Germany, with data type Actual or Forecast.

Due to WebSockets' bidirectional communication protocol, you can re-subscribe
with new filters on the fly while already listening to the stream.


Quickstart
----------

First, we must connect to the WebSockets endpoint:

.. code-block:: python

    eq.events.connect()

Once connected, we can specify our filters and subscribe to them. In this example,
we create filters for Actual and Forecast data in Germany, France or Great Britain:

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

Putting it all together, this is how you connect, subscribe, and start listening
for curve events:

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

The client tries to reconnect on network errors automatically. You can override
the number of reconnect attempts by providing the ``reconnect_attempts`` parameter.
The number of attempts reset once if a connection is re-established.

.. code-block:: python

    eq.events.connect(reconnect_attempts=5)


Disconnecting
-------------

Method reference: :py:meth:`eq.events.disconnect() <energyquantified.api.EventsAPI.disconnect>`

Disconnect from the stream by calling
:py:meth:`disconnect() <energyquantified.api.EventsAPI.disconnect>` or
:py:meth:`close() <energyquantified.api.EventsAPI.close>`. The
:py:meth:`get_next() <energyquantified.api.EventsAPI.get_next>` method still returns
all events received before disconnecting.

.. code-block:: python

    eq.events.disconnect()


Subscribing
-----------

Method reference: :py:meth:`eq.events.subscribe_curve_events() <energyquantified.api.EventsAPI.subscribe_curve_events>`


To receive curve events, one must subscribe by providing a list of filters.

You can update your filters while already subscribed by calling
:py:meth:`subscribe_curve_events() <energyquantified.api.EventsAPI.subscribe_curve_events>`
with the new filters.

After subscribing, the server responds with a
:py:class:`CurvesSubscribeResponse <energyquantified.events.CurvesSubscribeResponse>`
object. By default, the client logs the result (``INFO`` level for a successful
subcription, ``ERROR`` when it fails). You can override this behaviour by supplying
the ``callback`` parameter with your function:

.. code-block:: python

    def on_subscribe(response: CurvesSubscribeResponse):
        if response.ok:
            print("Subscribed")
        else:
            print("Failed to subscribe")

    eq.events.subscribe_curve_events(
        filters=[...],
        callback=on_subscribe
    )


Providing filters
~~~~~~~~~~~~~~~~~

There are two different filter types for curve events:

    * :py:class:`~energyquantified.events.CurveNameFilter`: Filter by
      curves/curve names

    * :py:class:`~energyquantified.events.CurveAttributeFilter`: Filter by curve
      attributes similar to the curve search

However, both filter types support filtering on ``event_types``, ``begin``
and ``end``.

You can subscribe with a combination of both
:py:class:`CurveNameFilter <energyquantified.events.CurveNameFilter>` and
:py:class:`CurveAttributeFilter <energyquantified.events.CurveAttributeFilter>`.
The maximum number of filters allowed is limited to ten (10). You will receive
events for curves that match **any** of your filters, (a filter matches if
**all set variables** match the event).

Subscribe to curve events with one or more filters:

.. code-block:: python

    # Single filter
    eq.events.subscribe_curve_events(filters=filter_1)

.. code-block:: python

    # Multiple filters
    eq.events.subscribe_curve_events(filters=[
        filter_1,
        filter_2,
        filter_3,
    ])


Creating a filter
^^^^^^^^^^^^^^^^^^^^^^

Set filter variables in the constructor or via the ``set_<variable>()`` methods:

.. code-block:: python

    from datetime import datetime
    from energyquantified.events import CurveAttributeFilter, EventType
    from energyquantified.metadata import Area

    # Provide values to the Filter constructor
    my_filter = CurveAttributeFilter(
        event_types=EventType.CURVE_UPDATE,
        begin=datetime(2023, 9, 1),
        areas=Area.DE,
    )

    # Provide values via set_*-methods (fluently)
    my_filter = (
        CurveAttributeFilter()
        .set_event_types(EventType.CURVE_UPDATE)
        .set_begin(datetime(2023, 9, 1))
        .set_areas(Area.DE),
    )

Set multiple values by providing a list, either to the constructor or to
each ``set_<variable>()`` method:

.. code-block:: python

    from energyquantified.events import CurveAttributeFilter, EventType
    from energyquantified.metadata import Area, DataType

    # Provide a list of values in the constructor
    my_filter = CurveAttributeFilter(
        event_types=[EventType.CURVE_UPDATE, EventType.CURVE_DELETE],
        areas=[Area.DE, Area.FR],
        data_types=[DataType.ACTUAL, DataType.FORECAST],
    )

    # Provide a list of values via set_*-methods (fluently)
    my_filter = (
        CurveAttributeFilter()
        .set_event_types([EventType.CURVE_UPDATE, EventType.CURVE_DELETE])
        .set_areas([Area.DE, Area.FR]),
        .set_data_types([DataType.ACTUAL, DataType.FORECAST])
    )

You can also provide strings instead of objects:

.. code-block:: python

    my_filter = CurveAttributeFilter(
        event_types=["CURVE_UPDATE", "CURVE_DELETE"],
        areas=["DE", "FR"],
        data_types=["ACTUAL", "FORECAST"],
    )


Filter specific curves
^^^^^^^^^^^^^^^^^^^^^^

Class reference: :py:class:`energyquantified.events.CurveNameFilter`

Use the :py:class:`CurveNameFilter <energyquantified.events.CurveNameFilter>` to
match specific curves by providing a list of :py:class:`Curve <energyquantified.metadata.Curve>`
objects or curve names.

**Available parameters:**

    * ``event_types``: Filter by
      :py:class:`EventType <energyquantified.events.EventType>`.

    * ``curves``: Filter by :py:class:`Curve <energyquantified.metadata.Curve>`
      objects or curve names.

    * ``begin``: The earliest date to look for changed values (inclusive).

    * ``end``: The last date to look for changed values (exclusive).

The code snippet below illustrates creating a filter for updates in a certain
date range for two curves. You will receive a curve event whenever a value
between ``begin`` (inclusive) and ``end`` (exclusive) changes for either of the
curves.

.. code-block:: python

    from datetime import date
    from energyquantified.events import CurveNameFilter, EventType

    # Providing curves by name
    my_filter = CurveNameFilter(
        event_types=EventType.CURVE_UPDATE,
        curves=[
            "DE Wind Power Production MWh/h 15min Actual",
            "FR Wind Power Production MWh/h 15min Forecast",
        ],
        begin=date(2023, 9, 1),
        end=date(2023, 10, 1),
    )


Filter by curve attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^

Class reference: :py:class:`energyquantified.events.CurveAttributeFilter`

Use the :py:class:`CurveAttributeFilter <energyquantified.events.CurveAttributeFilter>`
to filter curve events based on :py:class:`Curve <energyquantified.metadata.Curve>`
attributes.

**Available parameters:**

    * ``event_types``: Filter by
      :py:class:`EventType <energyquantified.events.EventType>`.

    * ``q``: Freetext search alike the curve search (e.g., "wind power germany").

    * ``areas``: Filter by :py:class:`Area <energyquantified.metadata.Area>`.

    * ``data_types``: Filter by
      :py:class:`DataType <energyquantified.metadata.DataType>`.

    * ``commodities``: Filter by commodities.

    * ``categories``: Filter by categories.

    * ``exact_categories``: Filter by one or more exact categories. An exact
      category is a string of ordered categories separated by space (e.g.,
      ``"Wind Power Production"``).

    * ``begin``: The earliest date to look for changed values (inclusive).

    * ``end``: The last date to look for changed values (exclusive).

The code snippet below illustrates how to filter curve updates for January 2023
in Actual or Forecast data with the ``Wind Power Production``
category in Germany or France.

.. code-block:: python

    from datetime import date
    from energyquantified.events import CurveAttributeFilter, EventType
    from energyquantified.metadata import Area, DataType

    # Filter by curve attributes
    my_filter = CurveAttributeFilter(
        event_types=EventType.CURVE_UPDATE,
        data_types=[DataType.ACTUAL, DataType.FORECAST],
        exact_categories="Wind Power Production",
        areas=[Area.DE, Area.FR],
        begin=date(2023, 1, 1),
        end=date(2023, 2, 1),
    )

For a curve event to match the above filter, it must meet all of the following
requirements:

    * The event type is ``CURVE_UPDATE``
    * The data type is ``Actual`` or ``Forecast``
    * The exact category is ``Wind Power Production``
    * The area is Germany or France
    * At least one value in January 2023 is updated


Providing ``last_id`` (advanced)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Event IDs are strings of two numbers separated by a dash ("-"). The first number
is a timestamp. If you supply the optional parameter ``last_id`` to
:py:meth:`subscribe_curve_events() <energyquantified.api.EventsAPI.subscribe_curve_events>`,
you will receive events created after this ID:

.. code-block:: python

    # Subscribe and receive events after provided last_id only
    eq.events.subscribe_curve_events(
        filters=[...],
        last_id="1234567890123-0"
    )

This ID takes priority over the recommended ``last_id_file`` approach (further
described in :ref:`Remember last_id between processes runs <remember last id>`).


Handling events
---------------

Method reference: :py:meth:`eq.events.get_next() <energyquantified.api.EventsAPI.get_next>`

After subscribing to curve events, you will immediately start to receive events
matching your filters. Loop over the incoming events like so:

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
