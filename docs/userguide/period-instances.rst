Period-based instances
======================

This page shows how to load period-based series instances. All examples below
expects you to have an initialized instance of the client called ``eq``.

Operations described here are available under ``eq.period_instances.*``.

**Requirements:** Use these operations for curves with ``curve_type`` set
to any of the following:

 * ``INSTANCE_PERIOD``

.. important::

    We recommend reading the section on
    :doc:`period-based series <../userguide/periods>`
    before continuing, as all operations here return
    period-based series or lists of period-based series.


A note on REMIT data
--------------------

We generate new instances when new outage messages arrive. The series' start
on 1 January 2019 and goes up to 5 years into the future.

So the instance's issue date will be the same as the issue date
for the latest outage message and the tag will be the outage
message ID.

All REMIT curves for powerplants and aggregated production capacity are
period-based series instances.

(Exchange capacities reported via REMIT are stored as
:class:`Timeseries <energyquantified.data.Timeseries>`.)


Get the latest instance
-----------------------

Method reference: :py:meth:`eq.period_instances.latest() <energyquantified.api.PeriodInstancesAPI.latest>`

Load the latest instance like shown below. **curve**, **begin** and
**end** are required parameters:

   >>> from datetime import date
   >>> periodseries = eq.period_instances.latest(
   >>>    'DE Nuclear Capacity Available MW REMIT',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 6, 1)
   >>> )

   >>> periodseries
   <Periodseries: resolution=<Resolution: frequency=NONE, timezone=CET>, curve="DE Nuclear Capacity Available MW REMIT", instance=<Instance: issued="2020-07-16 05:20:00+00:00", tag="pgQCAPKo09HUBl9szRWmkA">, begin="2020-01-01 00:00:00+01:00", end="2020-06-01 00:00:00+02:00">

If you would like to know what the nuclear capacity in Germany was on, say,
1 April 2020 at 12:00, provide the **issued_at_latest** parameter:

   >>> from datetime import date, datetime
   >>> periodseries = eq.period_instances.latest(
   >>>    'DE Nuclear Capacity Available MW REMIT',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 6, 1),
   >>>    issued_at_latest=datetime(2020, 4, 1, 12, 0, 0) # 1 April at 12:00
   >>> )

As you can see, the latest message for 1 April 2020 at 12:00 was published on 30
March at 12:54 CEST. Here we print the instance only for clarity:

   >>> periodseries.instance
   <Instance: issued="2020-03-30 10:54:51+00:00", tag="GGXXxM8VKmeHWrbHHx3rAg">


Get a specific instance
-----------------------

Method reference: :py:meth:`eq.period_instances.get() <energyquantified.api.PeriodInstancesAPI.get>`

If you know the **issue date** and **tag** for an instance, you can load
it like seen below. You must always specify the issue date, but you can
leave the tag unspecified (which will default to a blank tag; this requires
the instance's tag to be blank).

Remember that **begin** and **end** are required.

Here we are loading the same instance as shown in the previous section, namely
an instance for the REMIT message published on 30 March 2020 at 12:54 CEST:

   >>> from datetime import date
   >>> from energyquantified.time import get_datetime, UTC
   >>> periodseries = eq.period_instances.get(
   >>>    'DE Nuclear Capacity Available MW REMIT',
   >>>    issued=get_datetime(2020, 3, 30, 10, 54, 51, tz=UTC),
   >>>    tag='GGXXxM8VKmeHWrbHHx3rAg',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 6, 1)
   >>> )

   >>> periodseries.instance
   <Instance: issued="2020-03-30 10:54:51+00:00", tag="GGXXxM8VKmeHWrbHHx3rAg">


Load instances
--------------

Method reference: :py:meth:`eq.period_instances.load() <energyquantified.api.PeriodInstancesAPI.load>`

To load multiple period-based series instances, you need to specify the
**curve**, **begin** and **end**.

To load the latest three updates for nuclear capacity in Germany, you can
do something like this:

   >>> from datetime import date
   >>> periodseries_list = eq.period_instances.load(
   >>>    'DE Nuclear Capacity Available MW REMIT',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 6, 1)
   >>> )

   >>> periodseries_list
   [<Periodseries: resolution=<Resolution: frequency=NONE, timezone=CET>, curve="DE Nuclear Capacity Available MW REMIT", instance=<Instance: issued="2020-07-16 05:20:00+00:00", tag="pgQCAPKo09HUBl9szRWmkA">, begin="2020-01-01 00:00:00+01:00", end="2020-06-01 00:00:00+02:00">,
    <Periodseries: resolution=<Resolution: frequency=NONE, timezone=CET>, curve="DE Nuclear Capacity Available MW REMIT", instance=<Instance: issued="2020-07-15 07:30:54+00:00", tag="FKqarmJMZUBbe-VcFtYczA">, begin="2020-01-01 00:00:00+01:00", end="2020-06-01 00:00:00+02:00">,
    <Periodseries: resolution=<Resolution: frequency=NONE, timezone=CET>, curve="DE Nuclear Capacity Available MW REMIT", instance=<Instance: issued="2020-07-13 19:07:48+00:00", tag="fj6UVXudDMsgXhzVIxWuFQ">, begin="2020-01-01 00:00:00+01:00", end="2020-06-01 00:00:00+02:00">]

The return type from ``load()`` is a
:py:class:`~energyquantified.data.PeriodseriesList`. This is a subclass of Python's
built-in list with two helpful methods:

 * :py:meth:`~energyquantified.data.PeriodseriesList.to_timeseries` converts
   the list of :py:meth:`~energyquantified.data.Periodseries` to a
   :py:class:`~energyquantified.data.TimeseriesList` of
   :py:class:`~energyquantified.data.Timeseries`. It requires you to specify a
   **frequency** for the output time series.

 * :py:meth:`~energyquantified.data.PeriodseriesList.to_dataframe` converts the
   list of period-bsed series to a ``pandas.DataFrame``. Like the
   :py:meth:`~energyquantified.data.PeriodseriesList.to_timeseries` method
   above, it also requires you to specify a **frequency** for the time series in
   the output data frame.

Like with the ``load()`` method for time series instances, specify
**issued_at_latest**, **issued_at_earliest**, **tags** and **exclude_tags**
for further filtering. You can also set **limit** to limit the number of
returned instances.

Here we load the 10 instances from the very end of 2019:

   >>> from datetime import date, datetime
   >>> periodseries_list = eq.period_instances.load(
   >>>    'DE Nuclear Capacity Available MW REMIT',
   >>>    begin=date(2020, 1, 1),
   >>>    end=date(2020, 6, 1),
   >>>    issued_at_latest=datetime(2019, 12, 31, 23, 59, 59),
   >>>    limit=10  # Maximum number of instances
   >>> )

   >>> [p.instance for p in periodseries_list]
   [<Instance: issued="2019-12-23 14:05:48+00:00", tag="-qMu2U9NbWUz_EgHi6wRfA">,
    <Instance: issued="2019-12-22 02:39:53+00:00", tag="hi3biDstbdT4Gc9S-CBn9w">,
    <Instance: issued="2019-12-17 18:56:28+00:00", tag="qssw2izWQJtX3nmK7Zp4dg">,
    <Instance: issued="2019-12-13 00:42:15+00:00", tag="Sb01f_roj0IybuFdAJs7bA">,
    <Instance: issued="2019-12-12 21:51:57+00:00", tag="Sb01f_roj0IybuFdAJs7bA">,
    <Instance: issued="2019-12-11 09:08:55+00:00", tag="moIJ7ETPUPA04Zf3lPPaJQ">,
    <Instance: issued="2019-12-05 14:42:59+00:00", tag="3_eYOl5o6bqBC4IwNSlYPg">,
    <Instance: issued="2019-12-04 21:43:04+00:00", tag="3_eYOl5o6bqBC4IwNSlYPg">,
    <Instance: issued="2019-12-04 08:53:52+00:00", tag="c73EjiRNVVAkOwqN8l6aAg">,
    <Instance: issued="2019-12-01 09:43:58+00:00", tag="Ah-SewfIguFLydohq0efvQ">]


List instances
^^^^^^^^^^^^^^

Method reference: :py:meth:`eq.period_instances.list() <energyquantified.api.PeriodInstancesAPI.list>`

Similar to the ``load()``-method, but this method only lists the *instances*
instead of loading the period-based series with data:

   >>> eq.period_instances.list(
   >>>    'DE Nuclear Capacity Available MW REMIT',
   >>>    issued_at_latest=datetime(2019, 12, 31, 23, 59, 59),
   >>>    limit=10  # Maximum number of instances
   >>> )
   [<Instance: issued="2019-12-23 14:05:48+00:00", tag="-qMu2U9NbWUz_EgHi6wRfA">,
    <Instance: issued="2019-12-22 02:39:53+00:00", tag="hi3biDstbdT4Gc9S-CBn9w">,
    <Instance: issued="2019-12-17 18:56:28+00:00", tag="qssw2izWQJtX3nmK7Zp4dg">,
    <Instance: issued="2019-12-13 00:42:15+00:00", tag="Sb01f_roj0IybuFdAJs7bA">,
    <Instance: issued="2019-12-12 21:51:57+00:00", tag="Sb01f_roj0IybuFdAJs7bA">,
    <Instance: issued="2019-12-11 09:08:55+00:00", tag="moIJ7ETPUPA04Zf3lPPaJQ">,
    <Instance: issued="2019-12-05 14:42:59+00:00", tag="3_eYOl5o6bqBC4IwNSlYPg">,
    <Instance: issued="2019-12-04 21:43:04+00:00", tag="3_eYOl5o6bqBC4IwNSlYPg">,
    <Instance: issued="2019-12-04 08:53:52+00:00", tag="c73EjiRNVVAkOwqN8l6aAg">,
    <Instance: issued="2019-12-01 09:43:58+00:00", tag="Ah-SewfIguFLydohq0efvQ">]


-----

Next steps
^^^^^^^^^^

Learn how to load
:doc:`time series <../userguide/timeseries>`,
:doc:`time series instances <../userguide/instances>`, and
:doc:`period-based series <../userguide/periods>`.