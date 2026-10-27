PPA
===

This page shows how to load power purchase agreement (PPA) prices. All
examples below expects you to have an initialized instance of the client
called ``eq``.

Operations described here are available under ``eq.ppa.*``.

**Requirements:** Use these operations for curves with ``curve_type`` set
to any of the following:

 * ``PPA``

PPA objects
-----------

Each curve holds the PPA prices for one price area, such as
``DE Power Purchase Agreement EUR/MWh PPA``. The prices are quoted in
the curve's own currency.

When loading PPA data, the response is a list of PPA objects. A PPA object
consists of a **product** and a **price**:

.. code-block::

   class PPA:
       product: PPAProduct
       price: number

The **product** field describes which agreement the price is for:

.. code-block::

   class PPAProduct:
       date: date
       technology: Technology
       contract_structure: ContractStructure
       delivery_begin: date
       duration: PPADuration

The parameters:

 * **date** – The date the price was quoted.
 * **technology** – The generation technology: solar, onshore wind or
   offshore wind. See :py:class:`energyquantified.metadata.Technology`.
 * **contract_structure** – How the delivered volume is shaped: yearly
   baseload, monthly baseload, proxy or pay as produced. See
   :py:class:`energyquantified.metadata.ContractStructure`.
 * **delivery_begin** – The date delivery starts.
 * **duration** – The length of the agreement: 3, 5, 10 or 15 years. See
   :py:class:`energyquantified.metadata.PPADuration`.

Load PPA data
-------------

Method reference: :py:meth:`eq.ppa.load() <energyquantified.api.PpaAPI.load>`

You must at least specify these three parameters: **curve**, **begin** and
**end**. ``begin`` and ``end`` select prices by quote date. ``begin`` is
inclusive and ``end`` is exclusive.

   >>> from datetime import date
   >>> ppa_list = eq.ppa.load(
   >>>    'DE Power Purchase Agreement EUR/MWh PPA',
   >>>    begin=date(2026, 9, 1),   # or begin='2026-09-01'
   >>>    end=date(2026, 10, 1)     # or end='2026-10-01'
   >>> )

The response is a :class:`energyquantified.data.PPAList` of
:class:`energyquantified.data.PPA` objects. It is ordered by quote date,
technology, contract structure, delivery start and duration. The list also
has ``curve``, ``unit`` and ``denominator`` attributes:

   >>> ppa_list.curve
   <Curve: "DE Power Purchase Agreement EUR/MWh PPA", curve_type=PPA>

   >>> ppa_list
   [<PPA: <PPAProduct: date=2026-09-29, technology=SOLAR, contract_structure=PAY_AS_PRODUCED, delivery_begin=2027-01-01, duration=TEN_YEARS>, price=41.85>,
    <PPA: <PPAProduct: date=2026-09-29, technology=SOLAR, contract_structure=YEARLY_BASELOAD, delivery_begin=2027-01-01, duration=TEN_YEARS>, price=52.1>,
    <PPA: <PPAProduct: date=2026-09-29, technology=WIND_ONSHORE, contract_structure=PAY_AS_PRODUCED, delivery_begin=2027-01-01, duration=TEN_YEARS>, price=58.4>,
    ...

Filter PPA data
^^^^^^^^^^^^^^^

You can filter on **technology**, **contract_structure**, **delivery_begin**
and **duration**. ``technology``, ``contract_structure`` and ``duration``
accept a single value or a list of values. Filters on different fields are
combined, while several values for the same filter match any of them.

Say that we only want yearly and monthly baseload contracts for onshore
wind:

   >>> from energyquantified.metadata import ContractStructure, Technology
   >>> ppa_list = eq.ppa.load(
   >>>    'DE Power Purchase Agreement EUR/MWh QW01 PPA',
   >>>    begin=date(2026, 9, 1),
   >>>    end=date(2026, 10, 1),
   >>>    technology=Technology.WIND_ONSHORE,
   >>>    contract_structure=[
   >>>        ContractStructure.YEARLY_BASELOAD,
   >>>        ContractStructure.MONTHLY_BASELOAD,
   >>>    ],
   >>> )

The filters also accept the API's tags as strings, such as
``technology="wind_onshore"`` or ``contract_structure="year"``. Give
durations in years:

   >>> ppa_list = eq.ppa.load(
   >>>    'DE Power Purchase Agreement EUR/MWh QW01 PPA',
   >>>    begin=date(2026, 9, 1),
   >>>    end=date(2026, 10, 1),
   >>>    delivery_begin=date(2027, 1, 1),
   >>>    duration=[5, 10],  # or [PPADuration.FIVE_YEARS, PPADuration.TEN_YEARS]
   >>> )

Load for the latest quote date
------------------------------

Method reference: :py:meth:`eq.ppa.latest() <energyquantified.api.PpaAPI.latest>`

Load all PPA prices from the latest available quote date. You must only
specify one parameter: **curve**. You may also specify an optional **date**
parameter to load the prices from the latest quote date on or before the
given date.

   >>> latest_list = eq.ppa.latest('DE Power Purchase Agreement EUR/MWh QW01 PPA')

   >>> latest_list = eq.ppa.latest(
   >>>    'DE Power Purchase Agreement EUR/MWh QW01 PPA',
   >>>    date=date(2026, 9, 29),
   >>> )

:py:meth:`eq.ppa.latest() <energyquantified.api.PpaAPI.latest>` supports the
same filters as :py:meth:`eq.ppa.load() <energyquantified.api.PpaAPI.load>`.

Convert prices to another currency
----------------------------------

Both operations take a **unit** parameter for converting the prices from
the curve's own currency:

   >>> latest_list = eq.ppa.latest(
   >>>    'DE Power Purchase Agreement EUR/MWh QW01 PPA',
   >>>    unit='USD',
   >>> )
   >>> latest_list.unit
   'USD'

Convert a PPA list to a data frame
----------------------------------

Convert a :class:`PPAList <energyquantified.data.PPAList>` to a
``pandas.DataFrame`` like this:

   >>> latest_list.to_pandas_dataframe()
            date     technology contract_structure delivery_begin  duration  price
   0  2026-09-29          solar    pay_as_produced     2027-01-01        10  41.85
   1  2026-09-29          solar               year     2027-01-01        10  52.10
   2  2026-09-29   wind_onshore    pay_as_produced     2027-01-01        10  58.40
   3  2026-09-29   wind_onshore               year     2027-01-01         5  63.95
   4  2026-09-29   wind_onshore               year     2027-01-01        10  61.20
   5  2026-09-29  wind_offshore    pay_as_produced     2027-01-01        15  72.30

Convert a :class:`PPAList <energyquantified.data.PPAList>` to a
``polars.DataFrame`` like this:

   >>> latest_list.to_polars_dataframe()
   shape: (6, 6)
   ┌────────────┬───────────────┬────────────────────┬────────────────┬──────────┬───────┐
   │ date       ┆ technology    ┆ contract_structure ┆ delivery_begin ┆ duration ┆ price │
   │ ---        ┆ ---           ┆ ---                ┆ ---            ┆ ---      ┆ ---   │
   │ date       ┆ str           ┆ str                ┆ date           ┆ i32      ┆ f64   │
   ╞════════════╪═══════════════╪════════════════════╪════════════════╪══════════╪═══════╡
   │ 2026-09-29 ┆ solar         ┆ pay_as_produced    ┆ 2027-01-01     ┆ 10       ┆ 41.85 │
   │ 2026-09-29 ┆ solar         ┆ year               ┆ 2027-01-01     ┆ 10       ┆ 52.1  │
   │ 2026-09-29 ┆ wind_onshore  ┆ pay_as_produced    ┆ 2027-01-01     ┆ 10       ┆ 58.4  │
   │ 2026-09-29 ┆ wind_onshore  ┆ year               ┆ 2027-01-01     ┆ 5        ┆ 63.95 │
   │ 2026-09-29 ┆ wind_onshore  ┆ year               ┆ 2027-01-01     ┆ 10       ┆ 61.2  │
   │ 2026-09-29 ┆ wind_offshore ┆ pay_as_produced    ┆ 2027-01-01     ┆ 15       ┆ 72.3  │
   └────────────┴───────────────┴────────────────────┴────────────────┴──────────┴───────┘

The ``technology`` and ``contract_structure`` columns hold the API's tags,
and ``duration`` holds the number of years.
