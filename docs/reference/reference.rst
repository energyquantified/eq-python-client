.. _reference:

Full reference
==============

.. module:: energyquantified

This part of the documentation covers the public classes and methods
for Energy Quantified's Python library. All interaction with the API
happens through the :py:class:`energyquantified.EnergyQuantified` class:

The main client
---------------

.. autoclass:: energyquantified.EnergyQuantified
   :inherited-members:


API operations
--------------

The API operations are grouped into sections similar to the way the API
is organized. Each of those sections are implemented in their own class.

Here are the different API section classes:

------

.. autoclass:: energyquantified.api.MetadataAPI
   :inherited-members:

------

.. autoclass:: energyquantified.api.TimeseriesAPI
   :inherited-members:

------

.. autoclass:: energyquantified.api.InstancesAPI
   :inherited-members:

------

.. autoclass:: energyquantified.api.PeriodsAPI
   :inherited-members:

------

.. autoclass:: energyquantified.api.PeriodInstancesAPI
   :inherited-members:

------

.. autoclass:: energyquantified.api.OhlcAPI
   :inherited-members:


Data types
----------

There are three main groups of data types: Time series, period-based
series and OHLC data:


Time series classes
^^^^^^^^^^^^^^^^^^^

.. autoclass:: energyquantified.data.Timeseries
   :show-inheritance:
   :inherited-members:

-----

.. autoclass:: energyquantified.data.TimeseriesList
   :show-inheritance:
   :inherited-members:

------

.. autoclass:: energyquantified.data.ValueType
   :inherited-members:

------

.. autoclass:: energyquantified.data.Value

------

.. autoclass:: energyquantified.data.ScenariosValue

------

.. autoclass:: energyquantified.data.MeanScenariosValue


Period-based series classes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: energyquantified.data.Periodseries
   :show-inheritance:
   :inherited-members:

-----

.. autoclass:: energyquantified.data.PeriodseriesList
   :show-inheritance:
   :inherited-members:

------

.. autoclass:: energyquantified.data.Period

------

.. autoclass:: energyquantified.data.CapacityPeriod


Base class for series
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: energyquantified.data.base.Series
   :show-inheritance:
   :inherited-members:


OHLC data classes
^^^^^^^^^^^^^^^^^

.. autoclass:: energyquantified.data.Product
   :inherited-members:

------

.. autoclass:: energyquantified.data.OHLC
   :inherited-members:

------

.. autoclass:: energyquantified.data.OHLCList
   :show-inheritance:
   :members:


SRMC data classes
^^^^^^^^^^^^^^^^^

.. autoclass:: energyquantified.data.SRMC
   :show-inheritance:
   :inherited-members:

------

.. autoclass:: energyquantified.data.SRMCOptions
   :inherited-members:


Metadata
--------

.. autoclass:: energyquantified.metadata.Allocation
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.Area
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.Border
   :inherited-members:
   :special-members: __hash__, __eq__

------

.. autoclass:: energyquantified.metadata.Curve
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.CurveType
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.DataType
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.Instance
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.Place
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.PlaceType
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.Aggregation
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.Filter
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.ContractPeriod
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.OHLCField
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.ContinuousContract
   :inherited-members:

------

.. autoclass:: energyquantified.metadata.SpecificContract
   :inherited-members:


Date and time
-------------

.. autoclass:: energyquantified.time.Frequency
   :inherited-members:
   :special-members: __gt__, __lt__, __ge__, __le__

------

.. autoclass:: energyquantified.time.Resolution
   :inherited-members:
   :special-members: __rshift__, __lshift__

-----

**Methods** in ``energyquantified.time``. These methods are wrappers around the
default methods in Python's standard library and other libraries where the
time-zone is set to CET (which is used in the European power markets)
by default.

.. autofunction:: energyquantified.time.now
.. autofunction:: energyquantified.time.today
.. autofunction:: energyquantified.time.get_datetime
.. autofunction:: energyquantified.time.get_date
.. autofunction:: energyquantified.time.to_timezone
.. autofunction:: energyquantified.time.local_tz

-----

**Constants** in ``energyquantified.time``. These are the most commonly used
time-zones in the European power markets.

.. autodata:: energyquantified.time.UTC
.. autodata:: energyquantified.time.CET
.. autodata:: energyquantified.time.WET
.. autodata:: energyquantified.time.EET
.. autodata:: energyquantified.time.TRT
.. autodata:: energyquantified.time.DEFAULT_TZ

Utils
-----

.. autoclass:: energyquantified.utils.Page
   :show-inheritance:
   :inherited-members:

Exceptions
----------

Even though the exceptions below are listed with full path, they are exposed
in module ``energyquantified.exceptions``.

**API exceptions**

.. autoexception:: energyquantified.exceptions.APIError

------

.. autoexception:: energyquantified.exceptions.HTTPError

------

.. autoexception:: energyquantified.exceptions.ValidationError

------

.. autoexception:: energyquantified.exceptions.NotFoundError

------

.. autoexception:: energyquantified.exceptions.UnauthorizedError

------

.. autoexception:: energyquantified.exceptions.ForbiddenError

------

.. autoexception:: energyquantified.exceptions.InternalServerError

**Initialization errors**

.. autoexception:: energyquantified.exceptions.InitializationError

**Pagination exceptions**

.. autoexception:: energyquantified.exceptions.PageError

**Parser exceptions**

.. autoexception:: energyquantified.exceptions.ParseException
