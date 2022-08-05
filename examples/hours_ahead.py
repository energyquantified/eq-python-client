"""
Extract the most recent forecast for each hour, up-to one hour in advanced.

This is useful for intraday benchmarking.

The script will give you a pandas.DataFrame with the values at the end. It
prints this for demonstration purposes.

Usage:

 1. Install dependencies:
    pip install --upgrade energyquantified
    pip install pandas

 2. Add API key below: eq = EnergyQuantified(api_key='...')

 3. Change options (line 41-47). You should update the begin and the end
    datetime in particular.

 4. Run script


---

Note: This script may take some time to run, as it loads the forecasts
from one day at a time in a loop. If you need to check day-ahead forecasts,
you would be better off using relative(). See the documentation for more info:

https://energyquantified-python.readthedocs.io/en/latest/userguide/instances.html#relative-queries-day-ahead-forecasts
"""

from energyquantified import EnergyQuantified
from energyquantified.time import Frequency, UTC
from energyquantified.data import TimeseriesList

import pandas as pd

from datetime import datetime, timedelta


# Initialize the client
eq = EnergyQuantified(api_key="aaaaaa-bbbbbb-cccccc-ddddddd")


# Set options
curve_name = "DE Wind Power Production MWh/h 15min Forecast"
tags = ['ec', 'ecsr']  # Extract ec deterministic forecasts (4 per day)
begin = datetime(2022, 8, 1, tzinfo=UTC)  # TODO REPLACE (freemium only have 30 days' history)
end = datetime(2022, 8, 5, tzinfo=UTC)  # TODO REPLACE (freemium only have 30 days' history)
frequency = Frequency.PT15M  # PT1H = Hourly, PT15M = 15-minute
time_ahead = timedelta(hours=1)  # How far ahead you want at minimum (default: at least one after)
name = "wind"  # Shorter name for columns


# Load data in loop – one load per day
forecasts = []
load_step = timedelta(days=1)
d = begin
while d < end:
    earliest = d
    latest = d + load_step - timedelta(seconds=1)  # 23:59:59
    instances = eq.instances.load(
        curve_name,
        tags=tags,
        issued_at_earliest=earliest,
        issued_at_latest=latest,
        frequency=frequency
    )
    forecasts += instances
    d += load_step

# Prepare data
forecasts = sorted(forecasts, key=lambda f: (f.instance.issued, f.instance.tag))
for f in forecasts:
    created = f.instance.created + time_ahead
    cutoff = created + timedelta(hours=24)
    f.data = list(filter(lambda d: d.date >= created and d.date < cutoff, f.data))
    f.set_name(name)

# To dataframe using EQ's util
# Data is sorted from oldest (in the first column) to most recent (in the last
# column). Therefore, we can use pandas' fillna with backfill (see below).
timeseries_list = TimeseriesList(forecasts)
df = timeseries_list.to_df(single_level_header=True)

# Get first avail non-NaN value per row
# https://datascientyst.com/get-first-non-null-value-per-row-pandas/

# Get the data
df_data = df.fillna(method='bfill', axis=1).iloc[:, 0].to_frame()
df_data.columns = ['data']

# Get the forecast used for each value
df_instances = df.apply(lambda s: pd.Series.first_valid_index(s)[0], axis=1).to_frame()
df_instances.columns = ['instance']

print("Most recent data, up to one hour before delivery:")
print(df_data)

print("The forecast used for each timestamp:")
print(df_instances)

# Merge them into one dataframe w/ two columns
df = pd.concat([df_data, df_instances], axis=1)

print("Merge the above dataframes into one:")
print(df)
