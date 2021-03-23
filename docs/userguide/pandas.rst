Pandas integration
==================

This page describes the `pandas <https://pandas.pydata.org>`_ integration
of Energy Quantified's Python client. We chose to integrate with pandas because
it is quite popular and it works great with time series data. For full
documentation on **pandas**, refer to their
`documentation <https://pandas.pydata.org/docs/>`_.

Pandas is **not required** to use the ``energyquantified`` package. You must
therefore **install pandas** separately to use the following operations.


Convert data series to data frames
----------------------------------

You can convert any of these types to a ``pandas.DataFrame``:

 * :py:class:`~energyquantified.data.Timeseries`
 * :py:class:`~energyquantified.data.Periodseries`
 * :py:class:`~energyquantified.data.OHLCList`

They all have a method called ``to_dataframe()``. ``Periodseries`` differs from
the two others in which you must supply a **frequency** parameter.

There also exists an alias of ``to_dataframe()`` called ``to_df()``. The term
``df`` is a commonly used shorthand and variable name for ``DataFrame``'s.

Convert time series
^^^^^^^^^^^^^^^^^^^

Converting a time series is simple:

   >>> df = timeseries.to_dataframe()
   >>> df
                             DE Wind Power Production MWh/h 15min Actual
   <BLANKLINE>
   <BLANKLINE>
   date
   2020-01-01 00:00:00+01:00                                     8928.95
   2020-01-02 00:00:00+01:00                                    16302.95
   2020-01-03 00:00:00+01:00                                    32063.55
   2020-01-04 00:00:00+01:00                                    33299.36
   2020-01-05 00:00:00+01:00                                    13151.01

You can also set a custom name if you think the default one is a little
too verbose:

   >>> df = timeseries.to_dataframe(name='de wind')
   >>> df
                               de wind
   <BLANKLINE>
   <BLANKLINE>
   date
   2020-01-01 00:00:00+01:00   8928.95
   2020-01-02 00:00:00+01:00  16302.95
   2020-01-03 00:00:00+01:00  32063.55
   2020-01-04 00:00:00+01:00  33299.36
   2020-01-05 00:00:00+01:00  13151.01

If you have a scenario-based time series (such as a time series loaded for
an ensemble forecast), you will get one column per ensemble.

Notice that there are **three column headers** here. The first is the
**curve**, the second is the **instance**, and the third is the **scenarios**.
You can read more on this in the :ref:`column headers section<column-headers>`
below. It is also possible to merge these three header levels onto one, see
the section on :ref:`single-level column headers<single-column-headers>` for
details.

   >>> forecast.instance
   <Instance: issued="2020-10-26 00:00:00+00:00", tag="ec-ens", scenarios=51>
   >>> df = forecast.to_dataframe(name='wind forecast')
   >>> df
                                       wind forecast                                ...
                             2020-10-26 00:00 ec-ens                                ...
                                                           e00       e01       e02  ...       e47       e48       e49       e50
   date                                                                             ...
   2020-10-27 00:00:00+01:00                26575.48  26733.56  27500.18  26672.14  ...  24269.32  24301.24  30265.62  24280.31
   2020-10-28 00:00:00+01:00                30657.37  30446.78  28420.88  37041.53  ...  28426.01  27353.77  32797.71  28044.18
   2020-10-29 00:00:00+01:00                27776.44  27720.31  30748.11  28341.64  ...  30731.12  25900.96  29088.77  28441.85
   2020-10-30 00:00:00+01:00                26984.86  23955.59  32940.16  27493.37  ...  38920.07  34470.99  26831.95  30003.82
   2020-10-31 00:00:00+01:00                15179.69  14326.49  16155.63  16337.56  ...  16874.91  10602.34   8203.10  27192.68
   ...

There are 52 columns with data here. The first one, the one with a blank third
column header, is the mean of all the other scenarios (also known as ensembles).

You can extract a single ensemble like so (here we extract scenario ``e48``
from the ``2020-10-26 00:00 ec-ens`` instance:

   >>> df['wind forecast']['2020-10-26 00:00 ec-ens']['e48']
   date
   2020-10-27 00:00:00+01:00    24301.24
   2020-10-28 00:00:00+01:00    27353.77
   2020-10-29 00:00:00+01:00    25900.96
   2020-10-30 00:00:00+01:00    34470.99
   ...


Convert period-based series
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Period-based series are converted almost the same as time series. The only
difference is that you must supply a **frequency** parameter to the
``to_dataframe(frequency)`` method. You should read the above section before
continuing.

Here we convert a REMIT series for German nuclear available capacity to a daily
average capacity ``pandas.DataFrame``:

   >>> periodseries.instance
   <Instance: issued="2020-10-24 14:10:40+00:00", tag="a-PvMRn_EpOJtngkh4D06Q">
   >>> df = periodseries.to_dataframe(
   >>>    frequency=Frequency.P1D,
   >>>    name='de nuclear remit'
   >>> )
   >>> df
                                                    de nuclear remit
                             2020-10-24 14:10 a-PvMRn_EpOJtngkh4D06Q
   <BLANKLINE>
   date
   2020-10-20 00:00:00+02:00                             6714.000000
   2020-10-21 00:00:00+02:00                             6709.812500
   2020-10-22 00:00:00+02:00                             6714.000000
   2020-10-23 00:00:00+02:00                             7145.572917
   2020-10-24 00:00:00+02:00                             7958.677083
   2020-10-25 00:00:00+02:00                             8124.000000
   ...

Notice that the second column header (the instance) is a little bit weird. That
is because it's a combination of the publication date (as ``instance.issued``)
of the REMIT outage message for nuclear powerplants in Germany and the
ID of said message (as ``instance.tag``).

Convert OHLC data
^^^^^^^^^^^^^^^^^

When you have an :py:class:`~energyquantified.data.OHLCList`, which is the
response type from ``eq.ohlc.load()``, you can do this:

   >>> df = ohlc_list.to_dataframe()
   >>> df
           traded   period  front    delivery   open   high    low  close  settlement  volume  open_interest
   0   2020-10-15      day      1  2020-10-16    NaN    NaN    NaN    NaN       23.24     0.0            0.0
   1   2020-10-15      day      2  2020-10-17    NaN    NaN    NaN    NaN       19.00     0.0            0.0
   2   2020-10-15      day      3  2020-10-18    NaN    NaN    NaN    NaN       16.00     0.0            0.0
   3   2020-10-15    month      1  2020-11-01  23.50  23.50  22.30  22.30       22.35   343.0        10104.0
   4   2020-10-15    month      2  2020-12-01  25.65  25.65  24.40  24.40       24.40    68.0         9772.0
   5   2020-10-15    month      3  2021-01-01    NaN    NaN    NaN    NaN       28.65     0.0          192.0
   6   2020-10-15    month      4  2021-02-01    NaN    NaN    NaN    NaN       29.28     0.0          159.0
   7   2020-10-15    month      5  2021-03-01  24.25  24.25  24.00  24.10       24.10    40.0          105.0
   8   2020-10-15    month      6  2021-04-01  22.90  22.90  22.25  22.25       22.35    36.0           10.0
   9   2020-10-15  quarter      1  2021-01-01  28.10  28.10  27.10  27.15       27.10   251.0         5731.0
   10  2020-10-15  quarter      2  2021-04-01  20.25  20.25  19.75  19.75       19.75    86.0         1762.0
   ...

You can filter down further the contracts you want. Say that you only wish
to work on **front contracts**, then do this:

   >>> df[ df['front'] == 1 ]
           traded   period  front    delivery  open  high   low  close  settlement  volume  open_interest
   0   2020-10-15      day      1  2020-10-16   NaN   NaN   NaN    NaN       23.24     0.0            0.0
   3   2020-10-15    month      1  2020-11-01  23.5  23.5  22.3  22.30       22.35   343.0        10104.0
   9   2020-10-15  quarter      1  2021-01-01  28.1  28.1  27.1  27.15       27.10   251.0         5731.0
   15  2020-10-15     week      1  2020-10-19  21.5  21.5  20.0  20.00       20.00   310.0          200.0
   21  2020-10-15     year      1  2021-01-01  23.5  23.5  22.9  23.00       22.95    89.0         9790.0

For more details on filtering, see the pandas documentation.


Convert a list of series to a data frame
----------------------------------------

Responses from ``eq.instances.load()`` and ``eq.period_instances.load()``
respectively return a :py:class:`~energyquantified.data.TimeseriesList` and a
:py:class:`~energyquantified.data.PeriodseriesList`.

Both list implementations subclasses Python's built-in list, so you can call
``append()``, ``extend()``, ``pop()``, ``remove()`` and more on them. They
also have utility methods for converting all series contained in them to a
single ``pandas.DataFrame``.

Convert a time series list
^^^^^^^^^^^^^^^^^^^^^^^^^^

Say that you have loaded three wind power forecasts in daily resolution
using ``eq.instances.load()``, then you can convert them to a
single ``pandas.DataFrame`` like this:

   >>> df = timeseries_list.to_dataframe()
   >>> df
                             DE Wind Power Production MWh/h 15min Forecast
                                                      2020-10-25 00:00 gfs 2020-10-25 00:00 ec 2020-10-24 18:00 gfs
   <BLANKLINE>
   date
   2020-10-25 00:00:00+02:00                                           NaN                 NaN             25723.21
   2020-10-26 00:00:00+01:00                                      14148.87            15312.22             13579.25
   2020-10-27 00:00:00+01:00                                      22220.05            22581.10             22010.06
   2020-10-28 00:00:00+01:00                                      27906.20            29214.30             26829.98
   2020-10-29 00:00:00+01:00                                      28905.48            26575.11             28152.93
   ...

You can also add more time series to ``timeseries_list`` using the built-in
list methods. There is only one requirement: They **must** have the **same frequency**.

   >>> timeseries_list.insert(0, wind_actual)  # Add actual first
   >>> timeseries_list.insert(1, wind_normal)  # Add normal second
   >>> df = timeseries_list.to_dataframe()
   >>> df
                             DE Wind Power Production MWh/h 15min Actual DE Wind Power Production MWh/h 15min Normal  ... DE Wind Power Production MWh/h 15min Forecast
                                                                                                                      ...                           2020-10-25 00:00 ec 2020-10-24 18:00 gfs
                                                                                                                      ...
   date                                                                                                               ...
   2020-10-23 00:00:00+02:00                                    13193.50                                    16133.94  ...                                           NaN                  NaN
   2020-10-24 00:00:00+02:00                                    22438.26                                    16291.00  ...                                           NaN                  NaN
   2020-10-25 00:00:00+02:00                                    24872.55                                    16465.75  ...                                           NaN             25723.21
   2020-10-26 00:00:00+01:00                                         NaN                                    16588.33  ...                                      15312.22             13579.25
   2020-10-27 00:00:00+01:00                                         NaN                                    16721.59  ...                                      22581.10             22010.06
   2020-10-28 00:00:00+01:00                                         NaN                                    16845.30  ...                                      29214.30             26829.98
   2020-10-29 00:00:00+01:00                                         NaN                                    16958.63  ...                                      26575.11             28152.93
   ...

To get all instances for the forecast curve from the ``pandas.DataFrame``, use pandas'
built-in filtering capabilities:

   >>> df['DE Wind Power Production MWh/h 15min Forecast']
                             2020-10-25 00:00 gfs 2020-10-25 00:00 ec 2020-10-24 18:00 gfs
   <BLANKLINE>
   date
   2020-10-23 00:00:00+02:00                  NaN                 NaN                  NaN
   2020-10-24 00:00:00+02:00                  NaN                 NaN                  NaN
   2020-10-25 00:00:00+02:00                  NaN                 NaN             25723.21
   2020-10-26 00:00:00+01:00             14148.87            15312.22             13579.25
   2020-10-27 00:00:00+01:00             22220.05            22581.10             22010.06
   2020-10-28 00:00:00+01:00             27906.20            29214.30             26829.98
   2020-10-29 00:00:00+01:00             28905.48            26575.11             28152.93
   ...

Notice that the first column header with the curve name disappeared. That is
because pandas stores the data hierarchically. All columns with the same name
are grouped together. So, in this case, we get the three instances for the
wind power forecast curve.


Convert a period-based series list
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Just like with :py:class:`~energyquantified.data.Periodseries`, specify a
**frequency** to first convert to a fixed-interval time series in your
preferred resolution in a ``pandas.DataFrame``. Using the German nuclear REMIT
capacity example as before, we can see how the available nuclear capacity was
at different times:

   >>> from energyquantified.time import Frequency
   >>> df = periodseries_list.to_dataframe(frequency=Frequency.P1D)
   >>> df
                              DE Nuclear Capacity Available MW REMIT
                             2020-10-24 14:10 a-PvMRn_EpOJtngkh4D06Q 2020-10-23 22:53 a-PvMRn_EpOJtngkh4D06Q 2020-10-23 22:32 foawy0rsE5VaMvg-JLbVbQ 2020-10-23 07:45 5mkc_POSQXzDGnTVSzsQiQ
   <BLANKLINE>
   date
   2020-10-20 00:00:00+02:00                             6714.000000                             6714.000000                             6714.000000                             6714.000000
   2020-10-21 00:00:00+02:00                             6709.812500                             6709.812500                             6709.812500                             6709.812500
   2020-10-22 00:00:00+02:00                             6714.000000                             6714.000000                             6714.000000                             6714.000000
   2020-10-23 00:00:00+02:00                             7145.572917                             7542.625000                             6714.000000                             7540.770833
   2020-10-24 00:00:00+02:00                             7958.677083                             8124.000000                             7147.750000                             8124.000000
   ...


.. _column-headers:

Column headers for time series data
-----------------------------------

The data frames created from time series data has three column header levels:

 1. **Curve name**
 2. **Instance or contract**
 3. **Scenario**

**Curve name** is set the ``timeseries.curve.name`` by default. If there is
no curve attribute on the :py:class:`~energyquantified.data.Timeseries` object,
it defaults to be blank. The user can override this name by setting a custom
name (see below).

**Instance or contract** is set (defaults to blank) when the time series has
is an instance (forecast) or when the response is an OHLC series converted
to a time series:

 * For *instances*, this column header is set to ``<issued> <tag>``, like so:
   ``2020-10-16 00:00 ec``.
 * For *contracts*, it is set to ``<period> <front|delivery> <field>``.
   Examples: ``month front-1 close`` or ``year 2024-01-01 settlement``.

**Scenario** is the scenario or ensemble ID. This header is blank unless you
load ensemble data or scenario time series. For ensembles, it is normally
named ``eNN`` where `NN` is the zero-padded ensemble ID. ECMWF ensemble
forecasts, for example, have 51 scenarios, named from ``e00``, ``e01``, ...,
``e49``, ``e50``. Climate series uses underlying weather years. These column
headers are named after the weather year they are based on: ``y1980``,
``y1981``, ..., ``y2018``, ``y2019``.


.. _single-column-headers:

Force single-level column headers
---------------------------------

While the default behaviour is to create three levels of column headers,
as seen above, you can tell the client to merge all the levels into one.

Do this by setting the parameter ``single_level_header=True`` when
you invoke ``to_dataframe()``.

Using the wind forecast example from earlier on this page:

>>> forecast.instance
<Instance: issued="2020-10-26 00:00:00+00:00", tag="ec-ens", scenarios=51>
>>> df = forecast.to_dataframe(name='wind forecast')
>>> df
                                    wind forecast                                ...
                          2020-10-26 00:00 ec-ens                                ...
                                                        e00       e01       e02  ...       e47       e48       e49       e50
date                                                                             ...
2020-10-27 00:00:00+01:00                26575.48  26733.56  27500.18  26672.14  ...  24269.32  24301.24  30265.62  24280.31
2020-10-28 00:00:00+01:00                30657.37  30446.78  28420.88  37041.53  ...  28426.01  27353.77  32797.71  28044.18
2020-10-29 00:00:00+01:00                27776.44  27720.31  30748.11  28341.64  ...  30731.12  25900.96  29088.77  28441.85
2020-10-30 00:00:00+01:00                26984.86  23955.59  32940.16  27493.37  ...  38920.07  34470.99  26831.95  30003.82
2020-10-31 00:00:00+01:00                15179.69  14326.49  16155.63  16337.56  ...  16874.91  10602.34   8203.10  27192.68
...

We can add the ``single_level_header`` parameter. Notice that the headers,
which previously were three levels (curve name, instance and scenario), are
now merged into one row:

>>> df = forecast.to_dataframe(
>>>     name='wind forecast',
>>>     single_level_header=True  # Merge column headers
>>> )
                          wind forecast 2020-10-26 00:00 ec-ens wind forecast 2020-10-26 00:00 ec-ens e00  ... wind forecast 2020-10-26 00:00 ec-ens e49 wind forecast 2020-10-26 00:00 ec-ens e50
date                                                                                                       ...
2020-10-27 00:00:00+01:00                              26575.48                                  26733.56  ...                                  30265.62                                  24280.31
2020-10-28 00:00:00+01:00                              30657.37                                  30446.78  ...                                  32797.71                                  28044.18
2020-10-29 00:00:00+01:00                              27776.44                                  27720.31  ...                                  29088.77                                  28441.85
2020-10-30 00:00:00+01:00                              26984.86                                  23955.59  ...                                  26831.95                                  30003.82
2020-10-31 00:00:00+01:00                              15179.69                                  14326.49  ...                                   8203.10                                  27192.68
...

Some functions and utilities in pandas work best when the ``DataFrame`` has
a single level header. Setting ``single_level_header=True`` makes it easier
than if you would have to merge the headers manually.


Set custom time series name
---------------------------

Energy Quantified's curve names are made to be easy to understand but can be
quite long. So we made a :py:meth:`~energyquantified.data.base.Series.set_name`
method for :py:class:`~energyquantified.data.Timeseries`: and
:py:class:`~energyquantified.data.Periodseries`.

Use it to set your own custom name before converting to a ``pandas.DataFrame``:

   >>> timeseries.name
   'DE Wind Power Production MWh/h 15min Actual'
   >>> timeseries.set_name('de wind actual')
   >>> timeseries.name
   'de wind actual'

The custom name is reflected in the ``pandas.DataFrame`` column header:

   >>> timeseries.to_dataframe()
                             de wind actual
   <BLANKLINE>
   <BLANKLINE>
   date
   2020-01-01 00:00:00+01:00        8928.95
   2020-01-02 00:00:00+01:00       16302.95
   2020-01-03 00:00:00+01:00       32063.55
   2020-01-04 00:00:00+01:00       33299.36
   2020-01-05 00:00:00+01:00       13151.01

You can also specify a name when invoking the ``to_dataframe()`` method on
time series objects:

   >>> timeseries.to_dataframe(name='my awesome name')
                             my awesome name
   <BLANKLINE>
   <BLANKLINE>
   date
   2020-01-01 00:00:00+01:00         8928.95
   2020-01-02 00:00:00+01:00        16302.95
   2020-01-03 00:00:00+01:00        32063.55
   2020-01-04 00:00:00+01:00        33299.36
   2020-01-05 00:00:00+01:00        13151.01
