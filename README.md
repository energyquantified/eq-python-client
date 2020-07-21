# Energy Quantified Python Client

The Python library for [Energy Quantified](https://www.energyquantified.com)'s
Time Series API. It allows you to access thousands of data series directly from
Energy Quantified's time series database. It integrates with the popular
[pandas](https://pandas.pydata.org/docs/) library for high-performance data
analysis and manipulation.

Developed for **Python 3.7+**.

**Note:** An user account with an API key is required to use this library.
Create an account on [Energy Quantified](https://www.energyquantified.com)'s
home page. Trial users do get access to 30 days of history.

## Features

- Simple authentication
- Metadata caching
- Rate-limiting and automatic retries on network errors
- Full-text search and keyword search for curves and powerplants
- Forecasts- and time series data
- Period-based data
- *(TODO!)* OHLC data
- *(TODO!)* SRMC, dark- and spark spreads
- *(TODO!)* Shows your subscription for each series
- Support for time-zones, resolutions and aggregations
- Easy-to-use filters for issue dates and forecast types
- Integrates with pandas

## Documentation

TODO: Insert to readthedocs here.

## Installation

Install with **pip**:

```bash
# Install
pip install energyquantified

# Upgrade
pip install --upgrade energyquantified
```

## Example usage

Look at this short example on how to initialize the client, search for time
series and download data. More details available in the (TODO: Link) documentation.

```python
from datetime import date, timedelta
from energyquantified import EnergyQuantified

# Initialize client
eq = EnergyQuantified(api_key='<insert api key here>')

# Freetext search (filtering on attributes is also supported)
curves = eq.metadata.curves(q='germany wind production actual')

# Load time series data
curve = curve[0]
timeseries = eq.timeseries.load(
    curve,
    begin=date.today() - timedelta(days=10),
    end=date.today()
)

# Convert to Pandas data frame
df = timeseries.to_dataframe()
```

## License

The Energy Quantified Python client is licensed under the
[Apache License version 2.0](https://opensource.org/licenses/Apache-2.0).