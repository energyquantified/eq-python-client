Intraday trades
===============

This page shows how to load OHLC data for intraday trades. All examples below
expects you to have an initialized instance of the client called ``eq``, and
a trade curve called ``curve``:

   >>> curve = eq.metadata.curve('DE Intraday Continuous EUR/MWh EPEX Trades')

Operations described here are available under ``eq.trades.*``.

**Requirements:** Use these operations for curves with ``curve_type`` set
to any of the following:

 * ``TRADES``

The operations are grouped to follow the API's endpoint structure. Contract
searches live directly on ``eq.trades.*``, matching
``/trades/{curve}/contracts/``, while OHLC data is served from
``/trades/{curve}/ohlc/`` and is therefore grouped under ``eq.trades.ohlc.*``.

Trade objects
-------------

Each trade curve holds the intraday trades for one market, stored in
1-minute (``PT1M``) buckets of trading time. A trade is always made for a
**contract**, which is identified by the length of its delivery interval
and the start of delivery:

.. code-block::

   class TradeContract:
       period: Frequency
       delivery: datetime

The parameters:

 * **period** – The length of the delivery interval: ``PT15M``, ``PT30M``
   or ``PT1H``.
 * **delivery** – The beginning of the delivery interval, in the curve's
   timezone.

The OHLC data for a contract is a series of
:py:class:`TradeOHLC <energyquantified.data.TradeOHLC>` values, one per bucket
of trading time:

.. code-block::

   class TradeOHLC:
       traded_at: datetime
       open: number
       high: number
       low: number
       close: number
       vwap: number
       volume: number
       count: int

The parameters:

 * **traded_at** – The beginning of the trading-time bucket. This is when
   the trades happened, not when the contract is delivered.
 * **open**, **high**, **low** and **close** – The first, highest, lowest
   and last price traded in the bucket.
 * **vwap** – The volume-weighted average price in the bucket.
 * **volume** – The total volume traded in the bucket.
 * **count** – The number of trades in the bucket.

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
   The frequency cannot be finer than ``PT1M`` or coarser than ``PT1H``.
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

A list loaded with ``frequency=Frequency.PT15M``, and the series and values
in it, print like this:

   >>> series_list
   <TradeOHLCSeriesList: frequency=PT15M, curve="DE Intraday Continuous EUR/MWh EPEX Trades", unit="EUR", denominator="MWh", items=2>

   >>> series_list[0]
   <TradeOHLCSeries: frequency=PT15M, curve="DE Intraday Continuous EUR/MWh EPEX Trades", contract=<TradeContract: period=PT15M, delivery=2026-08-18 12:00:00+02:00>, unit="EUR", denominator="MWh", items=3>

   >>> series_list[0][0]
   <TradeOHLC: traded_at=2026-08-18 11:15:00+02:00, open=61.2, high=62.0, low=60.8, close=61.5, vwap=61.43, volume=12.4, count=9>

Convert trade OHLC data to a data frame
---------------------------------------

Both :py:class:`TradeOHLCSeriesList <energyquantified.data.TradeOHLCSeriesList>`
and :py:class:`TradeOHLCSeries <energyquantified.data.TradeOHLCSeries>` convert
to a data frame in a flat layout, with one row per contract and trading-time
bucket. The ``delivery`` and ``traded_at`` columns are in the curve's
timezone.

Convert to a ``pandas.DataFrame`` like this:

   >>> series_list.to_pandas_dataframe()
     period                  delivery                 traded_at  open  high   low  close   vwap  volume  count
   0  PT15M 2026-08-18 12:00:00+02:00 2026-08-18 11:15:00+02:00  61.2  62.0  60.8   61.5  61.43    12.4      9
   1  PT15M 2026-08-18 12:00:00+02:00 2026-08-18 11:30:00+02:00  61.5  63.1  61.5   62.9  62.37    20.1     14
   2  PT15M 2026-08-18 12:00:00+02:00 2026-08-18 11:45:00+02:00  62.9  64.0  62.2   63.6  63.25    35.7     27
   3  PT15M 2026-08-18 12:15:00+02:00 2026-08-18 11:30:00+02:00  58.0  58.4  57.1   57.6  57.82     8.3      6
   4  PT15M 2026-08-18 12:15:00+02:00 2026-08-18 11:45:00+02:00  57.6  59.2  57.6   58.9  58.51    16.0     11
   5  PT15M 2026-08-18 12:15:00+02:00 2026-08-18 12:00:00+02:00  58.9  60.3  58.5   60.1  59.47    41.2     33

Convert to a ``polars.DataFrame`` like this:

   >>> series_list.to_polars_dataframe()
   shape: (6, 10)
   ┌────────┬──────────────────────────┬──────────────────────────┬──────┬──────┬──────┬───────┬───────┬────────┬───────┐
   │ period ┆ delivery                 ┆ traded_at                ┆ open ┆ high ┆ low  ┆ close ┆ vwap  ┆ volume ┆ count │
   │ ---    ┆ ---                      ┆ ---                      ┆ ---  ┆ ---  ┆ ---  ┆ ---   ┆ ---   ┆ ---    ┆ ---   │
   │ str    ┆ datetime[μs, CET]        ┆ datetime[μs, CET]        ┆ f64  ┆ f64  ┆ f64  ┆ f64   ┆ f64   ┆ f64    ┆ i64   │
   ╞════════╪══════════════════════════╪══════════════════════════╪══════╪══════╪══════╪═══════╪═══════╪════════╪═══════╡
   │ PT15M  ┆ 2026-08-18 12:00:00 CEST ┆ 2026-08-18 11:15:00 CEST ┆ 61.2 ┆ 62.0 ┆ 60.8 ┆ 61.5  ┆ 61.43 ┆ 12.4   ┆ 9     │
   │ PT15M  ┆ 2026-08-18 12:00:00 CEST ┆ 2026-08-18 11:30:00 CEST ┆ 61.5 ┆ 63.1 ┆ 61.5 ┆ 62.9  ┆ 62.37 ┆ 20.1   ┆ 14    │
   │ PT15M  ┆ 2026-08-18 12:00:00 CEST ┆ 2026-08-18 11:45:00 CEST ┆ 62.9 ┆ 64.0 ┆ 62.2 ┆ 63.6  ┆ 63.25 ┆ 35.7   ┆ 27    │
   │ PT15M  ┆ 2026-08-18 12:15:00 CEST ┆ 2026-08-18 11:30:00 CEST ┆ 58.0 ┆ 58.4 ┆ 57.1 ┆ 57.6  ┆ 57.82 ┆ 8.3    ┆ 6     │
   │ PT15M  ┆ 2026-08-18 12:15:00 CEST ┆ 2026-08-18 11:45:00 CEST ┆ 57.6 ┆ 59.2 ┆ 57.6 ┆ 58.9  ┆ 58.51 ┆ 16.0   ┆ 11    │
   │ PT15M  ┆ 2026-08-18 12:15:00 CEST ┆ 2026-08-18 12:00:00 CEST ┆ 58.9 ┆ 60.3 ┆ 58.5 ┆ 60.1  ┆ 59.47 ┆ 41.2   ┆ 33    │
   └────────┴──────────────────────────┴──────────────────────────┴──────┴──────┴──────┴───────┴───────┴────────┴───────┘

Use ``to_pd_df()`` and ``to_pl_df()`` as shorthands. A contract without
trades has no rows in the data frame.

Convert trade OHLC data to time series
--------------------------------------

Use :py:meth:`eq.trades.ohlc.load_as_timeseries()
<energyquantified.api.TradesOhlcAPI.load_as_timeseries>` to extract a single OHLC
field for every matching contract and get it back as a
:py:class:`energyquantified.data.TimeseriesList`. Each time series carries the
contract it was extracted from in its ``trade_contract`` attribute, so the
result converts cleanly to a ``pandas.DataFrame`` with one column per
contract.

It takes the same contract filters and aggregation options as ``load``, but
two of them work differently:

``frequency``
   Buckets are aligned to the frequency itself, such as full hours for
   ``PT1H``, and not backwards from each contract's delivery. This puts the
   series for all contracts on the same time grid, so they line up in a data
   frame.

``unit``
   Converts the extracted field. Price fields (``open``, ``high``, ``low``,
   ``close`` and ``vwap``) are in the curve's currency, ``volume`` is in
   ``MWh/h`` and ``count`` has no unit. Price fields convert to other
   currencies and ``volume`` to other power units, such as ``MW``. ``count``
   cannot be converted. Converting a field to a unit it is not compatible
   with, such as ``volume`` to ``NOK``, fails with a validation error.

It also has two options of its own:

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
intervals. Contracts without trades are left out of the list.

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
