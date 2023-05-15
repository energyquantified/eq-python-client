Time series
===========

This page shows how to load time series data. All examples below expects you
to have an initialized instance of the client called ``eq``.

Operations described here are available under ``eq.timeseries.*``.

**Requirements:** Use these operations for curves with ``curve_type`` set
to any of the following:

 * ``TIMESERIES``
 * ``SCENARIO_TIMESERIES``

Load time series data
---------------------

Method reference: :py:meth:`eq.timeseries.load() <energyquantified.api.TimeseriesAPI.load>`

Loading time series data is quite straight-forward. You must at least specify
these three parameters: **curve**, **begin** and **end**.

So, let's load data for a curve called ``DE Wind Power Production MWh/h 15min Actual``
from 1 January 2020 at 00:00 (inclusive) to 6 January 2020 at 00:00 (exclusive).

In the example below, we specified the curve as a string. You can either supply
the **curve name** or a **Curve** object. The same goes for the date parameters,
where the allowed types are: **date**, **datetime** or an *ISO-8601*-formatted
**string**.

(Keep in mind that if you do not have a paid subscription on Energy Quantified,
you will only be able to load data 30 days back from *today*. So, in that case,
you should adjust the begin and end dates accordingly.)

   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Actual',
   >>>    begin='2020-01-01',
   >>>    end='2020-01-06',
   >>>    frequency='P1D'
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

Timezone conversion
^^^^^^^^^^^^^^^^^^^^

Use the ``time_zone`` parameter to convert the data to the given timezone:

   >>> from energyquantified.time import UTC
   >>>
   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Actual',
   >>>    begin='2020-01-01',
   >>>    end='2020-01-06',
   >>>    time_zone=UTC
   >>> )

**Note:** Only the following timezones are supported because these are the most
commonly used timezones. Most power markets in Europe operate in CET due to
standardization and market coupling.

- ``UTC`` – Coordinated Universal Time
- ``WET`` – Western European Time
- ``CET`` – Central European Time
- ``EET`` – Eastern European Time
- ``Europe/Istanbul`` – Turkey Time
- ``Europe/Moscow`` – Russian/Moscow Time
- ``Europe/Gas_Day`` – (Non-standard timezone; not in the IANA timezone database)
  European Gas Day at UTC-0500 (UTC-0400 during Daylight Saving Time). Starts
  at 06:00 in CE(S)T time. Used for the natural gas market in the European
  Union.

We use the `pytz <https://pypi.org/project/pytz/>`_ library for timezones.

Unit conversion
^^^^^^^^^^^^^^^

You can convert data to another unit. Add the desired unit as parameter to the
request and the date will be converted to the given unit before it's sent back to you.

Supported units at this moment:

- `°C` for temperatures in celsius degrees
- `Degrees` for angles in degrees
- `hPa` for pressure in hectopascal
- `m` for length in meters
- `m^2` for area in square meters
- `m^3` for volume in cubic meters
- `s` for time in seconds
- `t` for weight in tons
- `TW`, `GW`, `MW`, `kW`, `W` for power in watt
- `TWh`, `GWh`, `MWh`, `kWh`, `Wh` for energy in watt-hours
- `TWh/h`, `GWh/h`, `MWh/h`, `kWh/h`, `Wh/h` for average energy in watt-hours per hour
- `therm` for heat energy in therms
- `bbl` for volume in barrels
- `%` as percent
- `EUR`, `USD`, `GBP`, `NOK`, `SEK`, `DKK`, `CHF`, `CZK`, `HUF`, `PLN`, `BGN`, `HRK`, `RUB`, `RON`, `TRY`, `pence` for currencies

**Note:** Currency conversions are not supported for timeseries with a frequency higher than P1D.

Add the parameter to the request:

   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Actual',
   >>>    begin='2020-01-01',
   >>>    end='2020-01-06',
   >>>    frequency='P1D',
   >>>    unit='GWh/h'
   >>> )

The response data is converted:

   >>> timeseries.data
   [<Value: date=2020-01-01 00:00:00+01:00, value=6.39>,
    <Value: date=2020-01-01 00:15:00+01:00, value=6.38>,
    <Value: date=2020-01-01 00:30:00+01:00, value=6.64>
    ...

Aggregation
^^^^^^^^^^^

Notice that the actual wind curve in the above examples is in a 15-minute
resolution. Energy Quantified does not provide a copy of this curve in hourly,
daily or any other resolution.

If you would like to get the data in, say, daily resolution, supply an
extra argument, ``frequency``, when loading the time series data:

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

You can also decide on the aggregation method. Let's load the maximum wind
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

There is also support for hourly filters, such as ``BASE`` and ``PEAK``. So,
to load the daily *mean* wind production during *peak hours*, you can do like
so:

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

Aggregation threshold
~~~~~~~~~~~~~~~~~~~~~

In case, one or more input values are empty, the aggregation will return an
empty value. To avoid this, you can set the ``threshold`` parameter which
defines how many values are allowed to be missing within a frame of the
converted frequency. If the number of missing values is less than or equal to
the ``threshold``, aggregation is performed on the remaining non-empty values.
Otherwise, an empty value is returned.

**Note**: By default, the threshold is set to zero. This means that an empty
input value will result in an empty output value.

For example, you want to convert hourly values to daily values using the mean
value. Let's assume that six values on 2020-01-02 are empty and three on
2020-01-04. Instead of getting empty values, you want to get the average if a
maximum of four values are missing within a day. In this case, set the
``threshold`` to four.

   >>> from energyquantified.time import Frequency
   >>> from energyquantified.metadata import Aggregation, Filter
   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Actual',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 6),
   >>>    frequency=Frequency.P1D,
   >>>    aggregation=Aggregation.AVERAGE,
   >>>    threshold=4
   >>> )

   >>> timeseries.data
   [<Value: date=2020-01-01 00:00:00+01:00, value=8578.48>,
    <Value: date=2020-01-02 00:00:00+01:00, value=None>,
    <Value: date=2020-01-03 00:00:00+01:00, value=33363.6>,
    <Value: date=2020-01-04 00:00:00+01:00, value=37637.12>,
    <Value: date=2020-01-05 00:00:00+01:00, value=11912.42>]

The value for 2020-01-02 is ``None`` because more than four input values were
empty. The value for 2020-01-04 is not empty because less than or equal four
values were empty.

Load time series scenarios
--------------------------

Energy Quantified provides climate data, where we run the weather data for
different years through our models (as of this writing, the weather years
1980-2019).

By using the same method as above, ``eq.timeseries.load()``, we can load
this data.

For the scenario-based time series, the values in
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

Convert to pandas
-----------------

(This section contains a short description on how to convert a time series to a
``pandas.DataFrame``. See the chapter on :doc:`Pandas integration <pandas>`
for a detailed explanation.)

Convert :py:class:`~energyquantified.data.Timeseries` objects to pandas by
calling on :py:meth:`~energyquantified.data.Timeseries.to_dataframe`:

   >>> from datetime import date
   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Actual',
   >>>    begin=date(2020, 1, 1),   # or begin='2020-01-01'
   >>>    end=date(2020, 1, 6)      # or end='2020-01-06'
   >>> )

   >>> timeseries.to_dataframe()
   <BLANKLINE>
                             DE Wind Power Production MWh/h 15min Actual
   <BLANKLINE>
   <BLANKLINE>
   date
   2020-01-01 00:00:00+01:00                                        6387
   2020-01-01 00:15:00+01:00                                        6383
   2020-01-01 00:30:00+01:00                                        6640
   2020-01-01 00:45:00+01:00                                        6882
   2020-01-01 01:00:00+01:00                                        6945
   ...                                                               ...
   2020-01-05 22:45:00+01:00                                       17810
   2020-01-05 23:00:00+01:00                                       17814
   2020-01-05 23:15:00+01:00                                       17741
   2020-01-05 23:30:00+01:00                                       17878
   2020-01-05 23:45:00+01:00                                       18086
   <BLANKLINE>
   [480 rows x 1 columns]

You can also convert a scenario-based :py:class:`~energyquantified.data.Timeseries`
the same way. Notice that the data frame is quite wide (one column for each of the
40 weather years).

   >>> from energyquantified.time import Frequency
   >>> timeseries = eq.timeseries.load(
   >>>    'DE Wind Power Production MWh/h 15min Climate',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 1, 6),
   >>>    frequency=Frequency.P1D,
   >>> )

   >>> timeseries.to_dataframe()
                             DE Wind Power Production MWh/h 15min Climate                                                              ...
                                                                                                                                       ...
                                                                    y1980     y1981     y1982     y1983     y1984     y1985     y1986  ...     y2013     y2014     y2015     y2016     y2017     y2018     y2019
   date                                                                                                                                ...
   2020-01-01 00:00:00+01:00                                     18988.74  41907.79   7712.76  21450.40  41017.22  22006.53  12535.50  ...  27228.76  23010.97  25048.93   8048.41  20949.78  32833.12  36763.43
   2020-01-02 00:00:00+01:00                                     14084.11  36558.41  12050.44  23045.63  37403.62  16366.81  20389.57  ...  25633.00  29554.52  40121.31  25454.32  18422.81  21586.78  30514.11
   2020-01-03 00:00:00+01:00                                      7873.27  43711.02  32098.95  27374.06  41876.88  14908.12  16926.51  ...  34269.27  30967.48  32760.37  28027.87  34048.88  41116.13  12741.31
   2020-01-04 00:00:00+01:00                                     21656.69  29342.87  37587.62  37932.09  37568.10  23106.95  14855.93  ...  31147.11  26070.96  29673.18  22516.77  38706.61  28198.13  23159.46
   2020-01-05 00:00:00+01:00                                     11519.42  25586.94  28376.84  27198.14  25825.25  14052.56  17758.41  ...  15360.48  19578.57  17022.69  17374.12  15594.41  24443.66  26612.74
   <BLANKLINE>
   [5 rows x 40 columns]

-----

Next steps
----------

Learn how to load
:doc:`time series instances <../userguide/instances>`,
:doc:`period-based series <../userguide/periods>`, and
:doc:`period-based series instances <../userguide/period-instances>`.

Also see the chapter on :doc:`pandas integration <../userguide/pandas>`.