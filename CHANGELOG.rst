Changelog
=========

dev
------

**Improvements**

- Add timezone conversion.

0.10.1
------

**Bugfixes**

- Fixed a bug introduced in v0.10 in ``PeriodSeries.to_timeseries()``


0.10
----

**Improvements**

- Add areas ``IS`` and ``LU``
- Update borders:
    - Set ``SI – HU`` and ``SI – HU`` as Flow-based
- Increase rate limits.
- Increase default request timeout.
- Add option to include ``proxies`` in ``EnergyQuantified`` and ``RealtoConnection``.
- Add support for using periods installed capacity instead of values when
  converting a ``PeriodSeries`` to a ``Timeseries`` or a ``DataFrame``.


**Bugfixes**

- Fixed an error where SRMC responses failed to parse empty lists in the response


0.9.1
-----

**Improvements**

- Improve ``Border.__hash__``, ``Border.__eq__`` and ``Border.__ne__`` methods
- Add new areas:
   - ``MA`` Morocco
   - ``LY`` Libya
   - ``DZ`` Algeria
- Add new border:
   - ``SI – HU`` Flow-based
- Borders that no longer has commercial capacity:
   - ``LV – RU``
   - ``FI – RU``
   - ``LT – RU_KGD``
- Borders that have changed to flow-based:
   - ``AT – SI``
   - ``HR – HU``
   - ``CZ – DE``
   - ``CZ – PL``
   - ``HU – SK``
   - ``PL – SK``
   - ``PL – DE``
   - ``CZ – SK``
   - ``HU – RO``
- Border updated to flowed-based and explicit:
   - ``SI – HR``


0.9
---

**Bugfixes**

- When invoking ``timeseries.to_dataframe(single_level_header=True)`` the
  resulting column index was still a ``MultiIndex`` but with a single level.
  Now the resulting column index is a normal ``Index`` type.


0.8.1
-----

**Dependencies**

- ``requests``: Use the latest v2.x available, as requests is very stable library.
- ``python-dateutil``: Use the latest v2.8.x available.


0.8
---

**Improvements**

- Add ``eq.metadata.curve()`` which returns a Curve object for the corresponding
  curve name.
- Add a section in the metadata documentation on the ``eq.metadata.curve()`` method.
- Add ``eq.metadata.curves()`` and ``eq.metadata.curve()`` to reference page in
  the documentation.
- Add ``Area.short_tag`` which is a shorter tag than ``Area.tag``. It is typically
  used for TSO areas. Example: The area with tag ``DE-Amprion`` has the short
  tag ``Amprion``.
- Changes in capacity allocation for these borders:
   - AT-CZ Implicit only
   - AT-HU Implicit only
   - NO2-GB Implicit
- Add borders:
   - RS-XK Explicit
   - TR-GE Explicit


0.7.1
-----

More gas data preparations.

**Improvements**

- Add ``Place.areas`` (list of areas), as some places (i.e. gas interconnectors)
  are places on borders and should be listed for both areas.
- Add three new place types: ``PlaceType.GAS_STORAGE``,
  ``PlaceType.GAS_LNG_TERMINAL`` and ``PlaceType.GAS_INTERCONNECTOR``
- Add ``Curve.commodity`` (str) which is either ``Power``, ``Gas``, ``Coal``,
  ``Oil``, ``Carbon`` or ``None`` at this time.
- Add a ``commodity`` filter for ``eq.metadata.curves()``.

**Deprecations**

- Add ``Place.area`` is deprecated and will eventually be replaced by
  ``Place.areas``. It will be removed in a future release.


0.7
---

Implementing Acer's non-standard Gas Day timezone.

**Improvements**

- Define new timezone in ``pytz`` called ``Europe/Gas_Day``. It follows
  Acer's Gas Day, which is from 06:00 – 06:00 in CET/CEST. This timezone is
  used for the natural gas market in the European Union. Import it with
  ``from energyquantified.time import GAS_DAY``, or look it up in ``pytz``
  like so: ``pytz.timezone("Europe/Gas_Day")``.

**Bugfixes**

- When invoking ``timeseries.to_dataframe(name="foo", single_level_header=True)``,
  the resulting column header in pandas' DataFrame no longer includes the
  instance identifier. However, the ensemble/scenario name is still appended
  at the end.


0.6.3
-----

**Improvements**

- Increase rate limits.

**Bugfixes**

- Set ``has_instances = True`` in ``CurveType.INSTANCE_PERIOD`` (was ``False``).


0.6.2
-----

**Improvements**

- Add new area Kosovo (``Area.XK``) with these borders:
   - XK–AL Explicit
   - XK–ME Explicit
   - XK–MK Explicit
- Add new border:
   - NO2–GB Explicit
- Changes in capacity allocation for these borders:
   - IT-Sud–GR Implict and Explicit
   - BG–GR Implict and Explicit
   - PL–DE Implict and Explicit
   - PL–SK Implict and Explicit
   - PL–CZ Implict and Explicit
   - DE–CZ Implict and Explicit
   - AT–CZ Implict
   - AT–HU Implict
   - GB–FR Explicit
   - GB–BE Explicit
   - GB–NL Explicit
- Remove border:
   - RS–AL


0.6.1
-----

**Improvements**

- Add ``ContractPeriod.WEEKEND`` for OHLC data.

**Bugfixes**

- Fix crashes in ``Border.__str__`` and ``Border.__repr__`` due to missing
  implementations of ``__lt__`` and ``__gt__`` in class ``Allocation``
  (thanks to stanton119).


0.6
---

A release with lots of small improvements.

**Improvements**

- Add borders and parent-child relationships for the Italian price zone
  Calabria. The price zone has been in the client for a while, but haven't
  placed in the exchange neighbour list for the other price zones in Italy
  until now.
- Add the new parameter ``single_level_header`` to all ``to_dataframe()``
  methods. By default, the ``to_dataframe()``-method will create
  ``pandas.DataFrame`` objects with three column headers. When
  ``single_level_header=True``, the client will merge all three levels into
  one header. The parameter defaults to ``False`` (to not break the old
  behaviour).
- Remove the parameter ``hhv_to_lhv`` for all SRMC API operations.
- Add a new class ``RealtoConnection``. This class is a drop-in replacement
  for the ``EnergyQuantified``-class. It lets Realto users connect to
  the Energy Quantified's API on Realto's marketplace.
- Update the documentation on how to authenticate for Realto users.
- Add a quickstart chapter for Realto users.
- Add a section in the pandas documentation on the effects of setting the
  ``single_level_header`` parameter to ``True`` in ``to_dataframe()``.
- Add documentation on the ``fill`` parameter in
  ``eq.ohlc.load_delivery_as_timeseries()`` and
  ``eq.ohlc.load_front_as_timeseries()``.
- Other minor improvements in the documentation.

**Breaking change**

- Remove the HHV-to-LHV option for gas in the SRMC API.

**Bugfixes**

- Slashes (/) weren't escaped in curve names in the URL. While this didn't
  cause issues for Energy Quantified's API, it caused an issue while
  integrating the client with Realto's marketplace.

**Dependencies**

- Upgrade ``requests`` to v2.25.1.


0.5
---

Introducing support for short-run marginal cost (SRMC) calculations from
OHLC data.

**Improvements**

- Add ``OhlcAPI#latest_as_periods()`` method for generating a "forward curve"
  from all closing prices in a market.
- Add ``fill`` parameter to ``OhlcAPI#load_front_as_timeseries()`` and
  ``OhlcAPI#load_front_as_timeseries()``.
- Add ``SRMC`` and ``SRMCOptions`` data classes.
- Implement the SRMC API: ``load_front()``, ``load_delivery()``,
  ``load_front_as_timeseries()``, ``load_delivery_as_timeseries()``,
  ``latest()``, and ``latest_as_periods()``.
- Add section in the OHLC documentation on how to load "forward curves".
- Add new chapter on SRMC in the documentation.

**Bugfixes**

- Fix a crash in the ``Contract`` JSON parser that occured only for SRMC
  operations.

**Dependencies**

- Upgrade ``requests`` to v2.25.0.


0.4.2
-----

**Improvements**

- Update border configurations (such as the AELGrO cable between Belgium
  and Germany, for instance).

**Bugfixes**

- Add missing area (SEM).


0.4.1
-----

**Bugfixes**

- Fix a crash in ``TimeseriesList#to_dataframe()``.


0.4
---

Improve pandas integration with more utility methods.

**Improvements**

- ``Page`` objects are now immutable (for curve and place search responses).
- Add ``Series.set_name()`` to let users set a custom name for time series'
  and period-based series'.
- Add ``TimeseriesList`` with a ``to_dataframe()`` method for converting a list
  of time series to a pandas data frame. It subclasses Python's built-in list
  and overrides its methods with extra validations.
- Add ``PeriodseriesList``. Similar to ``TimeseriesList``, it subclasses
  Python's list. It has two methods: (1) ``to_timeseries()`` which converts
  this list to a ``TimeseriesList``, and (2) ``to_dataframe(frequency)`` which
  converts this list to a data frame.
- Add ``Periodseries#to_dataframe(frequency)``. Previously, you would have to
  first convert the period-based series to a time series and then call
  ``to_dataframe``.
- Update headers in pandas data frames.
- Add ``OHLCList#to_dataframe()`` for converting OHLC data to a data frame.
- Update documentation where applicable with a short description on how to
  convert time series, period-based series and OHLC data to data frames.
- Add own chapter on how to convert data to ``pandas.DataFrame``.
- Add own chapter on packages and where to find the different classes and
  enumerators.

**Breaking change**

With better pandas integration, we changed column headers for data frames. As
of v0.4, data frames have three column header levels for time series data:

 1. Curve name
 2. Instance or contract
 3. Scenario (ensemble)

We did this to better describe the data when converted from time series' to
pandas data frames. Refer to the chapter on pandas integration for more
details.


0.3
---

Introducing support for OHLC data (open, high, low, close).

**Improvements**

- Implement operations in the OHLC API: ``load()``, ``latest()``.
  ``load_delivery_as_timeseries()``, and ``load_front_as_timeseries()``
- Add data and metadata classes for OHLC: ``OHLCField``, ``ContractPeriod``,
  ``Product``, ``OHLC``, ``OHLCList``, and ``Contract``.
- Add member ``Series#contract``, which is a reference to a set by the
  ``load_*_as_timeseries()``-operations.
- Add documentation for OHLC.
- Add new curve data type: ``DataType.SCENARIO``.

**Bugfixes**

- Fix runtime error in ``Series#name()`` (``Series`` is superclass of
  ``Timeseries`` and ``Periodseries``).
- ``ValidationError`` exceptions occuring on the server-side didn't include
  which parameter that failed due to a bug in the JSON error message parser.


0.2
---

A small release with two improvements.

**Improvements**

- Add ``Periodseries#print()`` method.
- Increase 1-10 days-ahead constraints for relative queries to 0-10000.


0.1
---

The first public release of Energy Quantified's Python client. *Woho!*

**Improvements**

- Add utilities for working with date-times, frequencies, timezones and
  resolutions.
- Add metadata classes for areas, curves, instances, places and more.
- Add classes for time series and period-based series.
- Add wrapper around requests with rate-limiting, auto-retry on failure
  and authentication.
- Implement APIs for metadata, timeseries, instances, periods and
  period-instances.
- Add support for timeseries-to-pandas conversion.
- Add meaningful exceptions.
- Add a few examples to the git repo.
- Write tons of documentation.

**Dependencies**

- Add ``pytz``, ``tzlocal``, ``python-dateutil``, ``requests``.
- Not adding ``pandas``, as it is optional.

**Bugfixes**

- (None in this release, but probably introduced some!)
