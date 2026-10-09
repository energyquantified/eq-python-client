Intraday trades
===============

Trade operations are available under ``eq.trades.*`` for curves whose
``curve_type`` is ``TRADES``.

The operations are grouped to follow the API's endpoint structure. Contract
searches live directly on ``eq.trades.*``, matching
``/trades/{curve}/contracts/``, while OHLC data is served from
``/trades/{curve}/ohlc/`` and is therefore grouped under ``eq.trades.ohlc.*``.

List contracts
--------------

Use :py:meth:`eq.trades.contracts()
<energyquantified.api.TradesAPI.contracts>` to find contracts in a delivery
interval:

.. code-block:: python

   from energyquantified.time import Frequency

   contracts = eq.trades.contracts(
       curve,
       begin="2026-08-18 00:00:00+02:00",
       end="2026-08-19 00:00:00+02:00",
       periods=[Frequency.PT15M, Frequency.PT1H],
   )

Each item is an :py:class:`energyquantified.data.TradeContract` with a
``period`` and a timezone-aware ``delivery`` attribute. You can also filter
with ``exclude_periods``, ``after_time_of_day`` and ``before_time_of_day``.

Load trade OHLC data
--------------------

Use :py:meth:`eq.trades.ohlc.load() <energyquantified.api.TradesOhlcAPI.load>`
to load OHLC data for all contracts matching a delivery-interval search. The result is
an :py:class:`energyquantified.data.TradeOHLCSeriesList` with one
:py:class:`energyquantified.data.TradeOHLCSeries` per contract. The curve,
frequency, unit and denominator are the same for every series, so they are
also available on the list itself.

Parameters for ``ohlc.load``
~~~~~~~~~~~~~~~~~~~~~~~

``curve``
   The trade curve or its name. When a
   :py:class:`energyquantified.metadata.Curve` is supplied, its
   ``curve_type`` must be ``TRADES``.

``begin`` and ``end``
   Required delivery-interval boundaries. ``begin`` is inclusive and ``end``
   is exclusive, and they cannot be more than one week apart. They accept
   strings, :py:class:`datetime.date`, or :py:class:`datetime.datetime`
   values. A value without a UTC offset is interpreted in the curve's
   timezone.

``after_time_of_day`` and ``before_time_of_day``
   Optional local-time filters on the beginning of each contract's delivery.
   ``after_time_of_day`` is inclusive, while ``before_time_of_day`` is
   exclusive. Both accept a ``datetime.time`` or a string such as ``"08:00"``.
   If both are set, the after-time must be earlier than the before-time.

``periods`` and ``exclude_periods``
   Include or exclude contracts by the length of their delivery interval.
   Supply one value or a collection of
   :py:class:`energyquantified.time.Frequency` values or strings. Supported
   delivery periods are ``PT15M``, ``PT30M``, and ``PT1H``. For example,
   ``periods=[Frequency.PT15M, "PT1H"]`` includes 15-minute and hourly
   contracts.

``frequency``
   Optionally aggregate each contract's trade data into coarser buckets. It
   accepts a :py:class:`energyquantified.time.Frequency` or frequency string.
   The frequency cannot be finer than ``PT1M`` or coarser than ``P1D``.
   Buckets are aligned backwards from the contract's delivery minus
   ``min_lead_time``, as described below. If omitted, data is returned at the
   frequency of ``PT1M``.

``aggregate_by_contract``
   Set to ``True`` to combine all available trade data for each contract into
   one OHLC value. It defaults to ``False`` and cannot be combined with
   ``frequency``.

``min_lead_time`` and ``max_lead_time``
   Only include trades made within this window before delivery begins. Both
   accept a ``datetime.timedelta`` or an ISO-8601 duration string such as
   ``"PT36H"``. They must be between zero and 36 hours, be a whole number of
   minutes, and ``min_lead_time`` must be shorter than ``max_lead_time``.
   A trade is included when its lead time is greater than ``min_lead_time``
   and at most ``max_lead_time``. They default to ``PT0S`` and ``PT36H``,
   which selects every trade made in the 36 hours before delivery.

``unit``
   Convert the price fields (open, high, low, close, and VWAP) to another
   compatible unit. Volume and trade count are not price-converted.

Do not confuse ``periods`` with ``frequency``. A contract's period describes
its delivery duration, while ``frequency`` describes the time buckets used for
its trade observations.

How backwards aggregation works
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"Backwards" describes how bucket boundaries are calculated; it does not mean
that the returned series is in reverse chronological order. The beginning of
the contract's delivery, minus ``min_lead_time`` (zero by default), is used
as an anchor. Starting at that instant, the requested ``frequency`` is
repeatedly subtracted to form trading-time buckets:

.. code-block:: text

   delivery - frequency                              delivery
                 |------------------------------------|
                   final pre-delivery bucket

   delivery - 2 * frequency                delivery - frequency
                 |------------------------------------|
                   preceding bucket

For example, suppose a contract's delivery begins at ``12:45`` and
``frequency=Frequency.PT1H``. The buckets are aligned to ``:45`` rather than
to the wall-clock hour:

.. code-block:: text

   09:45              10:45              11:45              12:45
     |------------------|------------------|------------------|
       earlier bucket     preceding bucket   final bucket       delivery begins

The returned value whose ``traded_at`` is ``11:45`` summarizes trades in
``[11:45, 12:45)``: the start is inclusive and the end is exclusive. The
previous values summarize ``[10:45, 11:45)`` and ``[09:45, 10:45)``. Thus,
without a ``min_lead_time``, the last bucket is a complete bucket ending
exactly when delivery begins; it is not a partial ``[12:00, 12:45)``
wall-clock bucket.

Setting ``min_lead_time`` moves the anchor away from delivery before the
buckets are calculated. For the same ``12:45`` delivery,
``frequency=Frequency.PT1H`` and ``min_lead_time=timedelta(minutes=15)`` make
``12:30`` the exclusive end of the selected trading window:

.. code-block:: text

   09:30              10:30              11:30              12:30       12:45
     |------------------|------------------|------------------|-----------|
       earlier bucket     preceding bucket   final bucket       excluded    delivery
                                                                15 minutes  begins

The final value now has ``traded_at`` set to ``11:30`` and summarizes trades
in ``[11:30, 12:30)``. Trades at or after ``12:30`` have a lead time of 15
minutes or less and are excluded, as the ``min_lead_time`` boundary is
exclusive. Because the buckets are aligned backwards from ``12:30`` rather
than from ``12:45``, the final bucket still covers a full hour.

This alignment is calculated independently for each contract. With the same
``PT1H`` frequency, a contract delivered at ``13:00`` has buckets beginning on
the hour, while one delivered at ``12:45`` has buckets beginning at ``:45``.
The resulting series is still returned in chronological order, and every
``traded_at`` value denotes the beginning of its bucket.

When source values are combined within a bucket, ``open`` comes from the
earliest value, ``close`` from the latest, ``high`` and ``low`` are the extrema,
``vwap`` is weighted by volume, and ``volume`` and ``count`` are summed.
``aggregate_by_contract=True`` is different: it collapses all available
trading history for each contract into one OHLC value instead of forming
repeated fixed-frequency buckets.

Load unaggregated data for every contract in an interval:

.. code-block:: python

   series_list = eq.trades.ohlc.load(
       curve,
       begin="2026-08-18",
       end="2026-08-19",
   )

Filter by delivery time, exclude hourly contracts, and only look at the last
two hours before delivery:

.. code-block:: python

   from datetime import time, timedelta
   from energyquantified.time import Frequency

   series_list = eq.trades.ohlc.load(
       curve,
       begin="2026-08-18 00:00:00+02:00",
       end="2026-08-25 00:00:00+02:00",
       after_time_of_day=time(8, 0),
       before_time_of_day=time(20, 0),
       exclude_periods=Frequency.PT1H,
       max_lead_time=timedelta(hours=2),
   )

Aggregate a 1-minute trade curve to 5-minute buckets and convert its prices:

.. code-block:: python

   series_list = eq.trades.ohlc.load(
       curve,
       begin="2026-08-18",
       end="2026-08-19",
       frequency=Frequency.PT5M,
       unit="NOK",
   )

Return one OHLC value for each matching contract:

.. code-block:: python

   series_list = eq.trades.ohlc.load(
       curve,
       begin="2026-08-18",
       end="2026-08-19",
       aggregate_by_contract=True,
   )

Convert trade OHLC data to time series
--------------------------------------

Use :py:meth:`eq.trades.ohlc.load_as_timeseries()
<energyquantified.api.TradesOhlcAPI.load_as_timeseries>` to extract a single OHLC
field for every matching contract and get it back as a
:py:class:`energyquantified.data.TimeseriesList`. Each time series carries the
contract it was extracted from in its ``trade_contract`` attribute, so the
result converts cleanly to a ``pandas.DataFrame`` with one column per
contract.

It takes the same contract filters and aggregation options as ``load``, plus
two of its own:

``field``
   Required. The field to extract: a
   :py:class:`energyquantified.metadata.TradeOHLCField` or the corresponding
   string (``open``, ``high``, ``low``, ``close``, ``vwap``, ``volume``, or
   ``count``).

``fill``
   How to handle buckets without trades. ``no-fill`` (the default) leaves them
   empty. ``fill-holes`` and ``forward-fill`` both fill gaps between
   observations with the previous value.

Like in ``load``, ``begin`` and ``end`` only select contracts by delivery.
Each time series runs from the first to the last bucket with trades for its
contract, so the series in the list usually cover different trading-time
intervals. A contract without trades gives an empty time series.

.. code-block:: python

   from energyquantified.metadata import TradeOHLCField

   timeseries_list = eq.trades.ohlc.load_as_timeseries(
       curve,
       field=TradeOHLCField.VWAP,
       begin="2026-08-18",
       end="2026-08-19",
       frequency=Frequency.PT15M,
       fill="forward-fill",
   )

   df = timeseries_list.to_pd_df()
