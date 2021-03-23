Realto users
============

**Realto** runs an API marketplace for the digital exchange of energy data
and services. Energy Quantified has made its API available on their platform
for a few selected countries.

This page gives a short introduction on how to get started with Energy
Quantified's Python library for **Realto users**.

If you have an Energy Quantified user account, you should read the
:doc:`quickstart guide <quickstart>` instead.

-----

2-minute guide
^^^^^^^^^^^^^^

There are almost no differences in using the API directly from Energy Quantified
or through the Realto marketplace.

However, authentication works differently. Read
`Authentication for Realto users <../userguide/auth.html#realto-authentication>`__
to learn how to connect to the API with a Realto account.

Quickstart
~~~~~~~~~~

Read the :doc:`2-minute quickstart guide <quickstart>`, but follow the
instructions above on how to authenticate instead.

Differences for Realto users
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Energy Quantified API is split by country on Realto. So, you must specify
which country you would like to connect to when initializing the Python client.

A client authenticated to the German API on Realto will not be able to see
or download data for any other country. If you subscribe to multiple Energy
Quantified products on Realto, you can initialize one client per country:

>>> from energyquantified import RealtoConnection
>>> # Connect to the German data API
>>> eq_de = RealtoConnection(
>>>     api_url=RealtoConnection.API_URL_GERMANY,
>>>     api_key='abcdefghijklmnopqrstuvw'
>>> )
>>> # Connect to the French data API
>>> eq_fr = RealtoConnection(
>>>     api_url=RealtoConnection.API_URL_FRANCE,
>>>     api_key='abcdefghijklmnopqrstuvw'
>>> )

There are five countries available as of this writing:

.. code-block::

   RealtoConnection.API_URL_GERMANY
   RealtoConnection.API_URL_FRANCE
   RealtoConnection.API_URL_NETHERLANDS
   RealtoConnection.API_URL_UK
   RealtoConnection.API_URL_BELGIUM

These variables are strings of the base URL for the specific API on Realto:

>>> RealtoConnection.API_URL_GERMANY
'https://api.realto.io/energyquantified-germany'

So if Energy Quantified adds more products to the Realto marketplace – but
hasn't updated the client yet – you can set the ``api_url`` parameter to the
base URL of those API's.


What is available on Realto?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Operations for the following data types are enabled in the Realto integration:

 * :doc:`Time series <../userguide/timeseries>`
 * :doc:`Instances <../userguide/instances>` (forecasts)
 * :doc:`Period-based series <../userguide/timeseries>`
 * :doc:`Period-based instances <../userguide/timeseries>`

The `Curve search <../userguide/metadata.html#curve-search>`__
is also enabled, so that you can search for and discover data series. All
functions for converting API responses to ``pandas.DataFrame`` objects are
also working.

The API operations for OHLC data and SRMC calculations are unfortunately not
available to Realto users.


Next steps
^^^^^^^^^^

Then we recommend getting familiar with terminology and data types used in the
Energy Quantified API and in the Energy Quantified Python library:

- :doc:`Terminology and data models <../userguide/terminology>`
