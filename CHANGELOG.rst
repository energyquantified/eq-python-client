Changelog
=========

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
