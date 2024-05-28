Instances
=========

This page shows how to load instances of time series. All examples below
expects you to have an initialized instance of the client called ``eq``.

Operations described here are available under ``eq.instances.*``.

**Requirements:** Use these operations for curves with ``curve_type`` set
to any of the following:

 * ``INSTANCE``


Load instances
--------------

Method reference: :py:meth:`eq.instances.load() <energyquantified.api.InstancesAPI.load>`

To load multiple instances (typically forecasts), you only need to specify
the **curve**. By default, it will load 5 instances, but you can increase
(or decrease) this by specifying a ``limit`` option. You can also filter
by **issue date** and **tags**.

Let's start by loading the latest instances for the German wind power forecasts:

   >>> forecasts = eq.instances.load(
   >>>    'DE Wind Power Production MWh/h 15min Forecast'
   >>> )

   >>> forecasts
   [<Timeseries: resolution=<Resolution: frequency=PT15M, timezone=CET>, curve="DE Wind Power Production MWh/h 15min Forecast", instance=<Instance: issued="2020-06-25 12:00:00+00:00", tag="gfs-ens">, begin="2020-06-25 14:00:00+02:00", end="2020-07-11 14:00:00+02:00">,
    <Timeseries: resolution=<Resolution: frequency=PT15M, timezone=CET>, curve="DE Wind Power Production MWh/h 15min Forecast", instance=<Instance: issued="2020-06-25 12:00:00+00:00", tag="gfs">, begin="2020-06-25 14:00:00+02:00", end="2020-07-05 14:00:00+02:00">,
    <Timeseries: resolution=<Resolution: frequency=PT15M, timezone=CET>, curve="DE Wind Power Production MWh/h 15min Forecast", instance=<Instance: issued="2020-06-25 12:00:00+00:00", tag="ec-ens">, begin="2020-06-25 14:00:00+02:00", end="2020-07-10 14:00:00+02:00">,
    <Timeseries: resolution=<Resolution: frequency=PT15M, timezone=CET>, curve="DE Wind Power Production MWh/h 15min Forecast", instance=<Instance: issued="2020-06-25 12:00:00+00:00", tag="ec">, begin="2020-06-25 14:00:00+02:00", end="2020-07-05 14:00:00+02:00">,
    <Timeseries: resolution=<Resolution: frequency=PT15M, timezone=CET>, curve="DE Wind Power Production MWh/h 15min Forecast", instance=<Instance: issued="2020-06-25 06:00:00+00:00", tag="gfs-ens">, begin="2020-06-25 08:00:00+02:00", end="2020-07-11 08:00:00+02:00">]

The return type from ``load()`` is a
:py:class:`~energyquantified.data.TimeseriesList`. This is a subclass of Python's
built-in list. It has extra validations so that all time series in the list have
the same frequency (hourly, daily, etc.), and it has a method called
:py:meth:`~energyquantified.data.TimeseriesList.to_dataframe` which converts the
list of time series to a ``pandas.DataFrame``. See the chapter on
:doc:`Pandas integration <pandas>` for more details.

Notice that each time series in the list has an ``instance`` attribute (with
``issued`` (issue date) and ``tag``). This is what identifies the instances
(or forecasts, if you will):

   >>> [f.instance for f in forecasts]
   [<Instance: issued="2020-06-25 12:00:00+00:00", tag="gfs-ens">,
    <Instance: issued="2020-06-25 12:00:00+00:00", tag="gfs">,
    <Instance: issued="2020-06-25 12:00:00+00:00", tag="ec-ens">,
    <Instance: issued="2020-06-25 12:00:00+00:00", tag="ec">,
    <Instance: issued="2020-06-25 06:00:00+00:00", tag="gfs-ens">]


Energy Quantified has many years of forecasts in the database (non-paying
users only get access to instances from the latest 30 days). So, if you would
like to load older instances, you can do so! Here is how to load the last
instances issued in 2018:

   >>> from datetime import datetime
   >>> forecasts = eq.instances.load(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    issued_at_latest=datetime(2018, 12, 31, 23, 59, 59) # Last second of 2018!
   >>> )

Load only instances issued at a specific time of day by using the
``issued-time-of-day`` parameter. You can provide one or more time-values.

   >>> from datetime import time
   >>> forecasts = eq.instances.load(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    issued_time_of_day=["12:00", time(3,0)] # Issued at 12:00 or 03:00
   >>> )

You can also filter by the instance's **tags** you would like to load. It is
possible to list more than one tag. Let's download data for ``ec`` and ``gfs``:

   >>> forecasts = eq.instances.load(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    tags=['ec', 'gfs']  # Can be a string, too: tags='ec'
   >>> )

Combine the parameters ``issued_at_latest`` and ``tags`` to load the instances
of your liking. There is also an ``exclude_tags`` to let you remove certain
tags from the response.

Use the ``time_zone`` parameter to convert the data to the given timezone:

   >>> from energyquantified.time import UTC
   >>>
   >>> forecasts = eq.instances.load(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    time_zone=UTC
   >>> )

And finally, you can aggregate instances:

   >>> from datetime import datetime
   >>> from energyquantified.time import Frequency
   >>> from energyquantified.metadata import Aggregation, Filter
   >>> forecasts = eq.instances.load(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    issued_at_latest=datetime(2020, 6, 1, 0, 0, 0),
   >>>    tags='ec',
   >>>    frequency=Frequency.P1D,
   >>>    aggregation=Aggregation.AVERAGE,
   >>>    hour_filter=Filter.BASE,
   >>>    threshold=7 # Aggregate days only if 7 or fewer quarters are missing
   >>>    limit=10
   >>> )


Get the latest instance
-----------------------

Method reference: :py:meth:`eq.instances.latest() <energyquantified.api.InstancesAPI.latest>`

You can load the latest instance available like so:

   >>> forecast = eq.instances.latest(
   >>>    'DE Wind Power Production MWh/h 15min Forecast'
   >>> )

   >>> forecast
   <Timeseries: resolution=<Resolution: frequency=PT15M, timezone=CET>, curve="DE Wind Power Production MWh/h 15min Forecast", instance=<Instance: issued="2020-06-25 18:00:00+00:00", tag="gfs">, begin="2020-06-25 20:00:00+02:00", end="2020-06-26 10:00:00+02:00">

As for the method to load multiple instances, you can put filters on which
instance you would like to load:

   >>> from datetime import datetime
   >>> forecast = eq.instances.latest(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    tags='ec',
   >>>    issued_at_latest=datetime(2020, 6, 1, 0, 0, 0)
   >>> )

Aggregations are supported here, too.


Get a specific instance
-----------------------

Method reference: :py:meth:`eq.instances.get() <energyquantified.api.InstancesAPI.get>`

If you know the **issue date** and **tag** for an instance, you can load
it like seen below. You must always specify the issue date, but you can
leave the tag unspecified (which will default to a blank tag).

   >>> from datetime import datetime
   >>> forecast = eq.instances.get(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    issued=datetime(2020, 6, 1, 0, 0, 0),
   >>>    tag='ec'
   >>> )

   >>> forecast.instance
   <Instance: issued="2020-06-01 00:00:00+00:00", tag="ec">

Aggregations are supported here, too.


Include ensembles
-----------------

All the above methods — ``load()``, ``latest()`` and ``get()`` — can also load
*scenarios* for instances that have these. For instance-based data, we refer to
*scenarios* as *ensembles*. The terminology comes from meteorology,
where forecasts with multiple scenarios are called *ensemble forecasts*.

To load ensembles, add ``ensembles=True`` in the parameters.

There is one catch: When loading ensembles, the maximum number of instances
you can load at once becomes reduced to 10 due to increased server-side load.

Instances that don't have ensembles will return a regular, single-valued
time series.

In the below example, we are loading the GFS ensemble forecast issued
1 June 2020 at 00:00. And aggregations are supported here, too:

   >>> from datetime import datetime
   >>> forecast = eq.instances.get(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    issued=datetime(2020, 6, 1, 0, 0, 0),
   >>>    tag='gfs-ens',  # GFS ensemble forecast
   >>>    frequency=Frequency.P1D,
   >>>    ensembles=True  # Include ensembles
   >>> )

   >>> forecast.data[:3]
   [<MeanScenariosValue: date=2020-06-02 00:00:00+02:00, value=4249.56, scenarios=(4230.24, 4200.12, 3958.99, 4803.86, 5132.65, 4467.72, 5137.52, 4272.63, 3883.69, 3667.21, 4463.02, 4183.24, 4166.79, 4374.41, 3916.84, 3866.79, 3837.91, 4055.36, 3977.33, 4376.41, 4267.8)>,
    <MeanScenariosValue: date=2020-06-03 00:00:00+02:00, value=5150.15, scenarios=(5438.17, 5270.41, 4628.31, 4947.27, 5635.71, 5177.4, 4583.76, 5898.94, 5563.79, 4547.67, 5143.17, 5709.71, 5038.66, 4519.17, 4647.19, 4686.25, 5193.25, 5323.04, 5720.27, 5247.36, 5233.52)>,
    <MeanScenariosValue: date=2020-06-04 00:00:00+02:00, value=12355.81, scenarios=(11182.13, 11389.47, 9822.78, 10551.62, 12745.04, 10715.13, 15139.99, 11685.89, 11184.46, 10147.47, 12218.74, 14013.28, 13878.11, 11320.92, 17547.07, 10672.34, 13702.91, 9896.63, 13989.7, 15525.05, 12143.3)>]


Relative queries (day-ahead forecasts)
--------------------------------------

Method reference: :py:meth:`eq.instances.relative() <energyquantified.api.InstancesAPI.relative>`

When benchmarking models (forecasts), one often would like to know what a
forecast was for the day ahead. And you would like to do this over a date
interval. For example, we would like to know Monday's forecast for Tuesday,
and Tuesday's forecast for Wednesday, and so on.

Energy Quantified's API has solved this by via an operation we call *relative
forecasts*.

The relative forecasts work for **0 or more days ahead**:

   - ``days_ahead=0`` means forecasts for intraday
   - ``days_ahead=1`` means forecasts for day ahead
   - ``days_ahead=2`` means forecasts for day after day ahead
   - `... and so on`

You *must* filter on the **tag**, and you *can* filter on the **time-of-day**
the forecast was issued. When there isn't any forecast issued for a specific
day, then that day will have no values.

   >>> from datetime import datetime, time
   >>> day_ahead_forecast = eq.instances.relative(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    begin=datetime(2020, 6, 1, 0, 0, 0),
   >>>    end=datetime(2020, 6, 5, 0, 0, 0),
   >>>    tag='ec',
   >>>    days_ahead=1,  # The day-ahead forecast (0 or higher allowed)
   >>>    time_of_day=time(0, 0),  # Issued at exactly 00:00
   >>>    frequency=Frequency.P1D
   >>> )

   >>> day_ahead_forecast.data
   [<Value: date=2020-06-01 00:00:00+02:00, value=10720.75>,
    <Value: date=2020-06-02 00:00:00+02:00, value=4144.67>,
    <Value: date=2020-06-03 00:00:00+02:00, value=6397.83>,
    <Value: date=2020-06-04 00:00:00+02:00, value=12686.8>]

If you don't know precisely when the forecast was issued, or you would like
only to get forecasts issued before a particular time of the day, use the
**before_time_of_day** instead. You can also decide whether to select the
*earliest* or *latest* issued instance by specifying the **issued** parameter.

There is also a parameter for **after_time_of_day**.

Here we select the *latest day ahead* wind power forecasts issued *before 12:00* every
day from 1 June to 5 June:

   >>> from datetime import datetime, time
   >>> day_ahead_forecast = eq.instances.relative(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    begin=datetime(2020, 6, 1, 0, 0, 0),
   >>>    end=datetime(2020, 6, 5, 0, 0, 0),
   >>>    tag='ec',
   >>>    days_ahead=1,
   >>>    before_time_of_day=time(12, 0),  # Issued before 12 o'clock
   >>>    issued='latest',   # Set to "earliest" or "latest"
   >>>    frequency=Frequency.P1D
   >>> )

   >>> day_ahead_forecast.data
   [<Value: date=2020-06-01 00:00:00+02:00, value=10720.75>,
    <Value: date=2020-06-02 00:00:00+02:00, value=4144.67>,
    <Value: date=2020-06-03 00:00:00+02:00, value=6397.83>,
    <Value: date=2020-06-04 00:00:00+02:00, value=12686.8>]

Aggregations are also supported, as you can see from the examples above.


Rolling forecasts (hours-ahead forecasts)
-----------------------------------------

Method reference: :py:meth:`eq.instances.rolling() <energyquantified.api.InstancesAPI.rolling>`

Rolling forecasts are time series where each value is from the latest instance
(forecast) created at least ``hours_ahead`` hours before.

If the time series from a rolling forecast with ``hours_ahead=2`` contains the
dates ``2023-10-01 05:15:00`` and ``2023-10-01 05:30:00``, then the values are
from the latest instance (forecast) created at or before ``2023-10-01 03:15:00``
and ``2023-10-01 03:30:00``, respectively.

The example below illustrates how to load a rolling forecast for wind power in
Germany from ``2023-10-01`` (inclusive) to ``2023-10-02`` (exclusive):

   >>> from datetime import datetime
   >>> rolling_forecast = eq.instances.rolling(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    begin=datetime(2023, 10, 1),
   >>>    end=datetime(2023, 10, 2),
   >>>    hours_ahead=2,
   >>> )

   >>> rolling_forecast.data
   [<Value: date=2023-10-01 00:00:00+02:00, value=7973.2>,
    <Value: date=2023-10-01 00:15:00+02:00, value=8049.1>,
    <Value: date=2023-10-01 00:30:00+02:00, value=8076.5>,
    ...,
    <Value: date=2023-10-01 23:15:00+02:00, value=9892>,
    <Value: date=2023-10-01 23:30:00+02:00, value=9878>,
    <Value: date=2023-10-01 23:45:00+02:00, value=9867.4>]

Specify the ``tags`` parameter to create a rolling forecast with values from
instances with a matching tag only. Similarly, filter out specific instances
with the ``exclude_tags`` parameter.

The following code snippet shows how to load the rolling forecast for
``DE Wind Power Production MWh/h 15min Forecast`` from ``2023-10-01``
(inclusive) to ``2023-10-02``, using values from instances with the ``ec`` or
``gfs`` tag. The result is filtered for ``PEAK``, aggregated from quarter-hourly
to hourly frequency, and unit converted from ``MWh/h`` to ``GWh/h``.

   >>> from datetime import datetime
   >>> from energyquantified.metadata import Filter
   >>> rolling_forecast = eq.instances.rolling(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    begin=datetime(2023, 10, 1),
   >>>    end=datetime(2023, 10, 2),
   >>>    hours_ahead=2,
   >>>    tags=['ec', 'gfs'],
   >>>    frequency=Frequency.PT1H,
   >>>    hour_filter=Filter.PEAK,
   >>>    unit="GWh/h",
   >>> )

   >>> rolling_forecast.data
   [<Value: date=2023-10-01 08:00:00+02:00, value=9.61>
    <Value: date=2023-10-01 09:00:00+02:00, value=10.6>
    <Value: date=2023-10-01 10:00:00+02:00, value=8.58>
    <Value: date=2023-10-01 11:00:00+02:00, value=9.47>
    <Value: date=2023-10-01 12:00:00+02:00, value=10.84>
    <Value: date=2023-10-01 13:00:00+02:00, value=12.65>
    <Value: date=2023-10-01 14:00:00+02:00, value=15.51>
    <Value: date=2023-10-01 15:00:00+02:00, value=14.49>
    <Value: date=2023-10-01 16:00:00+02:00, value=13.02>
    <Value: date=2023-10-01 17:00:00+02:00, value=11.84>
    <Value: date=2023-10-01 18:00:00+02:00, value=10.7>
    <Value: date=2023-10-01 19:00:00+02:00, value=10.24>]

Please see the full method reference for additional load options and further
information.


Absolute forecasts queries
--------------------------

Method reference: :py:meth:`eq.instances.absolute() <energyquantified.api.InstancesAPI.absolute>`

Load forecasted values from various instances for a specific point in time,
to see how forecasts develop over time.

The following parameters are required to load absolute forecasts:
 * ``curve``: The :py:class:`Curve <energyquantified.metadata.Curve>` to load
 * ``delivery``: The point in time to load forecasted values for
 * ``begin``: Earliest issued date for instances (inclusive)
 * ``end``: Latest issued date for instances (exclusive)

The example below loads the absolute forecast for
``DE Wind Power Production MWh/h 15min Forecast`` at 2023-10-05 12:00, from
instances issued between 2023-10-01 (inclusive) and 2023-10-02 (exclusive).

   >>> from datetime import datetime
   >>> absolute_result = eq.instances.absolute(
   >>>   "DE Wind Power Production MWh/h 15min Forecast",
   >>>   datetime(2023, 10, 5, 12), # Delivery 2023-10-05 12:00
   >>>   begin=datetime(2023, 10, 1), # Earliest issued (inclusive)
   >>>   end=datetime(2023, 10, 2), # Latest issued (exclusive)
   >>> )

   >>> print(absolute_result)
   <AbsoluteResult:
      curve="DE Wind Power Production MWh/h 15min Forecast",
      resolution=<Resolution: frequency=PT15M, timezone=CET>,
      delivery=2023-10-05 12:00:00+02:00,
      filters=BASE,
      aggregation=MEAN,
      unit=MWh/h,
      items=
         <AbsoluteItem:
            instance=<Instance:
               issued="2023-10-01 00:00:00+00:00",
               tag="icon">,
            value=33493.8>,
         <AbsoluteItem:
            instance=<Instance:
               issued="2023-10-01 00:00:00+00:00",
               tag="gfs">,
            value=35230.1>,
         <AbsoluteItem:
            instance=<Instance:
               issued="2023-10-01 00:00:00+00:00",
               tag="ec">,
            value=24395>,
         ...,
         <AbsoluteItem:
            instance=<Instance:
               issued="2023-10-01 18:00:00+00:00",
               tag="gfs-en
            ">, value=24648.8>,
         <AbsoluteItem:
            instance=<Instance:
               issued="2023-10-01 18:00:00+00:00",
               tag="gfs">,
            value=29499.2>,
         <AbsoluteItem:
            instance=<Instance:
               issued="2023-10-01 18:00:00+00:00",
               tag="ecsr">,
            value=26542.6>>

The resolution of the delivery defaults to the Curve's resolution. Change the
frequency or time zone of the delivery by supplying the ``frequency`` or
``time_zone`` parameters, respectively. Note that you cannot use a frequency
higher than the Curve's original frequency, and time zone conversion is
supported only for curves with higher than daily frequency (> P1D).

Load the absolute forecast with delivery in hourly frequency from instances with
the ``ec`` tag:

   >>> from datetime import datetime
   >>> from energyquantified.time import Frequency
   >>> absolute_result = eq.instances.absolute(
   >>>   "DE Wind Power Production MWh/h 15min Forecast",
   >>>   datetime(2023, 10, 5, 12), # Delivery 2023-10-05 12:00
   >>>   begin=datetime(2023, 10, 1), # Earliest issued (inclusive)
   >>>   end=datetime(2023, 10, 2), # Latest issued (exclusive)
   >>>   frequency=Frequency.PT1H,
   >>>   tags=["ec"]
   >>> )

   >>> print(absolute_result)
   <AbsoluteResult:
      curve="DE Wind Power Production MWh/h 15min Forecast",
     resolution=<Resolution: frequency=PT1H, timezone=CET>,
     delivery=2023-10-05 12:00:00+02:00,
     filters=BASE,
     aggregation=MEAN,
     unit=MWh/h,
     items=
        <AbsoluteItem:
         instance=<Instance:
            issued="2023-10-01 00:00:00+00:00",
            tag="ec">,
         value=23897.75>,
        <AbsoluteItem:
         instance=<Instance:
            issued="2023-10-01 12:00:00+00:00",
            tag="ec">,
         value=31124.48>>

Set zone of the delivery with the ``time_zone`` parameter:

   >>> from datetime import datetime
   >>> from energyquantified.time import Frequency, UTC
   >>> absolute_result = eq.instances.absolute(
   >>>   "DE Wind Power Production MWh/h 15min Forecast",
   >>>   datetime(2023, 10, 5, 12), # Delivery 2023-10-05 12:00
   >>>   begin=datetime(2023, 10, 1), # Earliest issued (inclusive)
   >>>   end=datetime(2023, 10, 2), # Latest issued (exclusive)
   >>>   frequency=Frequency.PT1H,
   >>>   time_zone=UTC,
   >>>   tags=["ec"]
   >>> )

   >>> print(absolute_result)
   <AbsoluteResult:
      curve="DE Wind Power Production MWh/h 15min Forecast",
     resolution=<Resolution: frequency=PT1H, timezone=UTC>,
     delivery=2023-10-05 12:00:00+00:00,
     filters=BASE,
     aggregation=MEAN,
     unit=MWh/h,
     items=
        <AbsoluteItem:
         instance=<Instance:
            issued="2023-10-01 00:00:00+00:00",
            tag="ec">,
         value=20479.78>,
        <AbsoluteItem:
         instance=<Instance:
            issued="2023-10-01 12:00:00+00:00",
            tag="ec">,
         value=29158.65>>

The :py:meth:`absolute() <energyquantified.api.InstancesAPI.absolute>` method
also supports filtering on specific hours (e.g., BASE/PEAK), unit conversion,
choosinghow to aggregate data when delivery frequency is lower than the Curve's,
and options to filter or exclude instances by tags.

The final example below illustrates and explains usage of all parameters
simultaneously:

   >>> from datetime import datetime
   >>> from energyquantified.metadata import Aggregation, Filter
   >>> from energyquantified.time import Frequency, UTC
   >>> absolute_result = eq.instances.absolute(
   >>>   "DE Wind Power Production MWh/h 15min Forecast",
   >>>   # Delivery 2023-10-05
   >>>   datetime(2023, 10, 5),
   >>>   # Earliest issued (inclusive) for instances to use
   >>>   begin=datetime(2023, 10, 1),
   >>>   # Latest issued (exclusive) for instances to use
   >>>   end=datetime(2023, 10, 2),
   >>>   # Frequency of the delivery
   >>>   frequency=Frequency.P1D,
   >>>   # Timezone of the delivery
   >>>   time_zone=UTC,
   >>>   # Exclude values not in PEAK when aggregating
   >>>   hour_filter=Filter.PEAK,
   >>>   # Convert the unit from 'MWh/h' to 'GWh/h'
   >>>   unit="GWh/h,
   >>>   # We load with a lower frequency (P1D < Curve's original
   >>>   # PT15M), so all of the PT15M values must be aggregated
   >>>   # into a single value representing the delivery. Aggregate
   >>>   # to AVERAGE (or MEAN).
   >>>   aggregation=Aggregation.AVERAGE,
   >>>   tags=["ec"], # Only include instances with tag 'ec'
   >>>   exclude_tags=["gfs"], # Exclude instance with tag 'gfs'
   >>> )

   >>> print(absolute_result)
   <AbsoluteResult:
      curve="DE Wind Power Production MWh/h 15min Forecast",
      resolution=<Resolution: frequency=P1D, timezone=UTC>,
      delivery=2023-10-05 00:00:00+00:00,
      filters=PEAK,
      aggregation=AVERAGE,
      unit=GWh/h,
      items=
         <AbsoluteItem:
            instance=<Instance:
               issued="2023-10-01 00:00:00+00:00",
               tag="ec">,
            value=16.81>,
         <AbsoluteItem:
            instance=<Instance:
               issued="2023-10-01 12:00:00+00:00",
               tag="ec">,
            value=23.1>>


List available instances and tags
---------------------------------

There are two utility methods available under ``eq.instances.*``:

Tags
^^^^

Method reference: :py:meth:`eq.instances.tags() <energyquantified.api.InstancesAPI.tags>`

List the unique tags that exist in instances for a curve. The response
is a Python set of the existing tags:

   >>> eq.instances.tags(
   >>>    'DE Wind Power Production MWh/h 15min Forecast'
   >>> )
   {'ec', 'ec-ens', 'ecsr', 'ecsr-ens', 'gfs', 'gfs-ens'}


List instances
^^^^^^^^^^^^^^

Method reference: :py:meth:`eq.instances.list() <energyquantified.api.InstancesAPI.list>`

Similar to the ``load()``-method, but this method only lists the *instances*
instead of loading the time series data:

   >>> eq.instances.list(
   >>>    'DE Wind Power Production MWh/h 15min Forecast',
   >>>    issued_at_latest='2020-05-01 00:00',
   >>>    tags='gfs',
   >>>    limit=10
   >>> )
   [<Instance: issued="2020-05-01 00:00:00+00:00", tag="gfs">,
    <Instance: issued="2020-04-30 18:00:00+00:00", tag="gfs">,
    <Instance: issued="2020-04-30 12:00:00+00:00", tag="gfs">,
    <Instance: issued="2020-04-30 06:00:00+00:00", tag="gfs">,
    <Instance: issued="2020-04-30 00:00:00+00:00", tag="gfs">,
    <Instance: issued="2020-04-29 18:00:00+00:00", tag="gfs">,
    <Instance: issued="2020-04-29 12:00:00+00:00", tag="gfs">,
    <Instance: issued="2020-04-29 06:00:00+00:00", tag="gfs">,
    <Instance: issued="2020-04-29 00:00:00+00:00", tag="gfs">,
    <Instance: issued="2020-04-28 18:00:00+00:00", tag="gfs">]


-----

Next steps
----------

Learn how to load
:doc:`time series <../userguide/timeseries>`,
:doc:`period-based series <../userguide/periods>`, and
:doc:`period-based series instances <../userguide/period-instances>`.