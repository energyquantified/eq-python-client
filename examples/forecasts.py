from datetime import datetime, date, timedelta

from energyquantified import EnergyQuantified
from energyquantified.time import Frequency


# Initialize client (replace with your API key)
eq = EnergyQuantified(api_key="aaaaaa-bbbbbb-cccccc-ddddddd")


# Curve alternative #1: The curve name for the German wind
# production actuals
curve_name = "DE Wind Power Production MWh/h 15min Forecast"

# Curve alternative #2: Find the Curve for German wind
# production actuals
curves = eq.metadata.curves(
    area='DE',
    exact_category='wind power production',
    data_type='forecast'
)
# Get the first curve (there should only be one result)
curve = curves[0]


# --- Load forecast #1 ---

# Minimal example of how to load the latest 4 available forecasts
# based on the EC deterministic weather model
forecasts = eq.instances.load(
    curve,  # or you can use curve_name
    tags=['ec'],
    limit=4,
    frequency=Frequency.PT1H  # Optionally aggregate to HOURLY resolution
)


# --- Load forecast #2 ---

# Get today at midnight as a datetime object
today = date.today()
today = datetime(year=today.year, month=today.month, day=today.day)

# Get yesterday at 00:00 (earliest) and yesterday at 23:59:59 (latest)
earliest = today - timedelta(days=1)
latest = today - timedelta(days=0, seconds=1)

# Load data EC and GFS deterministic wind power forecasts for yesterday
forecasts = eq.instances.load(
    curve,  # or you can use curve_name
    tags=['ec', 'gfs'],
    issued_at_earliest=earliest,
    issued_at_latest=latest,
    frequency=Frequency.PT1H  # Optionally aggregate to HOURLY resolution
)


# The result is a list of time series objects. When loading
# instances (forecasts), each time series object has an 'instance'-
# attribute set. It identifies the forecast:
for timeseries in forecasts:
    print(f" - {timeseries.instance}")
    print(
        f"   {len(timeseries.data)} hours, "
        f"begin=\"{timeseries.begin()}\", end=\"{timeseries.end()}\""
    )
