from energyquantified import EnergyQuantified
from energyquantified.metadata import Area, DataType

# Initialize client
eq = EnergyQuantified(api_key="aaaaaa-bbbbbb-cccccc-ddddddd")


# Search #1: Freetext search
print("Search #1: Freetext search")
curves = eq.metadata.curves(q="de wind production actual")
for curve in curves:
    print(curve)


# Search #2: Search by exact attributes on the curves
print("Search #2: Search by exact attributes")
curves = eq.metadata.curves(
    category=["Wind", "Production"],
    area=Area.DE,
    data_type=DataType.ACTUAL
)
for curve in curves:
    print(curve)


# Search #3: Search actual exchange curves
print("Search #3: Search actual exchange")
curves = eq.metadata.curves(
    q="de pl",
    data_type=DataType.ACTUAL
)
for curve in curves:
    print(curve)


# Search #4: Pagination
print("Search #4: Pagination")
page1 = eq.metadata.curves(
    area=Area.DE,
    data_type=DataType.ACTUAL,
    page_size=10,  # Set page size  (defaults to 50)
    page=1  # Optionally set page number (defaults to 1)
)
print(f"page number = {page1.page}, page size = {page1.page_size}")
print(f"total curves = {page1.total_items}, total pages = {page1.total_pages}")
# Get the next page
has_page2 = page1.has_next_page()
page2 = page1.get_next_page()
