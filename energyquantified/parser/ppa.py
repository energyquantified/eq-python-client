from dateutil import parser

from ..data import PPA, PPAList, PPAProduct
from ..exceptions import ParseException
from ..metadata import ContractStructure, PPADuration, Technology
from .metadata import parse_curve


def parse_ppa_response(json):
    # Parse curve
    curve = json.get("curve")
    if curve:
        curve = parse_curve(curve)
    # Parse unit
    unit = json.get("unit")
    denominator = json.get("denominator")
    # Parse PPA objects
    data = parse_ppa_list(json.get("data") or [])

    return PPAList(data, curve=curve, unit=unit, denominator=denominator)


def parse_ppa_list(json):
    # Parse data[], but keep track of data[index] to create a better exception
    data = []
    for index, item in enumerate(json):
        try:
            ppa = parse_ppa(item)
        except Exception as e:
            raise ParseException(
                f"Failed to parse data[{index}] in PPA JSON response: {item}"
            ) from e
        data.append(ppa)
    return data


def parse_ppa(json):
    return PPA(
        product=parse_ppa_product(json.get("product")),
        price=json.get("price"),
    )


def parse_ppa_product(json):
    return PPAProduct(
        date=parser.isoparse(json.get("date")).date(),
        technology=Technology.by_tag(json.get("technology")),
        contract_structure=ContractStructure.by_tag(json.get("contract_structure")),
        delivery_begin=parser.isoparse(json.get("delivery_begin")).date(),
        duration=PPADuration.by_years(json.get("duration")),
    )
