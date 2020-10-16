Changelog
=========

0.3-dev
-------

Introducing support for OHLC data (open, high, low, close).

**Improvements**

- Implement operations in the OHLC API: ``latest()``. ``load()``,
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
