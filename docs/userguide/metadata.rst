Metadata
========

This page describes how to search for data in the API. All examples below
expects you to have an initialized instance of the client called ``eq``.

Operations described here are available under ``eq.metadata.*``.


Curve search
------------

Method reference: :py:meth:`eq.metadata.curves() <energyquantified.api.MetadataAPI.curves>`

The API allows you to query for :py:class:`Curve <energyquantified.metadata.Curve>`
objects in many ways. It is using the same operation as the data search on Energy
Quantified's web application.

The curve object includes a :py:class:`Subscription
<energyquantified.metadata.Subscription>` field that describes your access for
the given curve.

Searching for curves in the API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When looking for curves, specify ``q`` to do a free-text search:

   >>> eq.metadata.curves(q='nuclear germany forecast')
   [<Curve: "DE Nuclear Production MWh/h 15min Forecast", curve_type=INSTANCE>]

You may filter on attributes:

   >>> from energyquantified.metadata import Area, DataType
   >>> eq.metadata.curves(
   >>>    area=Area.DE,
   >>>    data_type=DataType.FORECAST,
   >>>    category=['nuclear', 'production']
   >>> )
   [<Curve: "DE Nuclear Production MWh/h 15min Forecast", curve_type=INSTANCE>]

Or you can specify ``area`` and ``data_type`` as strings:

   >>> eq.metadata.curves(
   >>>    area='DE',
   >>>    data_type='FORECAST',
   >>>    category=['nuclear', 'production']
   >>> )
   [<Curve: "DE Nuclear Production MWh/h 15min Forecast", curve_type=INSTANCE>]

See :meth:`energyquantified.api.MetadataAPI.curves` for a full reference.

Pagination
^^^^^^^^^^

The curve search returns as a ``Page`` type, which is similar to Python
``list`` – but with extra flavour. Let's do a curve search that returns
many curves:

    >>> page1 = eq.metadata.curves(area=Area.DE, page_size=10)
    >>> page1.total_items
    607
    >>> page1.total_pages
    61
    >>> page1.page
    1
    >>> page1.page_size
    10

You can now go to the next page and previous page like so:

    >>> page2 = page1.get_next_page()
    >>> page1 = page2.get_previous_page()

You can, of course, also return a specific page directly when searching:

    >>> page61 = eq.metadata.curves(area=Area.DE, page_size=10, page=61)
    >>> page61
    [<Curve: "CZ>DE Exchange Net Transfer Capacity MW 15min REMIT", curve_type=TIMESERIES>,
     <Curve: "DE @Goldisthal Hydro Pumped-storage Capacity Available MW REMIT", curve_type=INSTANCE_PERIOD>,
     <Curve: "DE @Mainz-3 Natural Gas Power Capacity Available MW REMIT", curve_type=INSTANCE_PERIOD>,
     <Curve: "DE @Weisweiler-F Lignite Power Production MWh/h H Actual", curve_type=TIMESERIES>,
     <Curve: "DE @Weser-Porta River Temperature °C H Actual", curve_type=TIMESERIES>,
     <Curve: "DE Hydro Snow-and-Groundwater MWh D Normal", curve_type=TIMESERIES>,
     <Curve: "DE Nuclear Capacity Available MW REMIT", curve_type=INSTANCE_PERIOD>]

Metadata is cached. So, if you try to load the same page twice, it is fetched
from the cache, and thus not hitting the server.


Look up a curve name
--------------------

Method reference: :py:meth:`eq.metadata.curve() <energyquantified.api.MetadataAPI.curve>`

When you know the name of a curve and want to load the corresponding
:py:class:`Curve <energyquantified.metadata.Curve>` instance, use the
:py:meth:`eq.metadata.curve() <energyquantified.api.MetadataAPI.curve>` method:

    >>> curve = eq.metadata.curve("CZ>DE Exchange Net Transfer Capacity MW 15min REMIT")
    >>> curve
    <Curve: "CZ>DE Exchange Net Transfer Capacity MW 15min REMIT", curve_type=TIMESERIES>

When you provide a name that does not exist, this method will throw a
:py:class:`NotFoundError <energyquantified.exceptions.NotFoundError>`. Below we try
to load an actual nuclear production curve for Norway. However, Norway does not have
nuclear production, so the curve does not exist:

    >>> curve = eq.metadata.curve("NO Nuclear Production MWh/h Actual")
    ...
    NotFoundError: Curve 'NO Nuclear Production MWh/h Actual' not found


Places
------

Method reference: :py:meth:`eq.metadata.places() <energyquantified.api.MetadataAPI.places>`

Similar to the curve search, you can look up places with a free-text search:

   >>> nuclear_powerplants = eq.metadata.places(q='nuclear germany')
   >>> nuclear_powerplants
   [<Place: key="pp-brokdorf", name="Brokdorf", kind=PRODUCER, fuels=['Nuclear'], location=[53.851095, 9.345944]>,
    <Place: key="pp-emsland", name="Emsland", kind=PRODUCER, fuels=['Nuclear'], location=[52.481878, 7.306658]>,
    <Place: key="pp-grohnde", name="Grohnde", kind=PRODUCER, fuels=['Nuclear'], location=[52.035641, 9.413497]>,
    ...

You can also filter by attributes:

   >>> eq.metadata.places(area=Area.DE, fuel='nuclear')
   [<Place: key="pp-brokdorf", name="Brokdorf", kind=PRODUCER, fuels=['Nuclear'], location=[53.851095, 9.345944]>,
    <Place: key="pp-emsland", name="Emsland", kind=PRODUCER, fuels=['Nuclear'], location=[52.481878, 7.306658]>,
    <Place: key="pp-grohnde", name="Grohnde", kind=PRODUCER, fuels=['Nuclear'], location=[52.035641, 9.413497]>,
    ...

Places are not very useful by themselves, but they have a list of all referenced
curves. Here you can see the actual production curve and the
REMIT capacity curve for the German nuclear powerplant Brokdorf:

   >>> brokdorf = nuclear_powerplants[0]
   >>> brokdorf.curves
   [<Curve: "DE @Brokdorf Nuclear Capacity Available MW REMIT", curve_type=INSTANCE_PERIOD>,
    <Curve: "DE @Brokdorf Nuclear Production MWh/h H Actual", curve_type=TIMESERIES>]

See :meth:`energyquantified.api.MetadataAPI.places` for a full reference.

Categories
----------

Method references:
:py:meth:`eq.metadata.categories() <energyquantified.api.MetadataAPI.categories>`
and
:py:meth:`eq.metadata.exact_categories() <energyquantified.api.MetadataAPI.exact_categories>`

Curve names are, among other attributes, built by combining categories. You
can list categories by using the `categories()`-method. It will
return a set of all available categories:

   >>> eq.metadata.categories()
   {'API-2',
    'Auction',
    'Available',
    'Base',
    'Bioenergy',
    'Biogas',
    'Biomass',
    'Brent',
    ...

Since curve names are the combination of these categories (such as
``Spot Price``, ``Wind Power Production`` etc.), there is also an
operation for listing all combinations of categories. Use the
``exact_categories()``-method to list these:

   >>> eq.metadata.exact_categories()
   {'Bioenergy Power Production',
    'Biogas Power Production',
    'Biomass Power Capacity Available',
    'Biomass Power Production',
    'CHP District-heating Power Production',
    'CHP Industry Power Production',
    'CHP Power Production',
    'Consumption',
    'Consumption Capacity Available',
    'Consumption Holiday-Reduction',
    'Consumption Index Chilling',
    'Consumption Index Cloudiness',
    ...

As with other metadata, the responses are cached.


-----

Next steps
----------

Learn how to load :doc:`time series <../userguide/timeseries>`,
:doc:`time series instances <../userguide/instances>`,
:doc:`period-based series <../userguide/periods>`, and
:doc:`period-based series instances <../userguide/period-instances>`.