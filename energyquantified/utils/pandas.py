_timeseries_class = None
def _get_timeseries_class():
    """
    Private utility function for lazy-loading the Timeseries class.

    :return: The Timeseries class
    :rtype: class
    """
    global _timeseries_class
    if not _timeseries_class:
        from energyquantified.data import Timeseries
        _timeseries_class = Timeseries
    return _timeseries_class

_ohlc_list_class = None
def _get_ohlc_list_class():
    """
    Private utility function for lazy-loading the OHLCList class.

    :return: The OHLCList class
    :rtype: class
    """
    global _ohlc_list_class
    if not _ohlc_list_class:
        from energyquantified.data import OHLCList
        _ohlc_list_class = OHLCList
    return _ohlc_list_class


_value_type_class = None
def _get_value_type_class():
    """
    Private utility function for lazy-loading the ValueType enum class.

    :return: The ValueType class
    :rtype: class
    """
    global _value_type_class
    if not _value_type_class:
        from energyquantified.data import ValueType
        _value_type_class = ValueType
    return _value_type_class


pd = None
_is_pandas_installed = None
def is_pandas_installed():
    """
    Private utility to both lazy-load and to check if pandas is installed.

    :return: True when pandas is available on the system, otherwise False
    :rtype: bool
    """
    global pd, _is_pandas_installed
    if _is_pandas_installed is None:
        try:
            import pandas as pd
            _is_pandas_installed = True
        except ImportError as e:
            _is_pandas_installed = False
    return _is_pandas_installed


def assert_pandas_installed():
    """
    Assert that pandas is installed.

    :raises ImportError: When pandas is not installed on the system
    """
    if not is_pandas_installed():
        if not is_pandas_installed():
            raise ImportError(
                "You must install the \"pandas\" data analysis library "
                "to use this functionality. Visit "
                "https://pandas.pydata.org/docs/ for more information."
            )


def timeseries_to_dataframe(timeseries, name=None):
    """
    Convert a time series to a ``pandas.DataFrame``.

    :param timeseries: The time series
    :type timeseries: energyquantified.data.Timeseries, required
    :param name: Set a name for the value column, defaults to ``value``
    :type name: str, optional
    :return: A DataFrame
    :rtype: pandas.DataFrame
    :raises ImportError: When pandas is not installed on the system
    """
    # Checks
    assert_pandas_installed()
    assert isinstance(timeseries, _get_timeseries_class()), (
        "timeseries must be an instance of energyquantified.data.Timeseries"
    )
    if not name:
        name = timeseries.name
    # Conversion
    ValueType = _get_value_type_class()
    if timeseries.value_type() == ValueType.VALUE:
        # Convert a time series of (date, value)
        return _timeseries_to_dataframe_value(timeseries, name)
    if timeseries.value_type() == ValueType.SCENARIOS:
        # Convert a time series of (date, scenarios[])
        return _timeseries_to_dataframe_scenarios(timeseries, name)
    if timeseries.value_type() == ValueType.MEAN_AND_SCENARIOS:
        # Convert a time series of (date, value, scenarios[])
        return _timeseries_to_dataframe_mean_and_scenarios(timeseries, name)
    # Unknown value type for time series
    raise ValueError(
        "Unknown ValueType: timeseries.value_type = "
        f"{timeseries.value_type()}"
    )


def _timeseries_to_dataframe_value(timeseries, name):
    """
    Private utility function for converting a time series of single values
    to a pandas dataframe.

    :param timeseries: A time series object
    :type timeseries: Timeseries
    :param name: The time series name
    :type name: str
    :return: A pandas DataFrame
    :rtype: pandas.DataFrame
    """
    # Column headers
    columns = [
        [name],
        [timeseries.instance_or_contract_dataframe_column_header()],
        ['']
    ]
    # Convert a time series of (date, value)
    df = pd.DataFrame.from_records(
        ((v.value,) for v in timeseries),
        columns=columns,
        index=[v.date for v in timeseries],
    )
    df.index.name = 'date'
    return df


def _timeseries_to_dataframe_scenarios(timeseries, name):
    """
    Private utility function for converting a time series of scenario values
    to a pandas dataframe.

    :param timeseries: A time series object
    :type timeseries: Timeseries
    :param name: The time series name
    :type name: str
    :return: A pandas DataFrame
    :rtype: pandas.DataFrame
    """
    width = timeseries.total_values_per_item()
    # Column headers
    columns = [
        [name] * width,
        [timeseries.instance_or_contract_dataframe_column_header()] * width,
        timeseries.scenario_names
    ]
    # Convert a time series of (date, scenarios[])
    df = pd.DataFrame.from_records(
        (v.scenarios for v in timeseries.data),
        columns=columns,
        index=[v.date for v in timeseries],
    )
    df.index.name = 'date'
    return df


def _timeseries_to_dataframe_mean_and_scenarios(timeseries, name):
    """
    Private utility function for converting a time series of a mean value
    and scenarios to a pandas dataframe.

    :param timeseries: A time series object
    :type timeseries: Timeseries
    :param name: The time series name
    :type name: str
    :return: A pandas DataFrame
    :rtype: pandas.DataFrame
    """
    width = timeseries.total_values_per_item()
    # Column headers
    columns = [
        [name] * width,
        [timeseries.instance_or_contract_dataframe_column_header()] * width,
        [''] + timeseries.scenario_names
    ]
    # Convert a time series of (date, scenarios[])
    df = pd.DataFrame.from_records(
        ((v.value, *v.scenarios) for v in timeseries.data),
        columns=columns,
        index=[v.date for v in timeseries],
    )
    df.index.name = 'date'
    return df


def timeseries_list_to_dataframe(timeseries_list):
    """
    Convert a list of time series to a ``pandas.DataFrame``.

    :param timeseries_list: [description]
    :type timeseries_list: [type]
    """
    # Checks
    assert_pandas_installed()
    assert timeseries_list, "timeseries list is empty"
    for index, timeseries in enumerate(timeseries_list):
        assert isinstance(timeseries, _get_timeseries_class()), (
            f"timeseries_list[{index}] must be an instance of "
            f"energyquantified.data.Timeseries, but was: {type(timeseries)}"
        )
    # Merge into one data frame
    return pd.concat([ts.to_dataframe() for ts in timeseries_list], axis=1)


def ohlc_list_to_dataframe(ohlc_list):
    """
    Convert an :py:class:`energyquantified.data.OHLCList` to a
    ``pandas.DataFrame``.

    :param ohlc_list: A list of OHLC objects
    :type ohlc_list: OHLCList
    :return: A DataFrame
    :rtype: pandas.DataFrame
    :raises ImportError: When pandas is not installed on the system
    """
    # Checks
    assert_pandas_installed()
    assert isinstance(ohlc_list, _get_ohlc_list_class()), (
        "ohlc_list must be an instance of energyquantified.data.OHLCList"
    )
    # Conversion
    return pd.DataFrame.from_records((
        {
            "traded": ohlc.product.traded,
            "period": ohlc.product.period.tag,
            "front": ohlc.product.front,
            "delivery": ohlc.product.delivery,
            "open": ohlc.open,
            "high": ohlc.high,
            "low": ohlc.low,
            "close": ohlc.close,
            "settlement": ohlc.settlement,
            "volume": ohlc.volume,
            "open_interest": ohlc.open_interest,
        } for ohlc in ohlc_list
    ))