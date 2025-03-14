OHLC
====

This page shows how to load OHLC data (open, high, low, close). All examples
below expects you to have an initialized instance of the client called ``eq``.

Operations described here are available under ``eq.ohlc.*``.

**Requirements:** Use these operations for curves with ``curve_type`` set
to any of the following:

 * ``OHLC``

OHLC objects
------------

We group all products for a market into a single curve. For instance, we have
a curve called ``NP Futures Power Base EUR/MWh Nasdaq OHLC``, which contains
all power futures contracts for the system price in the Nord Pool area.

When loading OHLC data, the response is a list of OHLC objects. An OHLC object
consists of **open**, **high**, **low**, **close**, **settlement**, **volume**
and **open interest**. These fields may be missing/unset.

.. code-block::

   class OHLC:
       product: Product
       open: number
       high: number
       low: number
       close: number
       settlement: number
       volume: number
       open_interest: number

In addition to these fields, each OHLC object has a **product** field. The
**product** field describes which contract you are looking at:

.. code-block::

   class Product:
       traded: date
       period: Enum [DAY, WEEK, MONTH, QUARTER, SEASON, YEAR]
       front: integer
       delivery: date

Short descriptions for the attributes of ``Product`` objects:

- ``traded`` is the trading date
- ``period`` is the contract delivery period (day, week, month, quarter, year)
- ``front`` tells you which contract is closest to delivery (1 means the front contract, 2 means the second front, and so forth)
- ``delivery`` is the date when the contract goes into delivery


Load OHLC data
--------------

Method reference: :py:meth:`eq.ohlc.load() <energyquantified.api.OhlcAPI.load>`

Loading OHLC data is quite straight-forward. You must at least specify
these three parameters: **curve**, **begin** and **end**.

   >>> from datetime import date
   >>> ohlc_list = eq.ohlc.load(
   >>>    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
   >>>    begin=date(2020, 1, 1),   # or begin='2020-01-01'
   >>>    end=date(2020, 1, 6)      # or end='2020-01-06'
   >>> )

The response is a list of :class:`energyquantified.data.OHLC` objects. It is
ordered by trading date (chronologically) and period (alphabetically).
However, the list has a ``curve`` attribute that standard Python
``list``-objects do not:

   >>> ohlc_list.curve
   <Curve: "NP Futures Power Base EUR/MWh Nasdaq OHLC", curve_type=OHLC, subscription=FREEMIUM>

   >>> ohlc_list
   [<OHLC: <Product: traded=2020-01-02, period=DAY, front=1, delivery=2020-01-03>, open=, high=, low=, close=, settlement=26.56, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-01-02, period=DAY, front=2, delivery=2020-01-04>, open=23.0, high=23.0, low=23.0, close=23.0, settlement=24.0, volume=50.0, open_interest=>,
    ...
    <OHLC: <Product: traded=2020-01-02, period=MONTH, front=1, delivery=2020-02-01>, open=35.4, high=35.4, low=34.0, close=34.0, settlement=34.0, volume=394.0, open_interest=10678.0>,
    <OHLC: <Product: traded=2020-01-02, period=MONTH, front=2, delivery=2020-03-01>, open=32.8, high=33.0, low=32.21, close=32.21, settlement=32.21, volume=98.0, open_interest=10286.0>,
    ...
    <OHLC: <Product: traded=2020-01-02, period=QUARTER, front=1, delivery=2020-04-01>, open=28.2, high=28.2, low=26.95, close=27.0, settlement=27.0, volume=394.0, open_interest=8511.0>,
    <OHLC: <Product: traded=2020-01-02, period=QUARTER, front=2, delivery=2020-07-01>, open=26.35, high=26.5, low=25.75, close=25.75, settlement=25.75, volume=135.0, open_interest=6721.0>,
    ...

You can also filter on **period**. Say that we only want monthly contracts:

   >>> from energyquantified.metadata import ContractPeriod
   >>> ohlc_list = eq.ohlc.load(
   >>>    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 6),
   >>>    period=ContractPeriod.MONTH  # Only monthly contracts
   >>> )

Which will give you:

   >>> ohlc_list
   [<OHLC: <Product: traded=2020-01-02, period=MONTH, front=1, delivery=2020-02-01>, open=35.4, high=35.4, low=34.0, close=34.0, settlement=34.0, volume=394.0, open_interest=10678.0>,
    <OHLC: <Product: traded=2020-01-02, period=MONTH, front=2, delivery=2020-03-01>, open=32.8, high=33.0, low=32.21, close=32.21, settlement=32.21, volume=98.0, open_interest=10286.0>,
    <OHLC: <Product: traded=2020-01-02, period=MONTH, front=3, delivery=2020-04-01>, open=30.8, high=30.8, low=30.0, close=30.0, settlement=30.0, volume=6.0, open_interest=584.0>,
    <OHLC: <Product: traded=2020-01-02, period=MONTH, front=4, delivery=2020-05-01>, open=, high=, low=, close=, settlement=26.35, volume=, open_interest=55.0>,
    <OHLC: <Product: traded=2020-01-02, period=MONTH, front=5, delivery=2020-06-01>, open=, high=, low=, close=, settlement=24.73, volume=, open_interest=65.0>,
    <OHLC: <Product: traded=2020-01-02, period=MONTH, front=6, delivery=2020-07-01>, open=, high=, low=, close=, settlement=22.93, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-01-03, period=MONTH, front=1, delivery=2020-02-01>, open=34.3, high=34.6, low=33.75, close=34.5, settlement=34.4, volume=321.0, open_interest=10483.0>,
    <OHLC: <Product: traded=2020-01-03, period=MONTH, front=2, delivery=2020-03-01>, open=32.4, high=32.85, low=31.95, close=32.7, settlement=32.7, volume=86.0, open_interest=10243.0>,
    <OHLC: <Product: traded=2020-01-03, period=MONTH, front=3, delivery=2020-04-01>, open=30.0, high=30.7, low=30.0, close=30.35, settlement=30.35, volume=38.0, open_interest=589.0>,
    <OHLC: <Product: traded=2020-01-03, period=MONTH, front=4, delivery=2020-05-01>, open=27.0, high=27.0, low=27.0, close=27.0, settlement=27.0, volume=4.0, open_interest=55.0>,
    <OHLC: <Product: traded=2020-01-03, period=MONTH, front=5, delivery=2020-06-01>, open=24.7, high=24.7, low=24.7, close=24.7, settlement=24.7, volume=1.0, open_interest=65.0>,
    <OHLC: <Product: traded=2020-01-03, period=MONTH, front=6, delivery=2020-07-01>, open=23.55, high=23.55, low=23.55, close=23.55, settlement=23.55, volume=3.0, open_interest=>]

Notice that we only get data for two trading days. That is because the market
is only open on 2 January and 3 January in the date interval we queried.

And then you can also filter on **front** to get the continuous front contract:

   >>> from energyquantified.metadata import ContractPeriod
   >>> ohlc_list = eq.ohlc.load(
   >>>    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 10),
   >>>    period=ContractPeriod.MONTH,
   >>>    front=1   # The front contract only
   >>> )

   >>> ohlc_list
   [<OHLC: <Product: traded=2020-01-02, period=MONTH, front=1, delivery=2020-02-01>, open=35.4, high=35.4, low=34.0, close=34.0, settlement=34.0, volume=394.0, open_interest=10678.0>,
    <OHLC: <Product: traded=2020-01-03, period=MONTH, front=1, delivery=2020-02-01>, open=34.3, high=34.6, low=33.75, close=34.5, settlement=34.4, volume=321.0, open_interest=10483.0>,
    <OHLC: <Product: traded=2020-01-06, period=MONTH, front=1, delivery=2020-02-01>, open=33.9, high=33.9, low=32.1, close=32.1, settlement=32.1, volume=296.0, open_interest=10527.0>,
    <OHLC: <Product: traded=2020-01-07, period=MONTH, front=1, delivery=2020-02-01>, open=31.55, high=31.77, low=31.05, close=31.2, settlement=31.2, volume=311.0, open_interest=10405.0>,
    <OHLC: <Product: traded=2020-01-08, period=MONTH, front=1, delivery=2020-02-01>, open=30.55, high=30.55, low=28.8, close=29.5, settlement=29.45, volume=575.0, open_interest=10590.0>,
    <OHLC: <Product: traded=2020-01-09, period=MONTH, front=1, delivery=2020-02-01>, open=29.55, high=30.4, low=29.55, close=30.25, settlement=30.1, volume=322.0, open_interest=10766.0>]

Or you can filter on the **delivery** date to get the development for a specific
contract:

   >>> from energyquantified.metadata import ContractPeriod
   >>> ohlc_list = eq.ohlc.load(
   >>>    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 10),
   >>>    period=ContractPeriod.MONTH,
   >>>    delivery=date(2020, 6, 1)  # The June contract
   >>> )

   >>> ohlc_list
   [<OHLC: <Product: traded=2020-01-02, period=MONTH, front=5, delivery=2020-06-01>, open=, high=, low=, close=, settlement=24.73, volume=, open_interest=65.0>,
    <OHLC: <Product: traded=2020-01-03, period=MONTH, front=5, delivery=2020-06-01>, open=24.7, high=24.7, low=24.7, close=24.7, settlement=24.7, volume=1.0, open_interest=65.0>,
    <OHLC: <Product: traded=2020-01-06, period=MONTH, front=5, delivery=2020-06-01>, open=, high=, low=, close=, settlement=22.33, volume=, open_interest=65.0>,
    <OHLC: <Product: traded=2020-01-07, period=MONTH, front=5, delivery=2020-06-01>, open=, high=, low=, close=, settlement=22.28, volume=, open_interest=65.0>,
    <OHLC: <Product: traded=2020-01-08, period=MONTH, front=5, delivery=2020-06-01>, open=21.85, high=22.47, low=21.85, close=22.47, settlement=22.71, volume=8.0, open_interest=65.0>,
    <OHLC: <Product: traded=2020-01-09, period=MONTH, front=5, delivery=2020-06-01>, open=23.45, high=23.45, low=23.4, close=23.4, settlement=23.4, volume=8.0, open_interest=73.0>]

**Note:** You cannot specify both **front** and **delivery** at the same time.


Load for latest trading day
---------------------------

Method reference: :py:meth:`eq.ohlc.latest() <energyquantified.api.OhlcAPI.latest>`

Loading all OHLC data for the latest available trading day. You must only
specify one parameter: **curve**. You may also specify an optional **date**
parameter to load data for the latest trading day up to and including the
given date.

   >>> latest_list = eq.ohlc.latest('NP Futures Power Base EUR/MWh Nasdaq OHLC')

The response is an list :class:`energyquantified.data.OHLCList` of
:class:`energyquantified.data.OHLC` objects:

   >>> latest_list.curve
   <Curve: "NP Futures Power Base EUR/MWh Nasdaq OHLC", curve_type=OHLC, subscription=FREEMIUM>

   >>> latest_list
   [<OHLC: <Product: traded=2020-10-15, period=DAY, front=1, delivery=2020-10-16>, open=, high=, low=, close=, settlement=23.24, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-10-15, period=DAY, front=2, delivery=2020-10-17>, open=, high=, low=, close=, settlement=19.0, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-10-15, period=DAY, front=3, delivery=2020-10-18>, open=, high=, low=, close=, settlement=16.0, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-10-15, period=MONTH, front=1, delivery=2020-11-01>, open=23.5, high=23.5, low=22.3, close=22.3, settlement=22.35, volume=343.0, open_interest=10104.0>,
    <OHLC: <Product: traded=2020-10-15, period=MONTH, front=2, delivery=2020-12-01>, open=25.65, high=25.65, low=24.4, close=24.4, settlement=24.4, volume=68.0, open_interest=9772.0>,
    <OHLC: <Product: traded=2020-10-15, period=MONTH, front=3, delivery=2021-01-01>, open=, high=, low=, close=, settlement=28.65, volume=, open_interest=192.0>,
    ...

There is no filtering for
:py:meth:`eq.ohlc.latest() <energyquantified.api.OhlcAPI.latest>`, like there
is for :py:meth:`eq.ohlc.load() <energyquantified.api.OhlcAPI.load>`.

Load as a forward curve
-----------------------

Method reference: :py:meth:`eq.ohlc.latest_as_periods() <energyquantified.api.OhlcAPI.latest_as_periods>`

This method loads all contracts for a trading day (the latest trading day by
default), sorts them and merges them into a single period-based series (like
a forward curve). It uses the settlement price by default, but you can
override it by setting the ``field`` parameter.

   >>> from datetime import date
   >>> from energyquantified.metadata import OHLCField
   >>> forward_curve = eq.ohlc.latest_as_periods(
   >>>    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
   >>>    date=date(2020, 12, 1),  # Optionally set trading date
   >>>    field=OHLCField.SETTLEMENT  # Optionally select field (defaults to SETTLEMENT)
   >>> )

Use the ``time_zone`` parameter to convert the data to the given timezone:

   >>> from energyquantified.time import UTC
   >>>
   >>> forward_curve = eq.ohlc.latest_as_periods(
   >>>    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
   >>>    time_zone=UTC
   >>> )

The result is a period-based series:

   >>> forward_curve
   <Periodseries: resolution=<Resolution: frequency=NONE, timezone=CET>, curve="NP Futures Power Base EUR/MWh Nasdaq OHLC", begin="2020-12-07 00:00:00+01:00", end="2027-01-01 00:00:00+01:00">

   >>> for p in forward_curve:
   >>>     print(p)
   <Period: begin=2020-12-07 00:00:00+01:00, end=2020-12-14 00:00:00+01:00, value=21.75>
   <Period: begin=2020-12-14 00:00:00+01:00, end=2020-12-21 00:00:00+01:00, value=22.25>
   <Period: begin=2020-12-21 00:00:00+01:00, end=2020-12-28 00:00:00+01:00, value=18.75>
   <Period: begin=2020-12-28 00:00:00+01:00, end=2021-01-04 00:00:00+01:00, value=19>
   <Period: begin=2021-01-04 00:00:00+01:00, end=2021-01-11 00:00:00+01:00, value=23.5>
   <Period: begin=2021-01-11 00:00:00+01:00, end=2021-01-18 00:00:00+01:00, value=25.8>
   <Period: begin=2021-01-18 00:00:00+01:00, end=2021-02-01 00:00:00+01:00, value=26.1>
   <Period: begin=2021-02-01 00:00:00+01:00, end=2021-03-01 00:00:00+01:00, value=25.8>
   ...

And, as described in the period-based series chapter, you can convert it to
a time series in your preferred resolution. Here we convert it to a daily
time series:

   >>> from energyquantified.time import Frequency
   >>> timeseries = forward_curve.to_timeseries(frequency=Frequency.P1D)

   >>> for d, v in timeseries:
   >>>     print(d, v)
   2020-12-07 00:00:00+01:00 21.75
   2020-12-08 00:00:00+01:00 21.75
   2020-12-09 00:00:00+01:00 21.75
   2020-12-10 00:00:00+01:00 21.75
   2020-12-11 00:00:00+01:00 21.75
   2020-12-12 00:00:00+01:00 21.75
   2020-12-13 00:00:00+01:00 21.75
   2020-12-14 00:00:00+01:00 22.25
   2020-12-15 00:00:00+01:00 22.25
   ...


Convert an OHLC list to a data frame
------------------------------------

Convert a :class:`OHLCList <energyquantified.data.OHLCList>` to a
``pandas.DataFrame`` like this:

   >>> latest_list.to_pandas_dataframe()
           traded   period  front    delivery   open   high    low  close  settlement  volume  open_interest
   0   2020-10-15      day      1  2020-10-16    NaN    NaN    NaN    NaN       23.24     0.0            0.0
   1   2020-10-15      day      2  2020-10-17    NaN    NaN    NaN    NaN       19.00     0.0            0.0
   2   2020-10-15      day      3  2020-10-18    NaN    NaN    NaN    NaN       16.00     0.0            0.0
   3   2020-10-15    month      1  2020-11-01  23.50  23.50  22.30  22.30       22.35   343.0        10104.0
   4   2020-10-15    month      2  2020-12-01  25.65  25.65  24.40  24.40       24.40    68.0         9772.0
   5   2020-10-15    month      3  2021-01-01    NaN    NaN    NaN    NaN       28.65     0.0          192.0
   ...

Convert a :class:`OHLCList <energyquantified.data.OHLCList>` to a
``polars.DataFrame`` like this:

   >>> latest_list.to_polars_dataframe()
   shape: (37, 11)
   ┌────────────┬────────┬───────┬────────────┬──────┬──────┬──────┬───────┬────────────┬────────┬───────────────┐
   │ traded     ┆ period ┆ front ┆ delivery   ┆ open ┆ high ┆ low  ┆ close ┆ settlement ┆ volume ┆ open_interest │
   │ ---        ┆ ---    ┆ ---   ┆ ---        ┆ ---  ┆ ---  ┆ ---  ┆ ---   ┆ ---        ┆ ---    ┆ ---           │
   │ date       ┆ str    ┆ i32   ┆ date       ┆ f64  ┆ f64  ┆ f64  ┆ f64   ┆ f64        ┆ f64    ┆ f64           │
   ╞════════════╪════════╪═══════╪════════════╪══════╪══════╪══════╪═══════╪════════════╪════════╪═══════════════╡
   │ 2020-10-15 ┆ day    ┆ 1     ┆ 2020-10-16 ┆ null ┆ null ┆ null ┆ null  ┆ 23.24      ┆ 0.0    ┆ 0.0           │
   │ 2020-10-15 ┆ day    ┆ 2     ┆ 2020-10-17 ┆ null ┆ null ┆ null ┆ null  ┆ 19.0       ┆ 0.0    ┆ 0.0           │
   │ 2020-10-15 ┆ day    ┆ 3     ┆ 2020-10-18 ┆ null ┆ null ┆ null ┆ null  ┆ 16.0       ┆ 0.0    ┆ 0.0           │
   │ 2020-10-15 ┆ day    ┆ 4     ┆ 2020-10-19 ┆ null ┆ null ┆ null ┆ null  ┆ 20.0       ┆ 0.0    ┆ 0.0           │
   │ 2020-10-15 ┆ day    ┆ 5     ┆ 2020-10-20 ┆ null ┆ null ┆ null ┆ null  ┆ 20.0       ┆ 0.0    ┆ 0.0           │
   │ …          ┆ …      ┆ …     ┆ …          ┆ …    ┆ …    ┆ …    ┆ …     ┆ …          ┆ …      ┆ …             │
   │ 2020-10-15 ┆ year   ┆ 6     ┆ 2026-01-01 ┆ null ┆ null ┆ null ┆ null  ┆ 27.78      ┆ 0.0    ┆ 92.0          │
   │ 2020-10-15 ┆ year   ┆ 7     ┆ 2027-01-01 ┆ null ┆ null ┆ null ┆ null  ┆ 28.49      ┆ 0.0    ┆ 111.0         │
   │ 2020-10-15 ┆ year   ┆ 8     ┆ 2028-01-01 ┆ null ┆ null ┆ null ┆ null  ┆ 28.75      ┆ 0.0    ┆ 75.0          │
   │ 2020-10-15 ┆ year   ┆ 9     ┆ 2029-01-01 ┆ null ┆ null ┆ null ┆ null  ┆ 30.15      ┆ 0.0    ┆ 10.0          │
   │ 2020-10-15 ┆ year   ┆ 10    ┆ 2030-01-01 ┆ null ┆ null ┆ null ┆ null  ┆ 30.3       ┆ 0.0    ┆ 10.0          │
   └────────────┴────────┴───────┴────────────┴──────┴──────┴──────┴───────┴────────────┴────────┴───────────────┘

Load an OHLC field as a time series
-----------------------------------

Method references: :py:meth:`eq.ohlc.load_delivery_as_timeseries() <energyquantified.api.OhlcAPI.load_delivery_as_timeseries>`
and :py:meth:`eq.ohlc.load_front_as_timeseries() <energyquantified.api.OhlcAPI.load_front_as_timeseries>`

There are two additional methods in the OHLC API for loading a specific OHLC
field into a time series object.

.. _continuous-front:

For a continuous front contract
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To load the close price for a **continuous front contract**, specify all the
same parameters as you would do with the
:py:meth:`eq.ohlc.load() <energyquantified.api.OhlcAPI.load>`-method, and an
additional **field** parameter:

   >>> from energyquantified.metadata import OHLCField
   >>> timeseries = eq.ohlc.load_front_as_timeseries(
   >>>    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 10),
   >>>    period=ContractPeriod.MONTH,
   >>>    front=1,  # Front month
   >>>    field=OHLCField.CLOSE  # Load the closing price
   >>> )

The result is a time series in daily resolution. Energy Quantified's
time series always includes all days, so that you will end up with Saturdays
and Sundays in the result, but these will have empty values.

Notice that there is an additional ``contract`` field on the time series
object, describing the query used to load this data:

   >>> timeseries.curve
   <Curve: "NP Futures Power Base EUR/MWh Nasdaq OHLC", curve_type=OHLC, subscription=FREEMIUM>

   >>> timeseries.contract
   <ContinuousContract: period=MONTH, front=1, field=CLOSE>

   >>> timeseries.data
   [<Value: date=2020-01-02 00:00:00+01:00, value=34>,
    <Value: date=2020-01-03 00:00:00+01:00, value=34.4>,
    <Value: date=2020-01-04 00:00:00+01:00, value=None>,
    <Value: date=2020-01-05 00:00:00+01:00, value=None>,
    <Value: date=2020-01-06 00:00:00+01:00, value=32.1>,
    ...

.. _specific-contract:

For a specific contract
^^^^^^^^^^^^^^^^^^^^^^^

To load the close price for a **specific contract**, specify all the same
parameters as you would do with the
:py:meth:`eq.ohlc.load() <energyquantified.api.OhlcAPI.load>`-method, and an
additional **field** parameter:

   >>> from energyquantified.metadata import OHLCField
   >>> timeseries = eq.ohlc.load_delivery_as_timeseries(
   >>>    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 10),
   >>>    period=ContractPeriod.MONTH,
   >>>    delivery=date(2020, 6, 1),  # June contract
   >>>    field=OHLCField.CLOSE  # We want to load the CLOSE price
   >>> )

The result is a time series in daily resolution. Energy Quantified's
time series always includes all days, so that you will end up with Saturdays
and Sundays in the result, but these will have empty values.

Notice that there is an additional ``contract`` field on the time series
object, describing the query used to load this data:

   >>> timeseries.curve
   <Curve: "NP Futures Power Base EUR/MWh Nasdaq OHLC", curve_type=OHLC, subscription=FREEMIUM>

   >>> timeseries.contract
   <SpecificContract: period=MONTH, delivery=2020-06-01, field=CLOSE>

   >>> timeseries.data
   [<Value: date=2020-01-03 00:00:00+01:00, value=24.7>,
    <Value: date=2020-01-04 00:00:00+01:00, value=None>,
    <Value: date=2020-01-05 00:00:00+01:00, value=None>,
    <Value: date=2020-01-06 00:00:00+01:00, value=None>,
    <Value: date=2020-01-07 00:00:00+01:00, value=None>,

(Apparently, there wasn't any trades on the June contract for 6 and 7 January,
so there is no close price.)

Fill holes for dates without trading activity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the :ref:`continuous front contract<continuous-front>` example above, there
was no data on 4 Jan and 5 Jan because these dates falls on a weekend. In some
cases, you may want to have a time series without holes in the data. We have
added a parameter to solve this issue.

When you are loading OHLC data using
:py:meth:`eq.ohlc.load_delivery_as_timeseries() <energyquantified.api.OhlcAPI.load_delivery_as_timeseries>`
or
:py:meth:`eq.ohlc.load_front_as_timeseries() <energyquantified.api.OhlcAPI.load_front_as_timeseries>`,
, you can set a ``fill`` parameter. It allows you to fill these holes in,
for instance, weekends and other days without trading activity.

**Fill holes:**

Let's load the continuous front data from the example earlier, but where we
set the ``fill`` parameter to ``fill-holes``:

>>> from energyquantified.metadata import OHLCField
>>> timeseries = eq.ohlc.load_front_as_timeseries(
>>>    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
>>>    begin=date(2020, 1, 1),
>>>    end=date(2020, 1, 10),
>>>    period=ContractPeriod.MONTH,
>>>    front=1,  # Front month
>>>    field=OHLCField.CLOSE,
>>>    fill='fill-holes'  # Fills the holes!
>>> )

The response will have the latest available closing price set for 4 and 5 Jan:

>>> timeseries.data
[<Value: date=2020-01-02 00:00:00+01:00, value=34>,
 <Value: date=2020-01-03 00:00:00+01:00, value=34.4>,
 <Value: date=2020-01-04 00:00:00+01:00, value=34.4>,  # Filled value!
 <Value: date=2020-01-05 00:00:00+01:00, value=34.4>,  # Filled value!
 <Value: date=2020-01-06 00:00:00+01:00, value=32.1>,
 ...

**Forward fill:**

Another, more aggressive ``fill``-option doesn’t only fill the holes but
always fills the latest closing price forward.

That parameter value is ``forward-fill``.

Using the example from :ref:`specific contract<specific-contract>` above, where
we don't have any values on 4-7 Jan, we can use ``fill=forward-fill`` to set
these values to the latest available closing price we know:

>>> from energyquantified.metadata import OHLCField
>>> timeseries = eq.ohlc.load_delivery_as_timeseries(
>>>    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
>>>    begin=date(2020, 1, 1),
>>>    end=date(2020, 1, 10),
>>>    period=ContractPeriod.MONTH,
>>>    delivery=date(2020, 6, 1),
>>>    field=OHLCField.CLOSE,
>>>    fill='forward-fill'  # Always fill the closing price forward
>>> )

Even though there were no trades in the weekend 4-5 Jan, as well as on the
following workdays, Monday 6 Jan and Tuesday 7 Jan, we will now have the
closing price from Friday 3 Jan set on all these days:

>>> timeseries.data
[<Value: date=2020-01-03 00:00:00+01:00, value=24.7>,
 <Value: date=2020-01-04 00:00:00+01:00, value=24.7>,
 <Value: date=2020-01-05 00:00:00+01:00, value=24.7>,
 <Value: date=2020-01-06 00:00:00+01:00, value=24.7>,
 <Value: date=2020-01-07 00:00:00+01:00, value=24.7>,
 ...

Keep in mind that this option will forward-fill also dates into the future.
Use it with care.