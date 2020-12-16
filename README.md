# Energy Quantified Python Client

![Apache License version 2.0](https://img.shields.io/github/license/energyquantified/eq-python-client?style=flat "Apache License version 2.0")
![Python 3.7+](https://img.shields.io/pypi/pyversions/energyquantified.svg?style=flat "Python versions")
![Wheel](https://img.shields.io/pypi/wheel/energyquantified "Wheel")

[Documentation](https://energyquantified-python.readthedocs.io) |
[Python package](https://pypi.org/project/energyquantified/) |
[GitHub repository](https://github.com/energyquantified/eq-python-client)

The Python library for [Energy Quantified](https://www.energyquantified.com)'s
Time Series API. It allows you to access thousands of data series directly from
Energy Quantified's time series database. It integrates with the popular
[pandas](https://pandas.pydata.org/docs/) library for high-performance data
analysis and manipulation.

Developed for **Python 3.7+**.

```python
from datetime import date, timedelta
from energyquantified import EnergyQuantified

# Initialize client
eq = EnergyQuantified(api_key='<insert api key here>')

# Freetext search (filtering on attributes is also supported)
curves = eq.metadata.curves(q='de wind production actual')

# Load time series data
curve = curves[0]
timeseries = eq.timeseries.load(
    curve,
    begin=date.today() - timedelta(days=10),
    end=date.today()
)

# Convert to Pandas data frame
df = timeseries.to_dataframe()
```

Full [documentation](https://energyquantified-python.readthedocs.io) available
at Read the Docs.


## Features

- Simple authentication
- Metadata caching
- Rate-limiting and automatic retries on network errors
- Full-text search and keyword search for curves and powerplants
- Forecasts- and time series data
- Period-based data
- OHLC data
- SRMC calculations on OHLC data
- *(TODO!)* Shows your subscription for each series
- Support for time-zones, resolutions and aggregations
- Easy-to-use filters for issue dates and forecast types
- Integrates with pandas

**Note:** A user account with an API key is required to use this library.
Create an account on [Energy Quantified](https://www.energyquantified.com)'s
home page. Trial users get access to 30 days of history.

## Installation

Install with **pip**:

```bash
# Install
pip install energyquantified

# Upgrade
pip install --upgrade energyquantified
```

## Documentation

Find the [documentation](https://energyquantified-python.readthedocs.io) at
Read the Docs.

## License

The Energy Quantified Python client is licensed under the
[Apache License version 2.0](https://opensource.org/licenses/Apache-2.0).
