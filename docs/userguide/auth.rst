Authentication
==============

Get your API key from **Settings – API key** on the Energy Quantified
web application.

There are two ways to provide your API key to the API client:

Provide API key in code
-----------------------

Import the library, create a client and supply the API key. The actual API
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
parameter called **api_key_file**. Make sure to provide the full path,
or the relative path to the directory where you run your program from:

   >>> from energyquantified import EnergyQuantified
   >>> eq = EnergyQuantified(api_key_file='eq_api_key.txt')

The last line above should fail with an exception if it cannot find or
read the file, or if the file is empty.

-----

Next step
^^^^^^^^^

See how to :doc:`discover data <../userguide/metadata>`.
