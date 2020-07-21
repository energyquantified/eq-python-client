_timeseries_class = None
def _get_timeseries_class():
    """
    Private utility class for lazy-loading the Timeseries class.

    :return: The Timeseries class
    :rtype: class
    """
    global _timeseries_class
    if not _timeseries_class:
        from energyquantified.data import Timeseries
        _timeseries_class = Timeseries
    return _timeseries_class


_value_type_class = None
def _get_value_type_class():
    """
    Private utility class for lazy-loading the ValueType enum class.

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
        name = 'value'
    # Conversion
    ValueType = _get_value_type_class()
    if timeseries.value_type() == ValueType.VALUE:
        # Convert a time series of (date, value)
        df = pd.DataFrame.from_records(
            timeseries.data,
            columns=['date', name],
            index='date'
        )
    elif timeseries.value_type() == ValueType.SCENARIOS:
        # Convert a time series of (date, scenarios[])
        df = pd.DataFrame.from_records(
            ((d, *s) for d, s in timeseries.data),
            columns=['date'] + timeseries.scenario_names,
            index='date'
        )
    elif timeseries.value_type() == ValueType.MEAN_AND_SCENARIOS:
        # Convert a time series of (date, value, scenarios[])
        df = pd.DataFrame.from_records(
            ((d, v, *s) for d, v, s in timeseries.data),
            columns=['date', name] + timeseries.scenario_names,
            index='date'
        )
    else:
        # Unknown value type for time series
        raise ValueError(
            "Unknown ValueType: timeseries.value_type = "
            f"{timeseries.value_type()}"
        )
    return df
