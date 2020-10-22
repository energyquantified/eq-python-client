"""
A demonstration of how to plot data from Energy Quantified. Using the
front Quarter contract for Nord Pool as example.

Plotting the last 30 days and adding a couple of moving averages
(10-day, 3-day) for demonstration purposes.

Usage:

 0. You probably need tkinter (GUI library) installed to run this demo

 1. Install dependencies:
    pip install --upgrade energyquantified
    pip install pandas matplotlib mplfinance

 2. Add API key below: eq = EnergyQuantified(api_key='...')

 3. Run script
"""

from datetime import date, timedelta

from matplotlib import style
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from mplfinance.original_flavor import candlestick_ohlc

from energyquantified import EnergyQuantified
from energyquantified.time import Frequency, now, CET


# Connect to EQ
eq = EnergyQuantified(api_key='INSERT API KEY HERE')  # <- API key goes here

# Set options
curve = 'NP Futures Power Base EUR/MWh Nasdaq OHLC'
begin = date.today() - timedelta(days=29)  # Trial users get 30 days
end = date.today()

# Get the front quarter date for 'today' (i.e. 2020-07-01 = Q3-2020)
quarter_delivery = (
    Frequency.P3M.shift(
        Frequency.P3M.truncate(now(tz=CET)),
        1
    ).date()
)

# Verify API key (optional)
assert eq.is_api_key_valid(), "API key is not valid"

# Download data for the last 200 days
ohlc_list = eq.ohlc.load(
    'NP Futures Power Base EUR/MWh Nasdaq OHLC',
    begin=begin,
    end=end,
    period='quarter',
    delivery=quarter_delivery
)

# Create a pandas DataFrame
df = ohlc_list.to_dataframe()

# Extract front quarter contract (use this if you're not applying
# filters in eq.ohlc.load() like above)
# df = df[df['period'] == 'quarter']
# df = df[df['delivery'] == quarter_delivery]

# Map traded to matplotlib date
df['traded'] = df['traded'].map(mdates.date2num)

# Create 10-day and 3-day moving averages over settlement price
# (for demonstration purposes, not for analysis)
df['10ma'] = df['settlement'].rolling(window=10).mean()
df['3ma'] = df['settlement'].rolling(window=3).mean()

# Apply ggplot style to matplotlib charts
style.use('ggplot')

# Create two subplots (5-to-1 ratio)
ax1 = plt.subplot2grid((6, 1), (0,0), rowspan=5, colspan=1)
ax2 = plt.subplot2grid((6, 1), (5,0), rowspan=1, colspan=1, sharex=ax1)
ax1.xaxis_date()

# Add OHLC and moving averages to upper plot
candlestick_ohlc(
    ax1,
    df[['traded', 'open', 'high', 'low', 'close']].values,
    width=0.5,
    colorup='g',
    colordown='r'
)
ax1.plot(df['traded'], df['10ma'])
ax1.plot(df['traded'], df['3ma'])

# Add volume to lower plot
ax2.bar(df['traded'], df['volume'])

# Display plot
plt.show()
