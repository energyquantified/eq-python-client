from energyquantified import EnergyQuantified
from energyquantified.metadata import Area, DataType

# Initialize client
eq = EnergyQuantified(api_key="aaaaaa-bbbbbb-cccccc-ddddddd")

# Search #1: Freetext search
curves = eq.metadata.curves(q="de wind production actual")
for curve in curves:
    print(curve)

# Search #2: Search by exact attributes on the curves
curves = eq.metadata.curves(
    category=["Wind", "Production"],
    area=Area.DE,
    data_type=DataType.ACTUAL
)
for curve in curves:
    print(curve)
