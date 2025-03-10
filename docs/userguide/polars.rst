Polars integration
==================

This page describes the `polars <https://pola.rs/>`_ integration
of Energy Quantified's Python client. We chose to integrate with polars because
it is quite popular and it works great with time series data. For full
documentation on **polars**, refer to their
`documentation <https://docs.pola.rs/>`_.

Polars is **not required** to use the ``energyquantified`` package. You must
therefore **install polars** separately to use the following operations.

We also support `pandas <https://pandas.pydata.org>`_ for data frames. See the
:ref:`pandas integration page <pandas>` for more information.


Convert data series to data frames
----------------------------------

You can convert any of these types to a ``polars.DataFrame``:

 * :py:class:`~energyquantified.data.Timeseries`
 * :py:class:`~energyquantified.data.Periodseries`
 * :py:class:`~energyquantified.data.OHLCList`

They all have a method called ``to_polars_dataframe()``. ``Periodseries`` differs from
the two others in which you must supply a **frequency** parameter.

There also exists an alias of ``to_polars_dataframe()`` called ``to_pl_df()``. The term
``df`` is a commonly used shorthand and variable name for ``DataFrame``'s.

Note: There also exist a method called ``to_pandas_dataframe()`` and ``to_pd_df()`` for
converting to `pandas <https://pandas.pydata.org>`_ data frames. See the
:ref:`pandas integration page <pandas>` for more information.

Convert time series
^^^^^^^^^^^^^^^^^^^

Converting a time series is simple:

    >>> df = timeseries.to_polars_dataframe()
    >>> df
    shape: (5, 2)
    ┌─────────────────────────┬─────────────────────────────────┐
    │ date                    ┆ DE Wind Power Production MWh/h… │
    │ ---                     ┆ ---                             │
    │ datetime[μs, CET]       ┆ f64                             │
    ╞═════════════════════════╪═════════════════════════════════╡
    │ 2020-01-01 00:00:00 CET ┆ 9071.91                         │
    │ 2020-01-02 00:00:00 CET ┆ 16347.9                         │
    │ 2020-01-03 00:00:00 CET ┆ 32408.07                        │
    │ 2020-01-04 00:00:00 CET ┆ 33438.74                        │
    │ 2020-01-05 00:00:00 CET ┆ 13230.72                        │
    └─────────────────────────┴─────────────────────────────────┘

You can also set a custom name if you think the default one is a little
too verbose:

    >>> df = timeseries.to_polars_dataframe(name='de wind')
    >>> df
    shape: (5, 2)
    ┌─────────────────────────┬──────────┐
    │ date                    ┆ de wind  │
    │ ---                     ┆ ---      │
    │ datetime[μs, CET]       ┆ f64      │
    ╞═════════════════════════╪══════════╡
    │ 2020-01-01 00:00:00 CET ┆ 9071.91  │
    │ 2020-01-02 00:00:00 CET ┆ 16347.9  │
    │ 2020-01-03 00:00:00 CET ┆ 32408.07 │
    │ 2020-01-04 00:00:00 CET ┆ 33438.74 │
    │ 2020-01-05 00:00:00 CET ┆ 13230.72 │
    └─────────────────────────┴──────────┘

If you have a scenario-based time series (such as a time series loaded for
an ensemble forecast), you will get one column per ensemble.

Notice that each column is made from three components. The first is the
**curve**, the second is the **instance**, and the third is the **scenarios**.

    >>> forecast.instance
    <Instance: issued="2020-10-26 00:00:00+00:00", tag="ec-ens", scenarios=51>
    >>> df = forecast.to_polars_dataframe(name='de wind')
    >>> df
    shape: (14, 53)
    ┌─────────────────────────┬──────────┬─────────────┬─────────────┬───┬─────────────┬─────────────┬─────────────┬─────────────┐
    │ date                    ┆ de wind  ┆ de wind e00 ┆ de wind e01 ┆ … ┆ de wind e47 ┆ de wind e48 ┆ de wind e49 ┆ de wind e50 │
    │ ---                     ┆ ---      ┆ ---         ┆ ---         ┆   ┆ ---         ┆ ---         ┆ ---         ┆ ---         │
    │ datetime[μs, CET]       ┆ f64      ┆ f64         ┆ f64         ┆   ┆ f64         ┆ f64         ┆ f64         ┆ f64         │
    ╞═════════════════════════╪══════════╪═════════════╪═════════════╪═══╪═════════════╪═════════════╪═════════════╪═════════════╡
    │ 2020-10-27 00:00:00 CET ┆ 26575.48 ┆ 26733.56    ┆ 27500.18    ┆ … ┆ 24269.32    ┆ 24301.24    ┆ 30265.62    ┆ 24280.31    │
    │ 2020-10-28 00:00:00 CET ┆ 30657.37 ┆ 30446.78    ┆ 28420.88    ┆ … ┆ 28426.01    ┆ 27353.77    ┆ 32797.71    ┆ 28044.18    │
    │ 2020-10-29 00:00:00 CET ┆ 27776.44 ┆ 27720.31    ┆ 30748.11    ┆ … ┆ 30731.12    ┆ 25900.96    ┆ 29088.77    ┆ 28441.85    │
    │ 2020-10-30 00:00:00 CET ┆ 26984.86 ┆ 23955.59    ┆ 32940.16    ┆ … ┆ 38920.07    ┆ 34470.99    ┆ 26831.95    ┆ 30003.82    │
    │ 2020-10-31 00:00:00 CET ┆ 15179.69 ┆ 14326.49    ┆ 16155.63    ┆ … ┆ 16874.91    ┆ 10602.34    ┆ 8203.1      ┆ 27192.68    │
    │ …                       ┆ …        ┆ …           ┆ …           ┆ … ┆ …           ┆ …           ┆ …           ┆ …           │
    │ 2020-11-05 00:00:00 CET ┆ 19212.78 ┆ 41683.26    ┆ 29293.03    ┆ … ┆ 25730.43    ┆ 33394.54    ┆ 29395.27    ┆ 13270.89    │
    │ 2020-11-06 00:00:00 CET ┆ 18814.47 ┆ 38715.68    ┆ 8994.4      ┆ … ┆ 21424.98    ┆ 36817.54    ┆ 39952.28    ┆ 6765.39     │
    │ 2020-11-07 00:00:00 CET ┆ 16637.23 ┆ 20419.86    ┆ 3061.14     ┆ … ┆ 11021.58    ┆ 25435.09    ┆ 30738.6     ┆ 4298.48     │
    │ 2020-11-08 00:00:00 CET ┆ 13431.43 ┆ 7185.19     ┆ 3304.81     ┆ … ┆ 30308.28    ┆ 14438.97    ┆ 21285.35    ┆ 12204.36    │
    │ 2020-11-09 00:00:00 CET ┆ 13936.37 ┆ 16653.86    ┆ 7325.08     ┆ … ┆ 33969.75    ┆ 23434.31    ┆ 24121.93    ┆ 10273.44    │
    └─────────────────────────┴──────────┴─────────────┴─────────────┴───┴─────────────┴─────────────┴─────────────┴─────────────┘

There are 52 columns with data here. The first one, the one without a scenario
identifier, is the mean of all the other scenarios (also known as ensembles).

You can extract a single ensemble like so (here we extract scenario ``e48``
from the ``2020-10-26 00:00 ec-ens`` instance:

    >>> df.select(pl.col('date'), pl.col('de wind e48'))
    shape: (14, 2)
    ┌─────────────────────────┬─────────────┐
    │ date                    ┆ de wind e48 │
    │ ---                     ┆ ---         │
    │ datetime[μs, CET]       ┆ f64         │
    ╞═════════════════════════╪═════════════╡
    │ 2020-10-27 00:00:00 CET ┆ 24301.24    │
    │ 2020-10-28 00:00:00 CET ┆ 27353.77    │
    │ 2020-10-29 00:00:00 CET ┆ 25900.96    │
    │ 2020-10-30 00:00:00 CET ┆ 34470.99    │
    │ 2020-10-31 00:00:00 CET ┆ 10602.34    │
    │ …                       ┆ …           │
    │ 2020-11-05 00:00:00 CET ┆ 33394.54    │
    │ 2020-11-06 00:00:00 CET ┆ 36817.54    │
    │ 2020-11-07 00:00:00 CET ┆ 25435.09    │
    │ 2020-11-08 00:00:00 CET ┆ 14438.97    │
    │ 2020-11-09 00:00:00 CET ┆ 23434.31    │
    └─────────────────────────┴─────────────┘

Convert period-based series
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Period-based series are converted almost the same as time series. The only
difference is that you must supply a **frequency** parameter to the
``to_polars_dataframe(frequency)`` method. You should read the above section before
continuing.

Here we convert a REMIT series for German nuclear available capacity to a daily
average capacity ``polars.DataFrame``:

   >>> from energyquantified.time import Frequency
   >>> periodseries.instance
   <Instance: issued="2020-10-24 14:10:40+00:00", tag="a-PvMRn_EpOJtngkh4D06Q">
   >>> df = periodseries.to_polars_dataframe(
   >>>    frequency=Frequency.P1D,
   >>>    name='de nuclear remit'
   >>> )
   >>> df
    shape: (7, 2)
    ┌──────────────────────────┬──────────────────┐
    │ date                     ┆ de nuclear remit │
    │ ---                      ┆ ---              │
    │ datetime[μs, CET]        ┆ f64              │
    ╞══════════════════════════╪══════════════════╡
    │ 2020-10-23 00:00:00 CEST ┆ 7145.6           │
    │ 2020-10-24 00:00:00 CEST ┆ 7958.7           │
    │ 2020-10-25 00:00:00 CEST ┆ 8124.0           │
    │ 2020-10-26 00:00:00 CET  ┆ 8124.0           │
    │ 2020-10-27 00:00:00 CET  ┆ 8124.0           │
    │ 2020-10-28 00:00:00 CET  ┆ 8124.0           │
    │ 2020-10-29 00:00:00 CET  ┆ 8124.0           │
    └──────────────────────────┴──────────────────┘

Convert OHLC data
^^^^^^^^^^^^^^^^^

When you have an :py:class:`~energyquantified.data.OHLCList`, which is the
response type from ``eq.ohlc.load()``, you can do this:

   >>> df = ohlc_list.to_polars_dataframe()
   >>> df
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

You can filter down further the contracts you want. Say that you only wish
to work on **front contracts**, then do this:

    >>> df.filter(pl.col('front') == 1)
    shape: (5, 11)
    ┌────────────┬─────────┬───────┬────────────┬──────┬──────┬──────┬───────┬────────────┬────────┬───────────────┐
    │ traded     ┆ period  ┆ front ┆ delivery   ┆ open ┆ high ┆ low  ┆ close ┆ settlement ┆ volume ┆ open_interest │
    │ ---        ┆ ---     ┆ ---   ┆ ---        ┆ ---  ┆ ---  ┆ ---  ┆ ---   ┆ ---        ┆ ---    ┆ ---           │
    │ date       ┆ str     ┆ i32   ┆ date       ┆ f64  ┆ f64  ┆ f64  ┆ f64   ┆ f64        ┆ f64    ┆ f64           │
    ╞════════════╪═════════╪═══════╪════════════╪══════╪══════╪══════╪═══════╪════════════╪════════╪═══════════════╡
    │ 2020-10-15 ┆ day     ┆ 1     ┆ 2020-10-16 ┆ null ┆ null ┆ null ┆ null  ┆ 23.24      ┆ 0.0    ┆ 0.0           │
    │ 2020-10-15 ┆ month   ┆ 1     ┆ 2020-11-01 ┆ 23.5 ┆ 23.5 ┆ 22.3 ┆ 22.3  ┆ 22.35      ┆ 343.0  ┆ 10104.0       │
    │ 2020-10-15 ┆ quarter ┆ 1     ┆ 2021-01-01 ┆ 28.1 ┆ 28.1 ┆ 27.1 ┆ 27.15 ┆ 27.1       ┆ 251.0  ┆ 5731.0        │
    │ 2020-10-15 ┆ week    ┆ 1     ┆ 2020-10-19 ┆ 21.5 ┆ 21.5 ┆ 20.0 ┆ 20.0  ┆ 20.0       ┆ 310.0  ┆ 200.0         │
    │ 2020-10-15 ┆ year    ┆ 1     ┆ 2021-01-01 ┆ 23.5 ┆ 23.5 ┆ 22.9 ┆ 23.0  ┆ 22.95      ┆ 89.0   ┆ 9790.0        │
    └────────────┴─────────┴───────┴────────────┴──────┴──────┴──────┴───────┴────────────┴────────┴───────────────┘

For more details on filtering, see the polars documentation.


Convert a list of series to a data frame
----------------------------------------

Responses from ``eq.instances.load()`` and ``eq.period_instances.load()``
respectively return a :py:class:`~energyquantified.data.TimeseriesList` and a
:py:class:`~energyquantified.data.PeriodseriesList`.

Both list implementations subclasses Python's built-in list, so you can call
``append()``, ``extend()``, ``pop()``, ``remove()`` and more on them. They
also have utility methods for converting all series contained in them to a
single ``polars.DataFrame``.

Convert a time series list
^^^^^^^^^^^^^^^^^^^^^^^^^^

Say that you have loaded three wind power forecasts in daily resolution
using ``eq.instances.load()``, then you can convert them to a
single ``polars.DataFrame`` like this:

   >>> df = timeseries_list.to_polars_dataframe()
   >>> df
    shape: (10, 4)
    ┌──────────────────────────┬─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
    │ date                     ┆ DE Wind Power Production MWh/h… ┆ DE Wind Power Production MWh/h… ┆ DE Wind Power Production MWh/h… │
    │ ---                      ┆ ---                             ┆ ---                             ┆ ---                             │
    │ datetime[μs, CET]        ┆ f64                             ┆ f64                             ┆ f64                             │
    ╞══════════════════════════╪═════════════════════════════════╪═════════════════════════════════╪═════════════════════════════════╡
    │ 2020-10-25 00:00:00 CEST ┆ null                            ┆ null                            ┆ 23719.96                        │
    │ 2020-10-26 00:00:00 CET  ┆ 14148.87                        ┆ 15312.22                        ┆ 15718.38                        │
    │ 2020-10-27 00:00:00 CET  ┆ 22220.05                        ┆ 22581.1                         ┆ 22822.31                        │
    │ 2020-10-28 00:00:00 CET  ┆ 27906.2                         ┆ 29214.3                         ┆ 29885.93                        │
    │ 2020-10-29 00:00:00 CET  ┆ 28905.48                        ┆ 26575.11                        ┆ 35468.61                        │
    │ 2020-10-30 00:00:00 CET  ┆ 23433.83                        ┆ 13625.3                         ┆ 36959.33                        │
    │ 2020-10-31 00:00:00 CET  ┆ 9089.62                         ┆ 13267.83                        ┆ 22327.69                        │
    │ 2020-11-01 00:00:00 CET  ┆ 20825.92                        ┆ 23891.26                        ┆ 24770.07                        │
    │ 2020-11-02 00:00:00 CET  ┆ 26066.78                        ┆ 38314.79                        ┆ 21068.64                        │
    │ 2020-11-03 00:00:00 CET  ┆ 26569.44                        ┆ 25767.19                        ┆ null                            │
    └──────────────────────────┴─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘

You can also add more time series to ``timeseries_list`` using the built-in
list methods. There is only one requirement: They **must** have the **same frequency**.

   >>> timeseries_list.insert(0, wind_actual)  # Add actual first
   >>> timeseries_list.insert(1, wind_normal)  # Add normal second
   >>> df = timeseries_list.to_polars_dataframe()
   >>> df
    shape: (12, 6)
    ┌──────────────────────────┬──────────────────────────┬──────────────────────────┬───────────────────────────────────┬───────────────────────────────────┬───────────────────────────────────┐
    │ date                     ┆ DE Wind Power Production ┆ DE Wind Power Production ┆ DE Wind Power Production MWh/h…   ┆ DE Wind Power Production MWh/h…   ┆ DE Wind Power Production MWh/h…   │
    │ ---                      ┆ MWh/h…                   ┆ MWh/h…                   ┆ ---                               ┆ ---                               ┆ ---                               │
    │ datetime[μs, CET]        ┆ ---                      ┆ ---                      ┆ f64                               ┆ f64                               ┆ f64                               │
    │                          ┆ f64                      ┆ f64                      ┆                                   ┆                                   ┆                                   │
    ╞══════════════════════════╪══════════════════════════╪══════════════════════════╪═══════════════════════════════════╪═══════════════════════════════════╪═══════════════════════════════════╡
    │ 2020-10-23 00:00:00 CEST ┆ null                     ┆ null                     ┆ null                              ┆ 13213.79                          ┆ 15756.45                          │
    │ 2020-10-24 00:00:00 CEST ┆ null                     ┆ null                     ┆ null                              ┆ 22506.26                          ┆ 16053.49                          │
    │ 2020-10-25 00:00:00 CEST ┆ null                     ┆ null                     ┆ 23719.96                          ┆ 24920.88                          ┆ 16398.96                          │
    │ 2020-10-26 00:00:00 CET  ┆ 14148.87                 ┆ 15312.22                 ┆ 15718.38                          ┆ null                              ┆ 16713.83                          │
    │ 2020-10-27 00:00:00 CET  ┆ 22220.05                 ┆ 22581.1                  ┆ 22822.31                          ┆ null                              ┆ 17030.37                          │
    │ …                        ┆ …                        ┆ …                        ┆ …                                 ┆ …                                 ┆ …                                 │
    │ 2020-10-30 00:00:00 CET  ┆ 23433.83                 ┆ 13625.3                  ┆ 36959.33                          ┆ null                              ┆ 17740.51                          │
    │ 2020-10-31 00:00:00 CET  ┆ 9089.62                  ┆ 13267.83                 ┆ 22327.69                          ┆ null                              ┆ 17838.79                          │
    │ 2020-11-01 00:00:00 CET  ┆ 20825.92                 ┆ 23891.26                 ┆ 24770.07                          ┆ null                              ┆ 17844.98                          │
    │ 2020-11-02 00:00:00 CET  ┆ 26066.78                 ┆ 38314.79                 ┆ 21068.64                          ┆ null                              ┆ 17773.66                          │
    │ 2020-11-03 00:00:00 CET  ┆ 26569.44                 ┆ 25767.19                 ┆ null                              ┆ null                              ┆ 17646.08                          │
    └──────────────────────────┴──────────────────────────┴──────────────────────────┴───────────────────────────────────┴───────────────────────────────────┴───────────────────────────────────┘

To get all instances for the forecast curve from the ``polars.DataFrame``, use polars'
built-in filtering capabilities:

    >>> df.select(pl.col('date'), pl.col('^.*Forecast.*$'))
    shape: (12, 4)
    ┌──────────────────────────┬─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
    │ date                     ┆ DE Wind Power Production MWh/h… ┆ DE Wind Power Production MWh/h… ┆ DE Wind Power Production MWh/h… │
    │ ---                      ┆ ---                             ┆ ---                             ┆ ---                             │
    │ datetime[μs, CET]        ┆ f64                             ┆ f64                             ┆ f64                             │
    ╞══════════════════════════╪═════════════════════════════════╪═════════════════════════════════╪═════════════════════════════════╡
    │ 2020-10-23 00:00:00 CEST ┆ null                            ┆ null                            ┆ null                            │
    │ 2020-10-24 00:00:00 CEST ┆ null                            ┆ null                            ┆ null                            │
    │ 2020-10-25 00:00:00 CEST ┆ null                            ┆ null                            ┆ 23719.96                        │
    │ 2020-10-26 00:00:00 CET  ┆ 14148.87                        ┆ 15312.22                        ┆ 15718.38                        │
    │ 2020-10-27 00:00:00 CET  ┆ 22220.05                        ┆ 22581.1                         ┆ 22822.31                        │
    │ …                        ┆ …                               ┆ …                               ┆ …                               │
    │ 2020-10-30 00:00:00 CET  ┆ 23433.83                        ┆ 13625.3                         ┆ 36959.33                        │
    │ 2020-10-31 00:00:00 CET  ┆ 9089.62                         ┆ 13267.83                        ┆ 22327.69                        │
    │ 2020-11-01 00:00:00 CET  ┆ 20825.92                        ┆ 23891.26                        ┆ 24770.07                        │
    │ 2020-11-02 00:00:00 CET  ┆ 26066.78                        ┆ 38314.79                        ┆ 21068.64                        │
    │ 2020-11-03 00:00:00 CET  ┆ 26569.44                        ┆ 25767.19                        ┆ null                            │
    └──────────────────────────┴─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘


Convert a period-based series list
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Just like with :py:class:`~energyquantified.data.Periodseries`, specify a
**frequency** to first convert to a fixed-interval time series in your
preferred resolution in a ``polars.DataFrame``. Using the German nuclear REMIT
capacity example as before, we can see how the available nuclear capacity was
at different times:

   >>> from energyquantified.time import Frequency
   >>> df = periodseries_list.to_polars_dataframe(frequency=Frequency.P1D)
   >>> df
    shape: (9, 5)
    ┌──────────────────────────┬─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┬─────────────────────────────────┐
    │ date                     ┆ DE Nuclear Capacity Available … ┆ DE Nuclear Capacity Available … ┆ DE Nuclear Capacity Available … ┆ DE Nuclear Capacity Available … │
    │ ---                      ┆ ---                             ┆ ---                             ┆ ---                             ┆ ---                             │
    │ datetime[μs, CET]        ┆ f64                             ┆ f64                             ┆ f64                             ┆ f64                             │
    ╞══════════════════════════╪═════════════════════════════════╪═════════════════════════════════╪═════════════════════════════════╪═════════════════════════════════╡
    │ 2020-10-21 00:00:00 CEST ┆ null                            ┆ null                            ┆ null                            ┆ null                            │
    │ 2020-10-22 00:00:00 CEST ┆ null                            ┆ null                            ┆ null                            ┆ null                            │
    │ 2020-10-23 00:00:00 CEST ┆ null                            ┆ null                            ┆ null                            ┆ null                            │
    │ 2020-10-24 00:00:00 CEST ┆ null                            ┆ null                            ┆ 8118.020833                     ┆ 8124.0                          │
    │ 2020-10-25 00:00:00 CEST ┆ 8124.0                          ┆ null                            ┆ 8124.0                          ┆ 8124.0                          │
    │ 2020-10-26 00:00:00 CET  ┆ 8124.0                          ┆ null                            ┆ 8124.0                          ┆ 8124.0                          │
    │ 2020-10-27 00:00:00 CET  ┆ 8124.0                          ┆ null                            ┆ 8124.0                          ┆ 8124.0                          │
    │ 2020-10-28 00:00:00 CET  ┆ 8124.0                          ┆ null                            ┆ 8124.0                          ┆ 8124.0                          │
    │ 2020-10-29 00:00:00 CET  ┆ null                            ┆ null                            ┆ null                            ┆ null                            │
    └──────────────────────────┴─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┴─────────────────────────────────┘


Column headers for time series data
-----------------------------------

The data frames created from time series data has columns made of three components:

 1. **Curve name**
 2. **Instance or contract**
 3. **Scenario**

**Curve name** is set the ``timeseries.curve.name`` by default. If there is
no curve attribute on the :py:class:`~energyquantified.data.Timeseries` object,
it defaults to be blank. The user can override this name by setting a custom
name (see below).

**Instance or contract** is set (defaults to blank) when the time series is an
instance (forecast) or when the response is an OHLC series converted to a time
series:

 * For *instances*, this column header is set to ``<curve.name> <issued> <tag>``, like so:
   ``DE Wind Power Production MWh/h 15min Forecast 2020-10-16 00:00 ec``.

**Scenario** is the scenario or ensemble ID. This header is blank unless you
load ensemble data or scenario time series. For ensembles, it is normally
named ``eNN`` where `NN` is the zero-padded ensemble ID. ECMWF ensemble
forecasts, for example, have 51 scenarios, named from ``e00``, ``e01``, ...,
``e49``, ``e50``. Climate series uses underlying weather years. These column
headers are named after the weather year they are based on: ``y1980``,
``y1981``, ..., ``y2018``, ``y2019``.


Set custom time series name
---------------------------

Energy Quantified's curve names are made to be easy to understand but can be
quite long. So we made a :py:meth:`~energyquantified.data.base.Series.set_name`
method for :py:class:`~energyquantified.data.Timeseries`: and
:py:class:`~energyquantified.data.Periodseries`.

Use it to set your own custom name before converting to a ``polars.DataFrame``:

   >>> timeseries.name
   'DE Wind Power Production MWh/h 15min Actual'
   >>> timeseries.set_name('de wind actual')
   >>> timeseries.name
   'de wind actual'

The custom name is reflected in the ``polars.DataFrame`` column header:

   >>> timeseries.to_polars_dataframe()
    shape: (5, 2)
    ┌─────────────────────────┬─────────────────┐
    │ date                    ┆ de wind actual  │
    │ ---                     ┆ ---             │
    │ datetime[μs, CET]       ┆ f64             │
    ╞═════════════════════════╪═════════════════╡
    │ 2020-01-01 00:00:00 CET ┆ 9071.91         │
    │ 2020-01-02 00:00:00 CET ┆ 16347.9         │
    │ 2020-01-03 00:00:00 CET ┆ 32408.07        │
    │ 2020-01-04 00:00:00 CET ┆ 33438.74        │
    │ 2020-01-05 00:00:00 CET ┆ 13230.72        │
    └─────────────────────────┴─────────────────┘

You can also specify a name when invoking the ``to_polars_dataframe()`` method on
time series objects:

   >>> timeseries.to_polars_dataframe(name='my awesome name')
    shape: (5, 2)
    ┌─────────────────────────┬──────────────────┐
    │ date                    ┆ my awesome name  │
    │ ---                     ┆ ---              │
    │ datetime[μs, CET]       ┆ f64              │
    ╞═════════════════════════╪══════════════════╡
    │ 2020-01-01 00:00:00 CET ┆ 9071.91          │
    │ 2020-01-02 00:00:00 CET ┆ 16347.9          │
    │ 2020-01-03 00:00:00 CET ┆ 32408.07         │
    │ 2020-01-04 00:00:00 CET ┆ 33438.74         │
    │ 2020-01-05 00:00:00 CET ┆ 13230.72         │
    └─────────────────────────┴──────────────────┘
