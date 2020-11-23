Changelog
=========


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

- Add utilities for working with date-times, frequencies, time-zones and
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
