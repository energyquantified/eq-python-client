Period-based series
===================

This page shows how to load period-based series. All examples below
expects you to have an initialized and authenticated instance of the
client called ``eq``.

Operations described here are available under ``eq.periods.*``.

**Requirements:** Use these operations for curves with ``curve_type`` set
to any of the following:

 * ``PERIOD``


Load series
-----------

Loading data for a period-based series is quite straight-forward. There are
three parameters you can and must specify: **curve**, **begin** and **end**.

Let's load the installed wind power capacity for Germany:

   >>> from datetime import date
   >>> periodseries = eq.periods.load(
   >>>    'DE Wind Power Installed MW Capacity',
   >>>    begin=date(2020, 1, 1),  # or begin='2020-01-01'
   >>>    end=date(2020, 6, 1)     # or end='2020-06-01'
   >>> )

The response is an :class:`energyquantified.data.Periodseries` instance. These
are not normal time series, but more like lists of variable-length intervals
("periods"). This is a much more compact way of storing and
representing data that mostly have the same value – such as capacities.

Don't worry if you do not know how to work with this data structure – there
is a way to convert period-based series to time series.

   >>> periodseries
   <Periodseries: resolution=<Resolution: frequency=NONE, timezone=CET>, curve="DE Wind Power Installed MW Capacity", begin="2020-01-01 00:00:00+01:00", end="2020-01-06 00:00:00+01:00">

   >>> periodseries.data[:3]
   [<Period: begin=2020-01-01 00:00:00+01:00, end=2020-01-06 00:00:00+01:00, value=60645.29>,
    <Period: begin=2020-01-06 00:00:00+01:00, end=2020-01-13 00:00:00+01:00, value=60686.44>,
    <Period: begin=2020-01-13 00:00:00+01:00, end=2020-01-20 00:00:00+01:00, value=60832.02>]


Convert periods to a time series
--------------------------------

While storing and transferring capacities is much more efficient as periods,
ultimately you would like to convert them to time series in a fixed interval
when doing data analysis.

To convert a period series to a time series, use the ``to_timeseries()``-method
and supply your preferred frequency. Below is an example where the wind power
capacity loaded earlier is converted to a time series in monthy resolution.

If multiple periods are overlapping the same month, the resulting value is
a weighted average of those.

    >>> timeseries = periodseries.to_timeseries(Frequency.P1M)
    >>> timeseries
    <Timeseries: resolution=<Resolution: frequency=P1M, timezone=CET>, curve="DE Wind Power Installed MW Capacity", begin="2020-01-01 00:00:00+01:00", end="2020-05-01 00:00:00+02:00">

    >>> timeseries.print()
    Timeseries:
      Curve: <Curve: "DE Wind Power Installed MW Capacity", curve_type=PERIOD>
      Resolution: <Resolution: frequency=P1M, timezone=CET>
    <BLANKLINE>
    2020-01-01 00:00:00+01:00            60784.71
    2020-02-01 00:00:00+01:00            61005.94
    2020-03-01 00:00:00+01:00            61220.22
    2020-04-01 00:00:00+02:00            61345.18

When converting from a period series to a time series, the time-zone will
always remain the same.


-----

Read more
^^^^^^^^^

Learn how to load
:doc:`time series <../userguide/timeseries>`,
:doc:`time series instances <../userguide/instances>`, and
:doc:`period-based series instances <../userguide/period-instances>`.
