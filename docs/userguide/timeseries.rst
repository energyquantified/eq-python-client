Time series
===========

This page shows how to load time series data. All examples below expects you
to have an initialized and authenticated instance of the client called ``eq``.

Operations described here are available under ``eq.timeseries.*``.

**Requirements:** Use these operations for curves with ``curve_type`` set
to any of the following:

 * ``TIMESERIES``
 * ``SCENARIO_TIMESERIES``

Load time series data
---------------------

Loading time series data is quite straight-forward. You need to specify three
parameters at minimum: **curve**, **begin** and **end**.

So, let's load data for a curve called ``DE Wind Power Production MWh/h 15min Actual``
from 1 January 2020 at 00:00 (inclusive) to 6 January 2020 at 00:00 (exclusive).

In the example below we specified the curve as a string. You can either supply
the **curve name** or you can supply a **Curve** object. The same goes
for the date parameters, where the allowed types are: **date**, **datetime**
or an *ISO-8601*-formatted **string**.

(Keep in mind that if you do not have a paid subscription on Energy Quantified, you
will only be able to load data 30 days back from *today*. So in that case you should
adjust the begin and end dates accordingly.)

   >>> from datetime import date
   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Actual',
   >>>    begin=date(2020, 1, 1),   # or begin='2020-01-01'
   >>>    end=date(2020, 1, 6)      # or end='2020-01-06'
   >>> )

The response is an :class:`energyquantified.data.Timeseries` instance:

   >>> timeseries.curve
   <Curve: "DE Wind Power Production MWh/h 15min Actual", curve_type=TIMESERIES>

   >>> timeseries.resolution
   <Resolution: frequency=PT15M, timezone=CET>

   >>> timeseries.begin()
   datetime.datetime(2020, 1, 1, 0, 0, tzinfo=<DstTzInfo 'CET' CET+1:00:00 STD>)

   >>> timeseries.end()
   datetime.datetime(2020, 1, 6, 0, 0, tzinfo=<DstTzInfo 'CET' CET+1:00:00 STD>)

   >>> timeseries.data
   [<Value: date=2020-01-01 00:00:00+01:00, value=6387>,
    <Value: date=2020-01-01 00:15:00+01:00, value=6383>,
    <Value: date=2020-01-01 00:30:00+01:00, value=6640>
    ...


Aggregation
^^^^^^^^^^^

Notice that the wind actual curve in the above examples is in a 15-minute
resolution. Energy Quantified do not a copy of that curve in hourly, daily
or any other resolution.

If you would like to get the data in, say, daily resolution, simply
supply an extra argument, ``frequency``, when loading the time series data:

   >>> from energyquantified.time import Frequency
   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Actual',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 6),
   >>>    frequency=Frequency.P1D  # daily resolution
   >>> )

   >>> timeseries.resolution
   <Resolution: frequency=P1D, timezone=CET>

   >>> timeseries.data
   [<Value: date=2020-01-01 00:00:00+01:00, value=8928.95>,
    <Value: date=2020-01-02 00:00:00+01:00, value=16302.95>,
    <Value: date=2020-01-03 00:00:00+01:00, value=32063.55>,
    <Value: date=2020-01-04 00:00:00+01:00, value=33299.36>,
    <Value: date=2020-01-05 00:00:00+01:00, value=13151.01>]

You can also decide the aggregation method. Let's load the maximum wind
production per day:

   >>> from energyquantified.time import Frequency
   >>> from energyquantified.metadata import Aggregation
   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Actual',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 6),
   >>>    frequency=Frequency.P1D,
   >>>    aggregation=Aggregation.MAX  # Max value per day
   >>> )

   >>> timeseries.data
   [<Value: date=2020-01-01 00:00:00+01:00, value=14038>,
    <Value: date=2020-01-02 00:00:00+01:00, value=24891>,
    <Value: date=2020-01-03 00:00:00+01:00, value=36153>,
    <Value: date=2020-01-04 00:00:00+01:00, value=40671>,
    <Value: date=2020-01-05 00:00:00+01:00, value=18274>]

There is also support for hourly filters, such as ``BASE`` and ``PEAK``. This
is how you can load the mean wind production during peak hours:

   >>> from energyquantified.time import Frequency
   >>> from energyquantified.metadata import Aggregation, Filter
   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Actual',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 6),
   >>>    frequency=Frequency.P1D,
   >>>    aggregation=Aggregation.AVERAGE,
   >>>    hour_filter=Filter.PEAK
   >>> )

   >>> timeseries.data
   [<Value: date=2020-01-01 00:00:00+01:00, value=8578.48>,
    <Value: date=2020-01-02 00:00:00+01:00, value=16344.17>,
    <Value: date=2020-01-03 00:00:00+01:00, value=33363.6>,
    <Value: date=2020-01-04 00:00:00+01:00, value=37637.12>,
    <Value: date=2020-01-05 00:00:00+01:00, value=11912.42>]

When you specify a weekly, monthly, quarterly or yearly frequency, the API
will automatically use futures peak (8-20 on workdays only) in the aggregation.

Load time series scenarios
--------------------------

Energy Quantified provides climate data, where we run the weather data for different
years through our models (as of this writing, the weather years 1980-2019).
Using the same method as above, ``eq.timeseries.load()``, we can load this data.

For scenario-based time series, the values in
``timeseries.data[]`` are slightly different: It will consist of
``ScenarioValue`` items instead of ``Value`` items.

These ``ScenarioValue`` items contain a **scenarios** attribute instead of
a **value**. The **scenarios** attribute is a tuple of the scenario values:

   >>> from energyquantified.time import Frequency
   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Climate',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 6),
   >>>    frequency=Frequency.P1D,
   >>> )

   >>> timeseries.data
   [<ScenariosValue: date=2020-01-01 00:00:00+01:00, scenarios=(18988.74, 41907.79, 7712.76, 21450.4, 41017.22, 22006.53, 12535.5, 21720.46, 29565.86, 6424.07, 1977.56, 28206.2, 29880.71, 7876.56, 19262.9, 33366.47, 15903.28, 8025.6, 14447.35, 11107.51, 12495.92, 29776.22, 27195.17, 16943.26, 12084.37, 19026.09, 11743.87, 39982.1, 4164.34, 4904.58, 11775.45, 27830.02, 26543.89, 27228.76, 23010.97, 25048.93, 8048.41, 20949.78, 32833.12, 36763.43)>,
    <ScenariosValue: date=2020-01-02 00:00:00+01:00, scenarios=(14084.11, 36558.41, 12050.44, 23045.63, 37403.62, 16366.81, 20389.57, 27540.21, 43248.82, 2857.44, 1323.8, 40489.66, 37816.43, 14020.06, 24317.02, 29949.58, 8307.4, 8963.91, 31400.21, 22819.79, 15685.59, 26084.74, 20688.21, 23337.25, 12612.22, 40286.53, 3514.48, 30465.93, 15903.16, 4044.47, 7726.84, 18038.68, 26574.65, 25633, 29554.52, 40121.31, 25454.32, 18422.81, 21586.78, 30514.11)>,
    ...

-----

Next steps
^^^^^^^^^^

Learn how to load
:doc:`time series instances <../userguide/instances>`,
:doc:`period-based series <../userguide/periods>`, and
:doc:`period-based series instances <../userguide/period-instances>`.