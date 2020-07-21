.. Energy Quantified API Python library documentation documentation master file, created by
   sphinx-quickstart on Wed May 27 18:18:53 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Python client for Energy Quantified's Time Series API
=====================================================

Version: |version| (:doc:`Installation <intro/install>`)

The official Python library for `Energy Quantified <https://www.energyquantified.com>`_'s
Time Series API. It allows you to access thousands of data series directly from
Energy Quantified's time series database. It integrates with the popular
`pandas <https://pandas.pydata.org/docs/>`_ library for high-performance data
analysis and manipulation.

Developed for **Python 3.7+**.

Features
^^^^^^^^

- Simple authentication
- Metadata caching
- Rate-limiting and automatic retries on network errors
- Full-text search and keyword search for curves and powerplants
- Forecasts- and time series data
- Period-based data
- *(TODO)* OHLC data
- *(TODO)* SRMC, dark- and spark spreads
- *(TODO)* Shows your subscription for each series
- Support for time-zones, resolutions and aggregations
- Easy-to-use filters for issue dates and forecast types
- Integrates with pandas

**Note:** An user account is required to use this client. You can create
one on Energy Quantified's `home page <https://www.energyquantified.com>`_.


License
^^^^^^^

The Energy Quantified Python client is licensed under the
`Apache License version 2.0 <https://opensource.org/licenses/Apache-2.0>`_.


Getting started
^^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   intro/install
   intro/quickstart


The user guide
^^^^^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   userguide/terminology
   userguide/auth
   userguide/metadata
   userguide/timeseries
   userguide/instances
   userguide/periods
   userguide/period-instances


Other
^^^^^

.. toctree::
   :maxdepth: 2

   reference/reference
   reference/changelog


Indices and tables
^^^^^^^^^^^^^^^^^^

* :ref:`genindex`
* :ref:`search`
