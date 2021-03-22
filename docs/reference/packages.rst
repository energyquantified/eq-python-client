Packages
========

This page lists note-worthy classes and data models.

``energyquantified``
--------------------

The top-level package with the main class:

 * :py:class:`EnergyQuantified <energyquantified.EnergyQuantified>`: The client
   class. Use this class to initialize the client with an API key and
   to access API operations.

There is also additional class available here:

 * :py:class:`RealtoConnection <energyquantified.RealtoConnection>`: An
   alternative client class for Realto users. Use this class to connect
   to the API via a Realto subscription.

``energyquantified.data``
-------------------------

Where the time series, period-based series and OHLC data models are
implemented:

 * :py:class:`Timeseries <energyquantified.data.Timeseries>`: The time series
   data model. A time series is more or less a series of values. There are
   three different value types:

    * :py:class:`Value <energyquantified.data.Value>`
    * :py:class:`ScenariosValue <energyquantified.data.ScenariosValue>`
    * :py:class:`MeanScenariosValue <energyquantified.data.MeanScenariosValue>`

 * :py:class:`TimeseriesList <energyquantified.data.TimeseriesList>`: A list
   of time series objects.

 * :py:class:`Periodseries <energyquantified.data.Periodseries>`: The
   period-based series data model. It has two different period types:

    * :py:class:`Period <energyquantified.data.Period>`
    * :py:class:`CapacityPeriod <energyquantified.data.CapacityPeriod>`

 * :py:class:`OHLC <energyquantified.data.OHLC>`: A data class for a single
   OHLC. OHLC objects has a reference to:

    * :py:class:`Product <energyquantified.data.Product>`: A description of a
      traded product (future contract).

 * :py:class:`OHLCList <energyquantified.data.OHLCList>`: A list of OHLC data
   objects.

 * :py:class:`SRMC <energyquantified.data.SRMC>`: The server response from
   an short-run marginal cost (SRMC) calculation. It has multiple attributes,
   most are defined and used elsewhere. But it has one that is specific for
   SRMC:

    * :py:class:`SRMCOptions <energyquantified.data.SRMCOptions>`: A data
      class holding all factors used in an SRMC calculation.

``energyquantified.metadata``
-----------------------------

Metadata classes are data classes with constants, such as enumerators. There
are quite many classes in ``energyquantified.metadata``:

 * These two enumerators are useful for aggregation:

    * :py:class:`Aggregation <energyquantified.metadata.Aggregation>`:
      Aggregetion methods such as mean, max, min, and so forth.
    * :py:class:`Filter <energyquantified.metadata.Filter>`: Enumerator of
      filters for electricity futures products such as base, peak.

 * :py:class:`Area <energyquantified.metadata.Area>`: Representing a price
   area (or country). An area has a set of exchange
   :py:class:`Border <energyquantified.metadata.Border>` with some capacity
   :py:class:`Allocation <energyquantified.metadata.Allocation>`.

 * :py:class:`Curve <energyquantified.metadata.Curve>`: The identifier of any
   data series on Energy Quantified. Curves have a
   :py:class:`CurveType <energyquantified.metadata.CurveType>` to define its
   storage types (time series, instance, period-based, OHLC) and
   :py:class:`DataType <energyquantified.metadata.DataType>` for its data type
   (forecast, normal, actual, etc.)

 * :py:class:`Instance <energyquantified.metadata.Instance>`: The identifier of
   any instance (forecasts, mostly).

 * :py:class:`Place <energyquantified.metadata.Place>`: An identifier of
   anything with a geographical location, such as a powerplant, a large
   consumer, a location on a river. See
   :py:class:`PlaceType <energyquantified.metadata.PlaceType>` for all types.

 * :py:class:`OHLCField <energyquantified.metadata.OHLCField>`: Enumerator of
   fields in OHLC data objects.

 * :py:class:`ContractPeriod <energyquantified.metadata.ContractPeriod>`:
   Enumerator of contract periods for OHLC data objects. Typically week, month,
   quarter, year.

``energyquantified.time``
-------------------------

Date and time utilities.

 * :py:class:`Resolution <energyquantified.time.Resolution>`: A combination of
   a frequency and a time zone. It has utility methods for stepping forward and
   backward in a given interval.

 * :py:class:`Frequency <energyquantified.time.Frequency>`: Enumerator of
   supported frequencies on Energy Quantified. Mostly used for aggregations
   and in combination with resolutions.

 * Commonly used time zones in the European power markets:

    * :py:class:`UTC <energyquantified.time.UTC>` – Universal Time
    * :py:class:`CET <energyquantified.time.CET>` – Central European Time
    * :py:class:`EET <energyquantified.time.EET>` – Eastern European Time
    * :py:class:`WET <energyquantified.time.WET>` – Western European Time
    * :py:class:`TRT <energyquantified.time.TRT>` – Turkish Time

 * :py:meth:`local_tz() <energyquantified.time.local_tz>`: Get your the local
   time zone on your workstation.

 * Useful functions to get dates and date-times:

    * :py:meth:`now() <energyquantified.time.now>`: Get a time zone aware
      date-time of the current time.
    * :py:meth:`today() <energyquantified.time.today>`: Get a time zone aware
      date-time of the today at midnight.
    * :py:meth:`to_timezone() <energyquantified.time.to_timezone>`: Convert a
      date-time to given time zone.
    * :py:meth:`get_date() <energyquantified.time.get_date>`: Create a date
      with sensible defaults.
    * :py:meth:`get_datetime() <energyquantified.time.get_datetime>`: Create a
      date-time with sensible defaults.

``energyquantified.utils``
--------------------------

Most utilities are internals, but there is one public-facing class in utils:

 * :py:class:`Page <energyquantified.utils.Page>`: An immutable list with
   paging support. Typically used by the metadata APIs to browse "pages" when
   searching for curves and places.

``energyquantified.exceptions``
-------------------------------

All exceptions are defined in this package.

 * :py:class:`APIError <energyquantified.exceptions.APIError>`: Base exception
   for all API errors. It's subclasses are:

    * :py:class:`HTTPError <energyquantified.exceptions.HTTPError>`
    * :py:class:`ValidationError <energyquantified.exceptions.ValidationError>`
    * :py:class:`NotFoundError <energyquantified.exceptions.NotFoundError>`
    * :py:class:`UnauthorizedError <energyquantified.exceptions.UnauthorizedError>`
    * :py:class:`ForbiddenError <energyquantified.exceptions.ForbiddenError>`
    * :py:class:`InternalServerError <energyquantified.exceptions.InternalServerError>`

 * :py:class:`InitializationError <energyquantified.exceptions.InitializationError>`:
   Exception for when client initialization fails.

 * :py:class:`PageError <energyquantified.exceptions.PageError>`:
   Exception for paging failures (see Page).

 * :py:class:`ParseException <energyquantified.exceptions.ParseException>`:
   Exception for parsing errors on API responses.
