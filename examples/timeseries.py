from energyquantified import EnergyQuantified
from energyquantified.time import today, Resolution, Frequency, CET


# Initialize client (replace with your API key)
eq = EnergyQuantified(api_key="aaaaaa-bbbbbb-cccccc-ddddddd")

# Curve alternative #1: The curve name for the German wind
# production actuals
curve_name = "DE Wind Power Production MWh/h 15min Actual"

# Curve alternative #2: Find the Curve for German wind
# production actuals
curves = eq.metadata.curves(
    area='DE',
    exact_category='wind power production',
    data_type='actual'
)
# Get the first curve (there should only be one result)
curve = curves[0]

# Load data for last 15 days, aggregated to daily resolution
# We are using EQ's Resolution class for safe date arithmetics.
# Remove the "frequency=Frequency.P1D" parameter to load data in
# the original resolution (which is 15-minute/PT15M).
resolution = Resolution(Frequency.P1D, CET)
de_wind_actuals_daily = eq.timeseries.load(
    curve,
    begin=resolution.shift(today(), -15),
    end=resolution.shift(today(), +1),
    frequency=Frequency.P1D # Daily frequency
)

# Print the time series
de_wind_actuals_daily.print()
