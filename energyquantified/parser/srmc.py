from ..data import SRMC, SRMCOptions, OHLCList
from ..exceptions import ParseException
from ..metadata import Area
from .ohlc import parse_ohlc_list
from .timeseries import parse_timeseries
from .periodseries import parse_periodseries
from .metadata import parse_curve, parse_contract


def parse_srmc_response(json):
    # Get curve
    curve = json.get('curve')
    if curve is not None:
        curve = parse_curve(curve)
    # Get contract
    contract = json.get('contract')
    if contract is not None:
        contract = parse_contract(contract)
    # Get SRMC options
    options = json.get('srmc_options')
    if options is not None:
        options = parse_srmc_options(options)
    # Check for OHLC response
    data = json.get('ohlc')
    if data:
        ohlc = parse_ohlc_list(data)
        return SRMC(
            curve=curve,
            contract=contract,
            options=options,
            ohlc=OHLCList(ohlc)
        )
    # Check for timeseries response
    data = json.get('timeseries')
    if data:
        timeseries = parse_timeseries(data)
        return SRMC(
            curve=curve,
            contract=contract,
            options=options,
            timeseries=timeseries
        )
    # Check for period-based series response
    data = json.get('periodseries')
    if data:
        periodseries = parse_periodseries(data)
        return SRMC(
            curve=curve,
            contract=contract,
            options=options,
            periodseries=periodseries
        )
    # Something went wrong
    raise ParseException(
        "Failed to parse SRMC response, expected either ohlc data, "
        "timeseries or periodseries, but got neither"
    )

def parse_srmc_options(opts):
    # Check if there are any srmc options
    if not opts:
        return None
    # Get options
    fuel_type = opts.get('fuel_type')
    api2_tonne_to_mwh = opts.get('api2_tonne_to_mwh')
    gas_therm_to_mwh = opts.get('gas_therm_to_mwh')
    efficiency = opts.get('efficiency')
    carbon_emissions = opts.get('carbon_emissions')
    carbon_tax_area = opts.get('carbon_tax_area')
    if carbon_tax_area and Area.is_valid_tag(carbon_tax_area):
        carbon_tax_area = Area.by_tag(carbon_tax_area)
    else:
        carbon_tax_area = None
    # Create srmc options object
    srmc_options = SRMCOptions(
        fuel_type=fuel_type,
        api2_tonne_to_mwh=api2_tonne_to_mwh,
        gas_therm_to_mwh=gas_therm_to_mwh,
        efficiency=efficiency,
        carbon_emissions=carbon_emissions,
        carbon_tax_area=carbon_tax_area
    )
    # SRMC options
    return srmc_options
