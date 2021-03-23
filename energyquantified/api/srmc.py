from .base import BaseAPI

from ..exceptions import ValidationError
from ..metadata import Curve, CurveType, OHLCField
from ..parser.srmc import parse_srmc_response


# Tuple of supported values for Curve.curve_type in the time series API
CURVE_TYPES = (CurveType.OHLC,)

class SrmcAPI(BaseAPI):
    """
    Operations for SRMC calculations in the API. Access these operations via
    an instance of the :py:class:`energyquantified.EnergyQuantified` class:

       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.srmc.load_front(curve, begin, end, period='month', front=1)
    """

    @staticmethod
    def _check_curve_category(curve):
        # Check that the curve has either 'gas' or 'coal' in its name
        if isinstance(curve, Curve):
            name = curve.name.lower()
            if not 'gas' in name and not 'coal' in name:
                raise ValidationError(
                    reason="Provide a coal or gas curve",
                    parameter="curve"
                )
        elif isinstance(curve, str):
            name = curve.lower()
            if not 'gas' in name and not 'coal' in name:
                raise ValidationError(
                    reason="Provide a coal or gas curve",
                    parameter="curve"
                )

    def load_front(
            self,
            curve,
            begin=None,
            end=None,
            period=None,
            front=None,
            gas_therm_to_mwh=None,
            api2_tonne_to_mwh=None,
            carbon_emissions=None,
            efficiency=None,
            carbon_tax_area=None):
        """
        Calculate historical short-run margincal costs (SRMC) for a
        continuous front contract.

        SRMC is calculated from a **coal** or **gas** curve of your choosing.
        It uses the daily reference rates from the European Central Bank (ECB)
        for currency conversions. The EUA price in the calculation is the
        settlement price from ICE.

        Some countries, such as Great Britain, has an additional flat tax on
        carbon emissions. Specify the ``carbon_tax_area`` parameter to apply
        tax rules for a specific country.

        This operation works for **coal** or **gas** curves with
        ``curve_type = OHLC`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date
        :type begin: date, str, required
        :param end: The end date
        :type end: date, str, required
        :param period: Filter on contract period (day, week, month etc.),\
            defaults to None
        :type period: ContractPeriod, str, required
        :param front: The front contract (1=front, 2=second front, etc.)
        :type front: int, required
        :param gas_therm_to_mwh: Conversion from pence/therm to GBP/MWh\
            (still in higher-heating value). Defaults to 0.029307.
        :type gas_therm_to_mwh: float, optional
        :param api2_tonne_to_mwh: Conversion from API2 coal to MWh.\
            Defaults to 6.978.
        :type api2_tonne_to_mwh: float, optional
        :param carbon_emissions: The carbon content as tCO2/MWh. This value\
            varies between coal and gas. For coal, the default factor is\
            0.34056. For gas, the default factor is 0.202.
        :type carbon_emissions: float, optional
        :param efficiency: The energy efficiency. For coal, the default\
            factor is 0.42. For gas, the default factor is 0.59.
        :type efficiency: float, optional
        :param carbon_tax_area: Set an area to apply tax rules for.
        :type carbon_tax_area: Area, str, optional
        :return: An SRMC object with a list of OHLC objects
        :rtype: :py:class:`energyquantified.data.SRMC`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        self._check_curve_category(curve)
        url = f"/srmc/{safe_curve}/"
        # Parameters
        params = {}
        self._add_date(params, "begin", begin, required=True)
        self._add_date(params, "end", end, required=True)
        self._add_contract_period(params, "period", period, required=True)
        self._add_int(params, "front", front, min=1, required=True)
        self._add_number(params, "gas-therm-to-mwh", gas_therm_to_mwh)
        self._add_number(params, "api2-tonne-to-mwh", api2_tonne_to_mwh)
        self._add_number(params, "carbon-emissions", carbon_emissions, min=0.01, max=1.0)
        self._add_number(params, "efficiency", efficiency, min=0.01, max=1.0)
        self._add_area(params, "carbon-tax-area", carbon_tax_area)
        # HTTP request
        response = self._get(url, params=params)
        return parse_srmc_response(response.json())

    def load_delivery(
            self,
            curve,
            begin=None,
            end=None,
            period=None,
            delivery=None,
            gas_therm_to_mwh=None,
            api2_tonne_to_mwh=None,
            carbon_emissions=None,
            efficiency=None,
            carbon_tax_area=None):
        """
        Calculate historical short-run margincal costs (SRMC) for a specific
        contract, such as the year 2021, the month Jan 2021, etc.

        SRMC is calculated from a **coal** or **gas** curve of your choosing.
        It uses the daily reference rates from the European Central Bank (ECB)
        for currency conversions. The EUA price in the calculation is the
        settlement price from ICE.

        Some countries, such as Great Britain, has an additional flat tax on
        carbon emissions. Specify the ``carbon_tax_area`` parameter to apply
        tax rules for a specific country.

        This operation works for **coal** or **gas** curves with
        ``curve_type = OHLC`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date
        :type begin: date, str, required
        :param end: The end date
        :type end: date, str, required
        :param period: Filter on contract period (day, week, month etc.),\
            defaults to None
        :type period: ContractPeriod, str, required
        :param delivery: Filter on delivery date, requires parameter ``period``\
            to be set; cannot be used together with ``front``, defaults to None
        :type delivery: date, str, required
        :param gas_therm_to_mwh: Conversion from pence/therm to GBP/MWh\
            (still in higher-heating value). Defaults to 0.029307.
        :type gas_therm_to_mwh: float, optional
        :param api2_tonne_to_mwh: Conversion from API2 coal to MWh.\
            Defaults to 6.978.
        :type api2_tonne_to_mwh: float, optional
        :param carbon_emissions: The carbon content as tCO2/MWh. This value\
            varies between coal and gas. For coal, the default factor is\
            0.34056. For gas, the default factor is 0.202.
        :type carbon_emissions: float, optional
        :param efficiency: The energy efficiency. For coal, the default\
            factor is 0.42. For gas, the default factor is 0.59.
        :type efficiency: float, optional
        :param carbon_tax_area: Set an area to apply tax rules for.
        :type carbon_tax_area: Area, str, optional
        :return: An SRMC object with a list of OHLC objects
        :rtype: :py:class:`energyquantified.data.SRMC`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        self._check_curve_category(curve)
        url = f"/srmc/{safe_curve}/"
        # Parameters
        params = {}
        self._add_date(params, "begin", begin, required=True)
        self._add_date(params, "end", end, required=True)
        self._add_contract_period(params, "period", period, required=True)
        self._add_date(params, "delivery", delivery, required=True)
        self._add_number(params, "gas-therm-to-mwh", gas_therm_to_mwh)
        self._add_number(params, "api2-tonne-to-mwh", api2_tonne_to_mwh)
        self._add_number(params, "carbon-emissions", carbon_emissions, min=0.01, max=1.0)
        self._add_number(params, "efficiency", efficiency, min=0.01, max=1.0)
        self._add_area(params, "carbon-tax-area", carbon_tax_area)
        # HTTP request
        response = self._get(url, params=params)
        return parse_srmc_response(response.json())

    def load_front_as_timeseries(
            self,
            curve,
            begin=None,
            end=None,
            frequency=None,
            period=None,
            front=None,
            fill=None,
            gas_therm_to_mwh=None,
            api2_tonne_to_mwh=None,
            carbon_emissions=None,
            efficiency=None,
            carbon_tax_area=None):
        """
        Calculate historical short-run margincal costs (SRMC) for a continuous
        front contract and convert the result to a daily time series.

        SRMC is calculated from a **coal** or **gas** curve of your choosing.
        It uses the daily reference rates from the European Central Bank (ECB)
        for currency conversions. The EUA price in the calculation is the
        settlement price from ICE.

        Some countries, such as Great Britain, has an additional flat tax on
        carbon emissions. Specify the ``carbon_tax_area`` parameter to apply
        tax rules for a specific country.

        This operation works for **coal** or **gas** curves with
        ``curve_type = OHLC`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date
        :type begin: date, str, required
        :param end: The end date
        :type end: date, str, required
        :param period: Filter on contract period (day, week, month etc.),\
            defaults to None
        :type period: ContractPeriod, str, required
        :param front: The front contract (1=front, 2=second front, etc.)
        :type front: int, required
        :param fill: How to handle days without trades. Allowed values are:\
            ``no-fill`` do nothing, ``fill-holes`` fill in holes with data\
            from previous trading day, ``forward-fill`` fill in all blanks\
            with data from the previous trading day (also into the future).\
            Defaults to ``no-fill``.
        :type fill: str, optional
        :param gas_therm_to_mwh: Conversion from pence/therm to GBP/MWh\
            (still in higher-heating value). Defaults to 0.029307.
        :type gas_therm_to_mwh: float, optional
        :param api2_tonne_to_mwh: Conversion from API2 coal to MWh.\
            Defaults to 6.978.
        :type api2_tonne_to_mwh: float, optional
        :param carbon_emissions: The carbon content as tCO2/MWh. This value\
            varies between coal and gas. For coal, the default factor is\
            0.34056. For gas, the default factor is 0.202.
        :type carbon_emissions: float, optional
        :param efficiency: The energy efficiency. For coal, the default\
            factor is 0.42. For gas, the default factor is 0.59.
        :type efficiency: float, optional
        :param carbon_tax_area: Set an area to apply tax rules for.
        :type carbon_tax_area: Area, str, optional
        :return: An SRMC object with a ``timeseries`` object
        :rtype: :py:class:`energyquantified.data.SRMC`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        self._check_curve_category(curve)
        url = f"/srmc/{safe_curve}/timeseries/"
        # Parameters
        params = {}
        self._add_date(params, "begin", begin, required=True)
        self._add_date(params, "end", end, required=True)
        self._add_contract_period(params, "period", period, required=True)
        self._add_int(params, "front", front, min=1, required=True)
        self._add_fill(params, "fill", fill)
        self._add_number(params, "gas-therm-to-mwh", gas_therm_to_mwh)
        self._add_number(params, "api2-tonne-to-mwh", api2_tonne_to_mwh)
        self._add_number(params, "carbon-emissions", carbon_emissions, min=0.01, max=1.0)
        self._add_number(params, "efficiency", efficiency, min=0.01, max=1.0)
        self._add_area(params, "carbon-tax-area", carbon_tax_area)
        # HTTP request
        response = self._get(url, params=params)
        return parse_srmc_response(response.json())

    def load_delivery_as_timeseries(
            self,
            curve,
            begin=None,
            end=None,
            period=None,
            delivery=None,
            fill=None,
            gas_therm_to_mwh=None,
            api2_tonne_to_mwh=None,
            carbon_emissions=None,
            efficiency=None,
            carbon_tax_area=None):
        """
        Calculate historical short-run margincal costs (SRMC) for a specific
        contract and convert it to a daily time series.

        A specific contract could be the year 2021, the month Jan 2021, etc.

        SRMC is calculated from a **coal** or **gas** curve of your choosing.
        It uses the daily reference rates from the European Central Bank (ECB)
        for currency conversions. The EUA price in the calculation is the
        settlement price from ICE.

        Some countries, such as Great Britain, has an additional flat tax on
        carbon emissions. Specify the ``carbon_tax_area`` parameter to apply
        tax rules for a specific country.

        This operation works for **coal** or **gas** curves with
        ``curve_type = OHLC`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin date
        :type begin: date, str, required
        :param end: The end date
        :type end: date, str, required
        :param period: Filter on contract period (day, week, month etc.),\
            defaults to None
        :type period: ContractPeriod, str, required
        :param delivery: Filter on delivery date, requires parameter ``period``\
            to be set; cannot be used together with ``front``, defaults to None
        :type delivery: date, str, required
        :param fill: How to handle days without trades. Allowed values are:\
            ``no-fill`` do nothing, ``fill-holes`` fill in holes with data\
            from previous trading day, ``forward-fill`` fill in all blanks\
            with data from the previous trading day (also into the future).\
            Defaults to ``no-fill``.
        :type fill: str, optional
        :param gas_therm_to_mwh: Conversion from pence/therm to GBP/MWh\
            (still in higher-heating value). Defaults to 0.029307.
        :type gas_therm_to_mwh: float, optional
        :param api2_tonne_to_mwh: Conversion from API2 coal to MWh.\
            Defaults to 6.978.
        :type api2_tonne_to_mwh: float, optional
        :param carbon_emissions: The carbon content as tCO2/MWh. This value\
            varies between coal and gas. For coal, the default factor is\
            0.34056. For gas, the default factor is 0.202.
        :type carbon_emissions: float, optional
        :param efficiency: The energy efficiency. For coal, the default\
            factor is 0.42. For gas, the default factor is 0.59.
        :type efficiency: float, optional
        :param carbon_tax_area: Set an area to apply tax rules for.
        :type carbon_tax_area: Area, str, optional
        :return: An SRMC object with a ``timeseries`` object
        :rtype: :py:class:`energyquantified.data.SRMC`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        self._check_curve_category(curve)
        url = f"/srmc/{safe_curve}/timeseries/"
        # Parameters
        params = {}
        self._add_date(params, "begin", begin, required=True)
        self._add_date(params, "end", end, required=True)
        self._add_contract_period(params, "period", period, required=True)
        self._add_date(params, "delivery", delivery, required=True)
        self._add_fill(params, "fill", fill)
        self._add_number(params, "gas-therm-to-mwh", gas_therm_to_mwh)
        self._add_number(params, "api2-tonne-to-mwh", api2_tonne_to_mwh)
        self._add_number(params, "carbon-emissions", carbon_emissions, min=0.01, max=1.0)
        self._add_number(params, "efficiency", efficiency, min=0.01, max=1.0)
        self._add_area(params, "carbon-tax-area", carbon_tax_area)
        # HTTP request
        response = self._get(url, params=params)
        return parse_srmc_response(response.json())

    def latest(
            self,
            curve,
            date=None,
            gas_therm_to_mwh=None,
            api2_tonne_to_mwh=None,
            carbon_emissions=None,
            efficiency=None,
            carbon_tax_area=None):
        """
        Calculate short-run margincal costs (SRMC) for all settlement prices
        from a trading day. Defaults to using OHLC data from the latest
        available trading day, hence ``latest()``.

        If ``date`` is given, this method will try to fetch OHLC data for
        that trading day. When there is no data for the given day, OHLC data
        will be loaded for the closest trading day earlier in time with data.

        SRMC is calculated from a **coal** or **gas** curve of your choosing.
        It uses the daily reference rates from the European Central Bank (ECB)
        for currency conversions. The EUA price in the calculation is the
        settlement price from ICE.

        Some countries, such as Great Britain, has an additional flat tax on
        carbon emissions. Specify the ``carbon_tax_area`` parameter to apply
        tax rules for a specific country.

        This operation works for **coal** or **gas** curves with
        ``curve_type = OHLC`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param date: The trading date, defaults to today
        :type date: date, str, required
        :param gas_therm_to_mwh: Conversion from pence/therm to GBP/MWh\
            (still in higher-heating value). Defaults to 0.029307.
        :type gas_therm_to_mwh: float, optional
        :param api2_tonne_to_mwh: Conversion from API2 coal to MWh.\
            Defaults to 6.978.
        :type api2_tonne_to_mwh: float, optional
        :param carbon_emissions: The carbon content as tCO2/MWh. This value\
            varies between coal and gas. For coal, the default factor is\
            0.34056. For gas, the default factor is 0.202.
        :type carbon_emissions: float, optional
        :param efficiency: The energy efficiency. For coal, the default\
            factor is 0.42. For gas, the default factor is 0.59.
        :type efficiency: float, optional
        :param carbon_tax_area: Set an area to apply tax rules for.
        :type carbon_tax_area: Area, str, optional
        :return: An SRMC object with a list of OHLC objects
        :rtype: :py:class:`energyquantified.data.SRMC`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        self._check_curve_category(curve)
        url = f"/srmc/{safe_curve}/latest/"
        # Parameters
        params = {}
        self._add_date(params, "date", date)
        self._add_number(params, "gas-therm-to-mwh", gas_therm_to_mwh)
        self._add_number(params, "api2-tonne-to-mwh", api2_tonne_to_mwh)
        self._add_number(params, "carbon-emissions", carbon_emissions, min=0.01, max=1.0)
        self._add_number(params, "efficiency", efficiency, min=0.01, max=1.0)
        self._add_area(params, "carbon-tax-area", carbon_tax_area)
        # HTTP request
        response = self._get(url, params=params)
        return parse_srmc_response(response.json())

    def latest_as_periods(
            self,
            curve,
            date=None,
            gas_therm_to_mwh=None,
            api2_tonne_to_mwh=None,
            carbon_emissions=None,
            efficiency=None,
            carbon_tax_area=None):
        """
        Calculate short-run margincal costs (SRMC) for all settlement prices
        from a trading day, sort them, and merge/convert them to a continuous
        series.

        Defaults to using OHLC data from the latest available trading day,
        hence ``latest`` in the method name.

        If ``date`` is given, this method will try to fetch OHLC data for
        that trading day. When there is no data for the given day, OHLC data
        will be loaded for the closest trading day earlier in time with data.

        SRMC is calculated from a **coal** or **gas** curve of your choosing.
        It uses the daily reference rates from the European Central Bank (ECB)
        for currency conversions. The EUA price in the calculation is the
        settlement price from ICE.

        Some countries, such as Great Britain, has an additional flat tax on
        carbon emissions. Specify the ``carbon_tax_area`` parameter to apply
        tax rules for a specific country.

        This operation works for **coal** or **gas** curves with
        ``curve_type = OHLC`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param date: The trading date, defaults to today
        :type date: date, str, required
        :param gas_therm_to_mwh: Conversion from pence/therm to GBP/MWh\
            (still in higher-heating value). Defaults to 0.029307.
        :type gas_therm_to_mwh: float, optional
        :param api2_tonne_to_mwh: Conversion from API2 coal to MWh.\
            Defaults to 6.978.
        :type api2_tonne_to_mwh: float, optional
        :param carbon_emissions: The carbon content as tCO2/MWh. This value\
            varies between coal and gas. For coal, the default factor is\
            0.34056. For gas, the default factor is 0.202.
        :type carbon_emissions: float, optional
        :param efficiency: The energy efficiency. For coal, the default\
            factor is 0.42. For gas, the default factor is 0.59.
        :type efficiency: float, optional
        :param carbon_tax_area: Set an area to apply tax rules for.
        :type carbon_tax_area: Area, str, optional
        :return: An SRMC object with a period-based series
        :rtype: :py:class:`energyquantified.data.SRMC`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        self._check_curve_category(curve)
        url = f"/srmc/{safe_curve}/latest/periods/"
        # Parameters
        params = {}
        self._add_date(params, "date", date)
        self._add_number(params, "gas-therm-to-mwh", gas_therm_to_mwh)
        self._add_number(params, "api2-tonne-to-mwh", api2_tonne_to_mwh)
        self._add_number(params, "carbon-emissions", carbon_emissions, min=0.01, max=1.0)
        self._add_number(params, "efficiency", efficiency, min=0.01, max=1.0)
        self._add_area(params, "carbon-tax-area", carbon_tax_area)
        # HTTP request
        response = self._get(url, params=params)
        return parse_srmc_response(response.json())
