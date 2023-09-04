Python client for Energy Quantified's Time Series API
=====================================================

Release |version| (:doc:`Installation <intro/install>`)

.. image:: https://img.shields.io/github/license/energyquantified/eq-python-client?style=flat
   :alt: Apache License version 2.0
.. image:: https://img.shields.io/pypi/pyversions/energyquantified?style=flat
   :alt: Python 3.7+
.. image:: https://img.shields.io/pypi/wheel/energyquantified?style=flat
   :alt: PyPI – Wheel

The official Python library for `Energy Quantified <https://www.energyquantified.com>`_'s
Time Series API. It allows you to access thousands of data series directly from
Energy Quantified's time series database. It integrates with the popular
`pandas <https://pandas.pydata.org/docs/>`_ library for high-performance data
analysis and manipulation.

Developed for **Python 3.7+**.

.. code-block:: python

   from datetime import date, timedelta
   from energyquantified import EnergyQuantified

   # Initialize client
   eq = EnergyQuantified(api_key='<insert api key here>')

   # Free-text search (filtering on attributes is also supported)
   curves = eq.metadata.curves(q='de wind production actual')

   # Load time series data
   curve = curves[0]
   timeseries = eq.timeseries.load(
       curve,
       begin=date.today() - timedelta(days=10),
       end=date.today()
   )

   # Convert to Pandas data frame
   df = timeseries.to_dataframe()


Features
^^^^^^^^

- Simple authentication
- Metadata caching
- Rate-limiting and automatic retries on network errors
- Full-text search and keyword search for curves and powerplants
- Forecasts- and time series data
- Period-based data
- OHLC data
- SRMC calculations on OHLC data
- *(TODO)* Shows your subscription for each series
- Support for timezones, resolutions and aggregations
- Easy-to-use filters for issue dates and forecast types
- Integrates with pandas

**Note:** A user account is required to use this client. You can create
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
   intro/quickstart-realto


User guide
^^^^^^^^^^

.. toctree::
   :maxdepth: 2

   userguide/terminology
   userguide/auth
   userguide/metadata
   userguide/timeseries
   userguide/instances
   userguide/periods
   userguide/period-instances
   userguide/ohlc
   userguide/srmc
   userguide/pandas
   userguide/push-feed


Reference
^^^^^^^^^

.. toctree::
   :maxdepth: 2

   reference/packages
   reference/reference


Other
^^^^^

.. toctree::
   :maxdepth: 2

   reference/changelog

Indices and tables
^^^^^^^^^^^^^^^^^^

* :ref:`genindex`
* :ref:`search`
