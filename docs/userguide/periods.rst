Period-based series
===================

This page shows how to load period-based series'. All examples below
expects you to have an initialized instance of the client called ``eq``.

Operations described here are available under ``eq.periods.*``.

**Requirements:** Use these operations for curves with ``curve_type`` set
to any of the following:

 * ``PERIOD``


Load series
-----------

Method reference: :py:meth:`eq.periods.load() <energyquantified.api.PeriodsAPI.load>`

Loading data for a period-based series is quite straight-forward. There are
three parameters you can and must specify: **curve**, **begin** and **end**.

Let's load the installed wind power capacity for Germany:

   >>> from datetime import date
   >>> periodseries = eq.periods.load(
   >>>    'DE Wind Power Installed MW Capacity',
   >>>    begin=date(2020, 1, 1),  # or begin='2020-01-01'
   >>>    end=date(2020, 6, 1)     # or end='2020-06-01'
   >>> )

The response is a :class:`Periodseries <energyquantified.data.Periodseries>`.
These are not regular time series', but more like lists of variable-length
intervals ("periods"). They are a much more compact way of storing and
representing data that mostly remain the same, but changes sporadically
– such as capacities.

   >>> periodseries
   <Periodseries: resolution=<Resolution: frequency=NONE, timezone=CET>, curve="DE Wind Power Installed MW Capacity", begin="2020-01-01 00:00:00+01:00", end="2020-01-06 00:00:00+01:00">

   >>> periodseries.data[:3]
   [<Period: begin=2020-01-01 00:00:00+01:00, end=2020-01-06 00:00:00+01:00, value=60645.29>,
    <Period: begin=2020-01-06 00:00:00+01:00, end=2020-01-13 00:00:00+01:00, value=60686.44>,
    <Period: begin=2020-01-13 00:00:00+01:00, end=2020-01-20 00:00:00+01:00, value=60832.02>]

Use the ``time_zone`` parameter to convert the data to the given timezone:

   >>> from energyquantified.time import UTC
   >>>
   >>> periodseries = eq.periods.load(
   >>>    'DE Wind Power Installed MW Capacity',
   >>>    begin=date(2020, 1, 1),  # or begin='2020-01-01'
   >>>    end=date(2020, 6, 1),    # or end='2020-06-01'
   >>>    time_zone=UTC
   >>> )

Don't worry if you do not know how to work with this data structure – it is
easy to convert period-based series to time series.

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

**Note:** Currency conversions are not supported for periods.

Add the unit as parameter:

   >>> from datetime import date
   >>> periodseries = eq.periods.load(
   >>>    'DE Wind Power Installed MW Capacity',
   >>>    begin=date(2020, 1, 1),  # or begin='2020-01-01'
   >>>    end=date(2020, 6, 1),     # or end='2020-06-01'
   >>>    unit='GW'
   >>> )

The response data is converted to `GW`, and the unit is found at the ``unit``
attribute of the series:

   >>> periodseries.data[:3]
   [<Period: begin=2020-01-01 00:00:00+01:00, end=2020-01-06 00:00:00+01:00, value=60.65.>,
    <Period: begin=2020-01-06 00:00:00+01:00, end=2020-01-13 00:00:00+01:00, value=60.69>,
    <Period: begin=2020-01-13 00:00:00+01:00, end=2020-01-20 00:00:00+01:00, value=60.83>]
    ...

   >>> str(periodseries)
   <Periodseries:
      resolution=<Resolution: frequency=NONE, timezone=CET>,
      curve="DE Wind Power Installed MW Capacity",
      begin="2020-01-01 00:00:00+02:00",
      end="2023-06-01 00:00:00+02:00",
      unit="GW">

Convert periods to a time series
--------------------------------

Method reference: :py:meth:`Periodseries.to_timeseries() <energyquantified.data.Periodseries.to_timeseries>`

While storing and transferring capacities is much more efficient as periods,
ultimately you would like to convert them to time series in a fixed interval
when doing data analysis.

To convert a period series to a time series, use the ``to_timeseries()``-method
and supply your preferred frequency. Below is an example where we convert the
wind power capacity loaded earlier into a time series in monthly resolution.

If multiple periods are overlapping the same month, the resulting value is
a weighted average of those.

    >>> from energyquantified.time import Frequency
    >>> timeseries = periodseries.to_timeseries(Frequency.P1M)
    >>> timeseries
    <Timeseries: resolution=<Resolution: frequency=P1M, timezone=CET>, curve="DE Wind Power Installed MW Capacity", begin="2020-01-01 00:00:00+01:00", end="2020-05-01 00:00:00+02:00">

    >>> timeseries.print()
    Timeseries:
      Curve: <Curve: "DE Wind Power Installed MW Capacity", curve_type=PERIOD, subscription=FREEMIUM>
      Resolution: <Resolution: frequency=P1M, timezone=CET>
    <BLANKLINE>
    2020-01-01 00:00:00+01:00            60784.71
    2020-02-01 00:00:00+01:00            61005.94
    2020-03-01 00:00:00+01:00            61220.22
    2020-04-01 00:00:00+02:00            61345.18

When converting from a period series to a time series, the timezone will
always remain the same.


-----

Next steps
----------

Learn how to load
:doc:`time series <../userguide/timeseries>`,
:doc:`time series instances <../userguide/instances>`, and
:doc:`period-based series instances <../userguide/period-instances>`.
