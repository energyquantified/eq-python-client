from ..metadata import CurveType
from ..parser.ppa import parse_ppa_response
from .base import BaseAPI

# Tuple of supported values for Curve.curve_type in the PPA API
CURVE_TYPES = (CurveType.PPA,)


class PpaAPI(BaseAPI):
    """
    Operations for power purchase agreement (PPA) prices. Access these
    operations via an instance of the
    :py:class:`energyquantified.EnergyQuantified` class:

       >>> eq = EnergyQuantified(api_key="aaaa-bbbb-cccc-dddd")
       >>> eq.ppa.load(curve, begin, end)
    """

    def load(
        self,
        curve,
        begin=None,
        end=None,
        technology=None,
        contract_structure=None,
        delivery_begin=None,
        duration=None,
        unit=None,
    ):
        """
        Load PPA prices quoted in a date interval for a
        :py:class:`energyquantified.metadata.Curve`.

        Filters on different fields are combined (AND). When you give several
        values for the same filter, prices matching any of them are
        returned (OR).

        This operation works for curves with ``curve_type = PPA`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param begin: The begin of the quote-date interval (inclusive)
        :type begin: date, str, required
        :param end: The end of the quote-date interval (exclusive)
        :type end: date, str, required
        :param technology: Only include prices for these technologies
        :type technology: Technology, str, list, optional
        :param contract_structure: Only include prices for these contract\
            structures
        :type contract_structure: ContractStructure, str, list, optional
        :param delivery_begin: Only include prices for contracts with\
            delivery starting on this date
        :type delivery_begin: date, str, optional
        :param duration: Only include prices for contracts of these\
            durations. Allowed values are 3, 5, 10 and 15 years.
        :type duration: PPADuration, int, list, optional
        :param unit: Convert the prices to another currency, defaults to the\
            curve's unit
        :type unit: str, optional
        :return: A list of PPA objects
        :rtype: :py:class:`energyquantified.data.PPAList`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/ppa/{safe_curve}/"
        # Parameters
        params = {}
        self._add_date(params, "begin", begin, required=True)
        self._add_date(params, "end", end, required=True)
        self._add_ppa_filters(
            params,
            technology=technology,
            contract_structure=contract_structure,
            delivery_begin=delivery_begin,
            duration=duration,
        )
        self._add_str(params, "unit", unit)
        # HTTP request
        response = self._get(url, params=params)
        return parse_ppa_response(response.json())

    def latest(
        self,
        curve,
        date=None,
        technology=None,
        contract_structure=None,
        delivery_begin=None,
        duration=None,
        unit=None,
    ):
        """
        Load all PPA prices from the latest quote date.

        If ``date`` is given, this method loads the prices from the latest
        quote date on or before that date.

        Filters on different fields are combined (AND). When you give several
        values for the same filter, prices matching any of them are
        returned (OR).

        This operation works for curves with ``curve_type = PPA`` only.

        :param curve: The curve or curve name
        :type curve: :py:class:`energyquantified.metadata.Curve`, str
        :param date: The latest quote date to consider, defaults to the\
            latest available quote date
        :type date: date, str, optional
        :param technology: Only include prices for these technologies
        :type technology: Technology, str, list, optional
        :param contract_structure: Only include prices for these contract\
            structures
        :type contract_structure: ContractStructure, str, list, optional
        :param delivery_begin: Only include prices for contracts with\
            delivery starting on this date
        :type delivery_begin: date, str, optional
        :param duration: Only include prices for contracts of these\
            durations. Allowed values are 3, 5, 10 and 15 years.
        :type duration: PPADuration, int, list, optional
        :param unit: Convert the prices to another currency, defaults to the\
            curve's unit
        :type unit: str, optional
        :return: A list of PPA objects
        :rtype: :py:class:`energyquantified.data.PPAList`
        """
        # Build URL
        safe_curve = self._urlencode_curve_name(curve, curve_types=CURVE_TYPES)
        url = f"/ppa/{safe_curve}/latest/"
        # Parameters
        params = {}
        self._add_date(params, "date", date)
        self._add_ppa_filters(
            params,
            technology=technology,
            contract_structure=contract_structure,
            delivery_begin=delivery_begin,
            duration=duration,
        )
        self._add_str(params, "unit", unit)
        # HTTP request
        response = self._get(url, params=params)
        return parse_ppa_response(response.json())

    def _add_ppa_filters(
        self,
        params,
        technology,
        contract_structure,
        delivery_begin,
        duration,
    ):
        self._add_technology_list(params, "technology", technology)
        self._add_contract_structure_list(
            params, "contract-structure", contract_structure
        )
        self._add_date(params, "delivery-begin", delivery_begin)
        self._add_ppa_duration_list(params, "duration", duration)
