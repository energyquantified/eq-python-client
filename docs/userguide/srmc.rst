Short-run marginal costs (SRMC)
===============================

This page shows how to do short-run marginal cost (SRMC) calculations on
OHLC data. All examples below expects you to have an initialized instance
of the client called ``eq``.

Operations described here are available under ``eq.srmc.*``.

**Requirements:** Use these operations for the following curves:

 * Either **gas** or **coal** curves with ``curve_type = OHLC``

.. important::

    We recommend reading the section on :doc:`OHLC data <../userguide/ohlc>`
    before continuing. These operations run SRMC calculations on OHLC data,
    so it would help if you were familiar with Energy Quantified's take on
    closing prices.


On calculations
---------------

Energy Quantified supports SRMC calculations for **gas** and **coal**.
We calculate short-run marginal costs on-the-fly from closing prices:

 * You can override all factors in our SRMC calculation, such as
   efficiency, carbon emission factor and conversion rates (except for
   currency conversion).
 * Results from SRMC calculations are in **€/MWh**. Currency conversion is
   using **reference rates** from the **European Central Bank (ECB)**.
 * We use the **trading date** for the contract when deciding the **currency
   conversion rate** to use.
 * Some countries, such as the UK, has an **additional tax** (18 GBP/t as
   of this writing). It is supported in our implementation and is
   converted to EUR/t and added to the EUA price when provided.
 * Gas contracts are traded with the assumption of effectiveness in
   **higher-heating value**, but the power market uses **lower-heating value**.
   We support this conversion.

**Note:** We use settlement prices in the OHLC calculations. When returning
OHLC data for SRMC, only the ``settlement`` field is set.

More details, such as the formulas used, are available in the SRMC article on
Energy Quantified's `Knowledge base <https://app.energyquantified.com/knowledge-base/>`_
(login required).


Load SRMC
---------

Method references:
:py:meth:`eq.srmc.load_front() <energyquantified.api.SrmcAPI.load_front>` and
:py:meth:`eq.srmc.load_delivery() <energyquantified.api.SrmcAPI.load_delivery>`

Calculating historical short-run marginal costs is very similar to
`loading historical OHLC data <../userguide/ohlc.html#load-ohlc-data>`__.

However, because SRMC calculations require you to either specify a **front**
contract or a **specific** contract, we have split ``load()`` into two methods.
The difference between ``load_front()`` and ``load_delivery()`` is that
the first requires a **front** parameter and the second requires a **delivery**
parameter.

For a continuous front contract
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To calculate SRMC for the coal API2 front contract, specify the **curve**,
**begin**, **end**, **period** and **front**:

   >>> from datetime import date
   >>> from energyquantified.metadata import ContractPeriod
   >>> srmc_coal = eq.srmc.load_front(
   >>>    'Futures Coal API-2 USD/t ICE OHLC',
   >>>    begin=date(2020, 12, 1),   # or begin='2020-01-01'
   >>>    end=date(2020, 12, 30),    # or end='2020-01-06'
   >>>    period=ContractPeriod.MONTH,
   >>>    front=1,
   >>> )

The response is an :py:class:`SRMC <energyquantified.data.SRMC>` object. It
has a curve, a contract (specifying that it is a front-month contract), an
``SRMCOptions`` object with all factors used in the calculation, and a list of
OHLC objects:

   >>> srmc_coal
   <SRMC:
    curve=Futures Coal API-2 USD/t ICE OHLC,
    contract=<ContinuousContract: period=MONTH, front=1, field=>,
    options=<SRMCOptions: COAL, api2_tonne_to_mwh=6.978, efficiency=0.42, carbon_emissions=0.34056, carbon_tax_area=None>,
    ohlc=<OHLCList: items=[<OHLC>, <OHLC>, ...]>
   >

For a specific contract
^^^^^^^^^^^^^^^^^^^^^^^

Similar to front contracts, you can get the SRMC for a specific contract by
only changing the function to ``load_delivery()`` and swap out the **front**
parameter with a **delivery** date:

   >>> from datetime import date
   >>> from energyquantified.metadata import ContractPeriod
   >>> srmc_coal = eq.srmc.load_delivery(  # load_delivery()
   >>>    'Futures Coal API-2 USD/t ICE OHLC',
   >>>    begin=date(2020, 12, 1),
   >>>    end=date(2020, 12, 30),
   >>>    period=ContractPeriod.MONTH,
   >>>    delivery=date(2021, 3, 1),  # March 2021
   >>> )

The result is also very similar, except that the **contract** is now a
``SpecificContract`` while previously it was a ``ContinuousContract``:

   >>> srmc_coal
   <SRMC:
    curve=Futures Coal API-2 USD/t ICE OHLC,
    contract=<SpecificContract: period=MONTH, delivery=2021-03-01, field=>,
    options=<SRMCOptions: COAL, api2_tonne_to_mwh=6.978, efficiency=0.42, carbon_emissions=0.34056, carbon_tax_area=None>,
    ohlc=<OHLCList: items=[<OHLC>, <OHLC>, ...]>
   >

You can extract any of these attributes:

   >>> srmc_coal.curve
   <Curve: "Futures Coal API-2 USD/t ICE OHLC", curve_type=OHLC>
   >>> srmc_coal.contract
   <SpecificContract: period=MONTH, delivery=2021-03-01, field=>
   >>> srmc_coal.options
   <SRMCOptions: COAL, api2_tonne_to_mwh=6.978, efficiency=0.42, carbon_emissions=0.34056, carbon_tax_area=None>
   >>> srmc_coal.ohlc
   [<OHLC: <Product: traded=2020-12-01, period=MONTH, front=3, delivery=2021-03-01>, open=, high=, low=, close=, settlement=40.96, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-02, period=MONTH, front=3, delivery=2021-03-01>, open=, high=, low=, close=, settlement=41.63, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-03, period=MONTH, front=3, delivery=2021-03-01>, open=, high=, low=, close=, settlement=41.06, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-04, period=MONTH, front=3, delivery=2021-03-01>, open=, high=, low=, close=, settlement=42.34, volume=, open_interest=>,
    ...

And, of course, you can convert the OHLC data to a ``pandas.DataFrame`` like
this:

   >>> srmc_coal.ohlc.to_dataframe()
           traded period  front    delivery  open  high   low close  settlement volume open_interest
   0   2020-12-01  month      3  2021-03-01  None  None  None  None       40.96   None          None
   1   2020-12-02  month      3  2021-03-01  None  None  None  None       41.63   None          None
   2   2020-12-03  month      3  2021-03-01  None  None  None  None       41.06   None          None
   3   2020-12-04  month      3  2021-03-01  None  None  None  None       42.34   None          None
   ...

Load as a time series
---------------------

Method references:
:py:meth:`eq.srmc.load_front_as_timeseries() <energyquantified.api.SrmcAPI.load_front_as_timeseries>`
and
:py:meth:`eq.srmc.load_delivery_as_timeseries() <energyquantified.api.SrmcAPI.load_delivery_as_timeseries>`

This method works like
:py:meth:`eq.srmc.load_front() <energyquantified.api.SrmcAPI.load_front>`
and :py:meth:`eq.srmc.load_delivery() <energyquantified.api.SrmcAPI.load_delivery>`
(see previous section) except that it returns a daily time series instead of OHLC data.

For a continuous front contract
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To calculate SRMC for the coal API2 front contract, specify the **curve**,
**begin**, **end**, **period** and **front**:

   >>> from datetime import date
   >>> from energyquantified.metadata import ContractPeriod
   >>> srmc_coal = eq.srmc.load_front_as_timeseries(
   >>>    'Futures Coal API-2 USD/t ICE OHLC',
   >>>    begin=date(2020, 12, 1),   # or begin='2020-01-01'
   >>>    end=date(2020, 12, 30),    # or end='2020-01-06'
   >>>    period=ContractPeriod.MONTH,
   >>>    front=1,
   >>> )

The response is an :py:class:`SRMC <energyquantified.data.SRMC>` object. It
has a curve, a contract (specifying that it is a front-month contract), an
``SRMCOptions`` object with all factors used in the calculation, and a
``timeseries``:

   >>> srmc_coal
   <SRMC:
    curve=Futures Coal API-2 USD/t ICE OHLC,
    contract=<ContinuousContract: period=MONTH, front=1, field=SETTLEMENT>,
    options=<SRMCOptions: COAL, api2_tonne_to_mwh=6.978, efficiency=0.42, carbon_emissions=0.34056, carbon_tax_area=None>,
    timeseries=<Timeseries: resolution=<Resolution: frequency=P1D, timezone=CET>, curve="None", begin="2020-12-01 00:00:00+01:00", end="2020-12-16 00:00:00+01:00">
   >

You can extract the timeseries easily:

   >>> timeseries = srmc_coal.timeseries
   >>> for (date, value) in timeseries:
   >>>    print(date, value)
   2020-12-01 00:00:00+01:00 41.06
   2020-12-02 00:00:00+01:00 41.68
   2020-12-03 00:00:00+01:00 41.09
   2020-12-04 00:00:00+01:00 42.41
   2020-12-05 00:00:00+01:00 None
   2020-12-06 00:00:00+01:00 None
   2020-12-07 00:00:00+01:00 41.92
   2020-12-08 00:00:00+01:00 41.95
   ...

Notice that there are empty values during the weekend (5 December and 6
December). That is because there are no trades during these days.

For a specific contract
^^^^^^^^^^^^^^^^^^^^^^^

To calculate SRMC for a specific coal API2 contract, such as the May
2021-contract, specify the **curve**, **begin**, **end**, **period**
and **delivery** date:

   >>> from datetime import date
   >>> from energyquantified.metadata import ContractPeriod
   >>> srmc_coal = eq.srmc.load_delivery_as_timeseries(
   >>>    'Futures Coal API-2 USD/t ICE OHLC',
   >>>    begin=date(2020, 12, 1),
   >>>    end=date(2020, 12, 30),
   >>>    period=ContractPeriod.MONTH,
   >>>    delivery=date(2021, 3, 1),  # March 2021
   >>> )

The response is an :py:class:`SRMC <energyquantified.data.SRMC>` object. It
has a curve, a contract (specifying that it is the March 2021-contract), an
``SRMCOptions`` object with all factors used in the calculation, and a
``timeseries``:

   >>> srmc_coal
   <SRMC:
    curve=Futures Coal API-2 USD/t ICE OHLC,
    contract=<SpecificContract: period=MONTH, delivery=2021-03-01, field=SETTLEMENT>,
    options=<SRMCOptions: COAL, api2_tonne_to_mwh=6.978, efficiency=0.42, carbon_emissions=0.34056, carbon_tax_area=None>,
    timeseries=<Timeseries: resolution=<Resolution: frequency=P1D, timezone=CET>, curve="None", begin="2020-12-01 00:00:00+01:00", end="2020-12-16 00:00:00+01:00">
   >

You can convert the time series to a ``pandas.DataFrame`` easily:

   >>> srmc_coal.timeseries.to_dataframe()
                             Futures Coal API-2 USD/t ICE OHLC
                                   month 2021-03-01 settlement
   <BLANKLINE>
   date
   2020-12-01 00:00:00+01:00                             40.96
   2020-12-02 00:00:00+01:00                             41.63
   2020-12-03 00:00:00+01:00                             41.06
   2020-12-04 00:00:00+01:00                             42.34
   2020-12-05 00:00:00+01:00                               NaN
   2020-12-06 00:00:00+01:00                               NaN
   2020-12-07 00:00:00+01:00                             41.83
   2020-12-08 00:00:00+01:00                             41.90
   ...


Load for a trading day
----------------------

Method reference: :py:meth:`eq.srmc.latest() <energyquantified.api.SrmcAPI.latest>`

This method loads all contracts for a trading day (the latest trading day by
default) and calculates the SRMC for each of them. You may also specify an
optional **date** parameter to load data for the latest trading day up to and
including the given date:

   >>> from datetime import date
   >>> srmc_coal = eq.srmc.latest(
   >>>    'Futures Coal API-2 USD/t ICE OHLC',
   >>>    date=date(2020, 12, 14)  # Optionally set a date
   >>> )

The response will contain a list of all OHLC objects from the latest available
trading day. The response will be almost the same as for ``load_front()``
and ``load_delivery()``, except that we don't have a ``contract`` set:

   >>> srmc_coal
   <SRMC:
    curve=Futures Coal API-2 USD/t ICE OHLC,
    options=<SRMCOptions: COAL, api2_tonne_to_mwh=6.978, efficiency=0.42, carbon_emissions=0.34056, carbon_tax_area=None>,
    ohlc=<OHLCList: items=[<OHLC>, <OHLC>, <OHLC>, ...]>
   >

   >>> srmc.coal.ohlc
   [<OHLC: <Product: traded=2020-12-14, period=MONTH, front=1, delivery=2021-01-01>, open=, high=, low=, close=, settlement=44.15, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-14, period=MONTH, front=2, delivery=2021-02-01>, open=, high=, low=, close=, settlement=44.07, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-14, period=MONTH, front=3, delivery=2021-03-01>, open=, high=, low=, close=, settlement=43.94, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-14, period=QUARTER, front=1, delivery=2021-01-01>, open=, high=, low=, close=, settlement=44.05, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-14, period=QUARTER, front=2, delivery=2021-04-01>, open=, high=, low=, close=, settlement=43.79, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-14, period=QUARTER, front=3, delivery=2021-07-01>, open=, high=, low=, close=, settlement=43.68, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-14, period=YEAR, front=1, delivery=2021-01-01>, open=, high=, low=, close=, settlement=43.78, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-14, period=YEAR, front=2, delivery=2022-01-01>, open=, high=, low=, close=, settlement=44.04, volume=, open_interest=>,
    <OHLC: <Product: traded=2020-12-14, period=YEAR, front=3, delivery=2023-01-01>, open=, high=, low=, close=, settlement=44.43, volume=, open_interest=>,
    ...


Load as a forward curve
-----------------------

Method reference: :py:meth:`eq.srmc.latest_as_periods() <energyquantified.api.SrmcAPI.latest_as_periods>`

Loads all contracts for a trading day (the latest trading day by default),
sorts them and merges them into a single period-based series (like a forward
curve):

   >>> from datetime import date
   >>> srmc_coal = eq.srmc.latest_as_periods(
   >>>    'Futures Coal API-2 USD/t ICE OHLC',
   >>>    date=date(2020, 12, 14)  # Optionally set a date
   >>> )

The response is an SRMC object with a period-based series set:

   >>> srmc_coal
   <SRMC:
    curve=Futures Coal API-2 USD/t ICE OHLC,
    options=<SRMCOptions: COAL, api2_tonne_to_mwh=6.978, efficiency=0.42, carbon_emissions=0.34056, carbon_tax_area=None>,
    periodseries=<Periodseries: resolution=<Resolution: frequency=NONE, timezone=CET>, curve="Futures Coal API-2 USD/t ICE OHLC", begin="2021-01-01 00:00:00+01:00", end="2027-01-01 00:00:00+01:00">
   >

You can convert the period-based series to a time series or to a
``pandas.DataFrame`` in your preferred resolution:

   >>> # Convert to a daily time series
   >>> from energyquantified.time import Frequency
   >>> srmc_coal.periodseries.to_timeseries(frequency=Frequency.P1D)
   <Timeseries: resolution=<Resolution: frequency=P1D, timezone=CET>, curve="Futures Coal API-2 USD/t ICE OHLC", begin="2021-01-01 00:00:00+01:00", end="2027-01-01 00:00:00+01:00">

   >>> # Convert to a pandas.DataFrame in daily resolution
   >>> srmc_coal.periodseries.to_dataframe(frequency=Frequency.P1D)
                             Futures Coal API-2 USD/t ICE OHLC
   <BLANKLINE>
   <BLANKLINE>
   date
   2021-01-01 00:00:00+01:00                             44.15
   2021-01-02 00:00:00+01:00                             44.15
   2021-01-03 00:00:00+01:00                             44.15
   2021-01-04 00:00:00+01:00                             44.15
   2021-01-05 00:00:00+01:00                             44.15
   ...                                                     ...
   2026-12-27 00:00:00+01:00                             47.16
   2026-12-28 00:00:00+01:00                             47.16
   2026-12-29 00:00:00+01:00                             47.16
   2026-12-30 00:00:00+01:00                             47.16
   2026-12-31 00:00:00+01:00                             47.16
   <BLANKLINE>
   [2191 rows x 1 columns]


Override SRMC factors
---------------------

All method described above has options you may set to override any the
following factors used in the SRMC calculation:

 * ``efficiency``: The efficiency of the fuel
 * ``carbon_emissions``: The carbon emission factor
 * ``hhv_to_lhv``: Conversion from higher-heating value to lower-heating value
 * ``gas_therm_to_mwh``: Conversion factor from pence/therm to GBP/MWh
 * ``api2_tonne_to_mwh``: Conversion from coal API2 tonnes to megawatt-hours
 * ``carbon_tax_area``: Set an :py:class:`Area <energyquantified.metadata.Area>`
   to apply local tax rules. Typically used for Great Britain's carbon tax.

Just set the factor you would like to change when using the SRMC functions:

   >>> from datetime import date
   >>> from energyquantified.metadata import ContractPeriod
   >>> srmc_coal = eq.srmc.load_front(
   >>>    'Futures Coal API-2 USD/t ICE OHLC',
   >>>    begin=date(2020, 12, 1),
   >>>    end=date(2020, 12, 30),
   >>>    period=ContractPeriod.MONTH,
   >>>    front=1,
   >>>    efficiency=0.2,  # Not very efficient, eh?
   >>>    carbon_emissions=0.35  # A little more than the default carbon emission
   >>> )

The overridden factors are now visible in the response's ``SRMCOptions``:

   >>> srmc_coal
   <SRMC:
    curve=...,
    contract=...,
    options=<SRMCOptions: COAL, api2_tonne_to_mwh=6.978, efficiency=0.2, carbon_emissions=0.35, carbon_tax_area=None>,
    ohlc=...
   >
