from dateutil import parser

from ..data import (
    Timeseries,
    TimeseriesList,
    Value,
    ScenariosValue,
    MeanScenariosValue
)
from ..exceptions import ParseException
from ..time import to_timezone
from .metadata import (
    parse_curve,
    parse_instance,
    parse_resolution,
    parse_contract
)


def parse_timeseries_list(json):
    """
    Parse a JSON list-response from the API a list of Timeseries objects with
    Curve, Resolution, Instance and Contract.
    """
    if not isinstance(json, list):
        raise ParseException(
            f"Expected list of time series JSON objects, found: {type(json)}"
        )
    return TimeseriesList(parse_timeseries(json_obj) for json_obj in json)


def parse_timeseries(json):
    """
    Parse a JSON response from the API into a Timeseries object with
    Curve, Resolution, Instance and Contract.
    """
    # Parse the Resolution
    resolution = json.get("resolution")
    if resolution:
        resolution = parse_resolution(resolution)
    # Parse the Curve
    curve = json.get("curve")
    if curve:
        curve = parse_curve(curve)
    # Parse the instance
    instance = json.get("instance")
    if instance:
        instance = parse_instance(instance, curve=curve)
    # Parse the contract
    contract = json.get("contract")
    if contract:
        contract = parse_contract(contract)
    # Parse scenario names
    scenario_names = json.get("scenario_names") or None
    # Parse data
    data = _parse_data(json.get("data"), resolution=resolution)

    return Timeseries(
        curve=curve,
        resolution=resolution,
        instance=instance,
        contract=contract,
        scenario_names=scenario_names,
        data=data
    )


def _parse_data(json, resolution=None):
    """
    Parse the data[] part of the json response
    """
    # Empty time series
    if not json:
        return []
    # Look at the first element
    element = json[0]
    has_value = "v" in element
    has_scenarios = "s" in element
    # Regular (datetime, value) time series
    if has_value and not has_scenarios:
        return _parse_value_data(json, resolution=resolution)
    # Scenario (datetime, scenarios[]) time series
    if not has_value and has_scenarios:
        return _parse_scenarios_data(json, resolution=resolution)
    # Mean + scenario (datetime, mean value, scenarios[]) time series
    if has_value and has_scenarios:
        return _parse_mean_scenarios_data(json, resolution=resolution)
    # Well, this is awkward...
    raise ValueError("Timeseries data is missing both value and scenarios")


def _parse_value_data(json, resolution=None):
    timezone = resolution.timezone

    data = []
    for element in json:
        datetime_obj = to_timezone(
            parser.isoparse(element.get("d")),
            tz=timezone
        )
        value = element.get("v")
        data.append(Value(datetime_obj, value))

    return data


def _parse_scenarios_data(json, resolution=None):
    timezone = resolution.timezone

    data = []
    for element in json:
        datetime_obj = to_timezone(
            parser.isoparse(element.get("d")),
            tz=timezone
        )
        scenarios = tuple(element.get("s"))
        data.append(ScenariosValue(datetime_obj, scenarios))

    return data


def _parse_mean_scenarios_data(json, resolution=None):
    timezone = resolution.timezone

    data = []
    for element in json:
        datetime_obj = to_timezone(
            parser.isoparse(element.get("d")),
            tz=timezone
        )
        mean = element.get("v")
        scenarios = tuple(element.get("s"))
        data.append(MeanScenariosValue(datetime_obj, mean, scenarios))

    return data