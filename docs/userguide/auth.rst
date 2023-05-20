Authentication
==============

Get your API key from **Settings – API key** on the Energy Quantified
web application.

There are two ways to provide your API key to the API client:

Provide API key in code
-----------------------

Import :py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`
from the library, create a client and supply the API key. The actual API
key is longer than the one provided in this example:

   >>> from energyquantified import EnergyQuantified
   >>> eq = EnergyQuantified(api_key='aaaa-bbbb-cccc-dddd')

*(Optional)* You may check whether or not the API key is valid like so:

   >>> eq.is_api_key_valid()
   True

Load API key from file
----------------------

Create a new text file, let's call it ``eq_api_key.txt`` in this example,
and write the API key to it:

 .. code-block::

   aaaa-bbbb-cccc-dddd

Then you can initialize the client like and provide the API key with a
parameter called **api_key_file**. Make sure to provide the full path
or the relative path to the directory where you run your program from:

   >>> from energyquantified import EnergyQuantified
   >>> eq = EnergyQuantified(api_key_file='eq_api_key.txt')

The last line above should fail with an error if it cannot find or
read the file or if the file is empty.

Once you've authenticated, move on to the next step on how to
:doc:`discover data <../userguide/metadata>`.

-----

.. _realto-authentication:

Authentication for Realto users
-------------------------------

Those who subscribe to Energy Quantified's API via the Realto marketplace
must initialize the client using a
:py:class:`RealtoConnection <energyquantified.RealtoConnection>` class.
This class makes sure the requests are sent to Realto's proxy servers
and that the API key is provided in the HTTP header Realto requires you
to use.

Import class :py:class:`RealtoConnection <energyquantified.RealtoConnection>`
from the library, create a client and supply the details needed to connect
to the Realto API. Notice that you must specify both an ``api_url`` and an
``api_key``:

   >>> from energyquantified import RealtoConnection
   >>> eq = RealtoConnection(
   >>>     api_url=RealtoConnection.API_URL_GERMANY,
   >>>     api_key='abcdefghijklmnopqrstuvw'  # Supply your API key
   >>> )

You can also store your API key in a file like you can with the default
Energy Quantified client:

   >>> from energyquantified import RealtoConnection
   >>> eq = RealtoConnection(
   >>>     api_url=RealtoConnection.API_URL_GERMANY,
   >>>     api_key_file='realto_api_key.txt'  # A file with API key
   >>> )

Each country is set up as a different API on Realto's marketplace. As of this
writing, the available products are:

.. code-block::

   RealtoConnection.API_URL_GERMANY
   RealtoConnection.API_URL_FRANCE
   RealtoConnection.API_URL_NETHERLANDS
   RealtoConnection.API_URL_UK
   RealtoConnection.API_URL_BELGIUM

These variables are nothing else than strings of the base URL for the specific
API on Realto:

>>> RealtoConnection.API_URL_GERMANY
'https://api.realto.io/energyquantified-germany'

So if Energy Quantified adds more products to the Realto marketplace — but
hasn't updated the client yet — you can set the ``api_url`` parameter to the
base URL of those API's.

-----

Proxies
----------------------

If you need to use a proxy, it can be configured for the entire session in both
:py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`
and :py:class:`RealtoConnection <energyquantified.RealtoConnection>` by providing
the ``proxies`` parameter with a dictionary of proxies.

Example with :py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`:

   >>> from energyquantified import EnergyQuantified
   >>> proxies = {
   >>>     'http': 'http://10.10.1.10:3128',
   >>>     'https': 'http://10.10.1.10:1080',
   >>> }
   >>> eq = EnergyQuantified(
   >>>     api_key='aaaa-bbbb-cccc-dddd',
   >>>     proxies=proxies, # Supply proxies here
   >>> )

Example with :py:class:`RealtoConnection <energyquantified.RealtoConnection>`:

   >>> from energyquantified import RealtoConnection
   >>> proxies = {
   >>>     'http': 'http://10.10.1.10:3128',
   >>>     'https': 'http://10.10.1.10:1080',
   >>> }
   >>> eq = RealtoConnection(
   >>>     api_url=RealtoConnection.API_URL_GERMANY,
   >>>     api_key='abcdefghijklmnopqrstuvw',
   >>>     proxies=proxies,  # Supply proxies here
   >>> )

Since the ``requests`` library is used internally in
:py:class:`EnergyQuantified <energyquantified.EnergyQuantified>` and
:py:class:`RealtoConnection <energyquantified.RealtoConnection>`, refer to
the `proxies section <https://requests.readthedocs.io/en/latest/user/advanced/#proxies>`_
in their documentation.

-----

Next step
---------

See how to :doc:`discover data <../userguide/metadata>`.
