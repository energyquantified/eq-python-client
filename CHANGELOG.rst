Changelog
=========

dev
---

**Improvements**

- Minor improvements in the documentation for relative forecasts
- Update supported Python versions in the documentation to 3.10+


0.14.7
------

**Bugfixes**

- Set ``price_area=True`` for area ``XK``


0.14.6
------

**Bugfixes**

- Patch ``PeriodSeries.to_timeseries()`` due to a regression with iterator behaviour in Python versions >=3.13.1, <3.13.4


0.14.5
------

**Improvements**

- Add ``__len__()`` method to ``Timeseries`` and ``PeriodSeries`` classes. This
  allows users to use the built-in ``len()`` function to get the number of
  values in a time series or period-based series.

**Bugfixes**

- Fix a bug in ``PeriodSeries.to_timeseries()`` that caused a crash for python
  version 3.13 and above. Thank you to @igramatk for reporting this issue.

**Deprecations**

- Deprecate method parameter ``exlude_tags`` and add ``exclude_tags`` as method parameter
  - Deprecated parameter will be removed in the next major release
  - Affected methods:
    - ``eq.instances.list()``
    - ``eq.instances.load()``
    - ``eq.period_instances.list()``
    - ``eq.period_instances.load()``


0.14.4
------

**Improvements**

- Lower the minimum supported ``front`` value for OHLC data from ``1`` to ``0``


0.14.3
------

**Improvements**

- Update the documentation with instance tag filtering in the push feed


0.14.2
------

**Improvements**

- Add ``tags`` and ``exclude_tags`` to curve event filters, for filtering
  events by instance tags


0.14.1
------

**Dependencies**

- Unpin ``websocket-client`` to allow for the latest version
  (until next major release)


0.14
----

**Improvements**

- Minor documentation improvements
- Added support for Polars data frames conversion
  - Introduced new methods: ``to_pl_df()`` and ``to_polars_dataframe()``
- Renamed Pandas data frame conversion methods for clarity and consistency
  - ``to_df()`` → ``to_pd_df()`` (old method deprecated)
  - ``to_dataframe()`` → ``to_pandas_dataframe()`` (old method deprecated)

**Bugfixes**

- Instances from ``eq.instances.list()`` previously had their ``issued`` time
  parsed in the UTC timezone. This has been fixed to be parsed in the curve's
  ``instance_issued_timezone`` if a curve *object* is provided to the method,
  otherwise (curve *name*) it will be parsed as a datetime with offset.


0.13.12
-------

**Improvements**

- Add parameters ``source`` and ``only_subscribed`` to ``eq.metadata.curves()``
  for filtering by source and subscribed curves, respectively.
- Update curve search documentation with examples on how to filter by source
  and subscribed curves.


0.13.11
-------

**Bugfixes**

- Fix typo in ``InstancesAPI.load()``


0.13.10
-------

**Improvements**

- Update border definitions


0.13.9
------

**Bugfixes**

- Fix a bug in ``TimeseriesList.to_df()`` sorting in the wrong order


0.13.8
------

**Dependencies**

- Upgrade ``python-dateutil`` latest from ``<=2.9`` to ``<2.10``


0.13.7
------

**Dependencies**

- Upgrade ``dateutil`` latest from 2.8 to 2.9


0.13.6
------

**Improvements**

- Add ``issued_time_of_day`` parameter to ``eq.instances.list()``,
  ``eq.instances.load()`` and ``eq.instances.latest()`` for filtering instances
  based on issued time


0.13.5
------

**Bugfixes**

- Adjust date formatting in ``AbsoluteResult.to_df()`` to be consistent with
  the rest of the client


0.13.4
------

**Improvements**

- Add ``AbsoluteResult.to_df()`` and ``AbsoluteResult.to_dataframe()``

**Bugfixes**

- The ``kind`` parameter on ``eq.metadata.places()`` did nothing. It is now fixed.


0.13.3
------

**Improvements**

- Modify the ``User-Agent`` header to comply with standard conventions


0.13.2
------

**Bugfixes**

- Fix deadlock in push feed preventing the client to resubscribe after recovery
  from a connection loss


0.13.1
------

**Improvements**

- Add new border:
   - ``DK1 – GB`` Explicit

**Bugfixes**

- Remove call to ``logging.basicConfig()`` in ``energyquantified/api/events.py``
  as it was causing issues with the logging configuration in the client's
  parent application


0.13
----

**Improvements**

- Parse Instance's ``created`` and ``modified`` in the Curve's time zone.
- Add ``eq.instances.rolling()`` for rolling forecasts


0.12.1
------

**Bugfixes**

- Remove code setting default log level to ``DEBUG``
- Fix a bug introduced in v0.12 that caused parsing of curve events to fail


0.12
----

**Improvements**

- Add ``PeriodInstancesAPI.relative()`` for relative queries
- Add ``modified-at-latest`` parameter for ``eq.instances.relative()``
- Implement absolute forecasts for instances ``eq.instances.absolute()``
- Add ``unit`` and ``denominator`` attributes to ``Series`` and ``OHLCList``
- Add support for unit conversion when loading data from the API
- Add ``curve_type`` parameter for ``eq.metadata.curves()``
- Add ``Subscription``, ``SubscriptionAccess``, ``SubscriptionType`` and
  ``SubscriptionCollectionPerm`` models
- Add ``Curve.subscription`` field, providing the user with subscription
  information for curves
- Add ``User``, ``Organization`` and ``AccountManager`` models
- Add ``UserAPI`` and ``eq.user.user()`` to get details of the current user

**Bugfixes**

- Remove unnecessary limitation from ``eq.instances.relative()`` for parameters
  ``time_of_day``, ``after_time_of_day`` and ``before_time_of_day``

**Breaking changes**

- Removed ``Place.area``. Use ``Place.areas`` instead.


0.11
----

**Improvements**

- Implement ``EventsAPI`` for streaming events from Energy Quantified's
  WebSocket API (push feed).
- Add timezone conversion.
- Add ``threshold`` parameter to define how many values are allowed to be
  missing while performing an aggregation.

**Dependencies**

- Add ``websocket-client`` v1.5.1
- Upgrade ``requests`` to minimum 2.31 due to security fixes


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
