from .classes import (
    _get_absolute_result_class,
    _get_ohlc_list_class,
    _get_timeseries_class,
    _get_value_type_class,
)
from .deprecation import deprecated


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
                'You must install the "pandas" data analysis library '
                "to use this functionality. Visit "
                "https://pandas.pydata.org/docs/ for more information."
            )


def timeseries_to_pandas_dataframe(timeseries, name=None, single_level_header=False):
    """
    Convert a time series to a ``pandas.DataFrame``.

    :param timeseries: The time series
    :type timeseries: energyquantified.data.Timeseries, required
    :param name: Set a custom name in the column header, Timeseries.curve.name \
        is used when this parameter is not set, defaults to None
    :type name: str, optional
    :param single_level_header: Set to True to use single-level header \
        in the DataFrame, defaults to False
    :type single_level_header: boolean, optional
    :return: A DataFrame
    :rtype: pandas.DataFrame
    :raises ImportError: When pandas is not installed on the system
    """
    # Checks
    assert_pandas_installed()
    assert isinstance(
        timeseries, _get_timeseries_class()
    ), "timeseries must be an instance of energyquantified.data.Timeseries"
    assert isinstance(
        name, (type(None), str)
    ), f"parameter name must be string or None, was {type(name)}"
    if name is None:
        name = timeseries.name
        include_instance = True
    else:
        include_instance = False
    # Conversion
    ValueType = _get_value_type_class()
    if timeseries.value_type() == ValueType.VALUE:
        # Convert a time series of (date, value)
        if single_level_header:
            return _timeseries_to_dataframe_value_single_header(
                timeseries, name, include_instance=include_instance
            )
        else:
            return _timeseries_to_dataframe_value(timeseries, name)
    if timeseries.value_type() == ValueType.SCENARIOS:
        # Convert a time series of (date, scenarios[])
        if single_level_header:
            return _timeseries_to_dataframe_scenarios_single_header(
                timeseries, name, include_instance=include_instance
            )
        else:
            return _timeseries_to_dataframe_scenarios(timeseries, name)
    if timeseries.value_type() == ValueType.MEAN_AND_SCENARIOS:
        # Convert a time series of (date, value, scenarios[])
        if single_level_header:
            return _timeseries_to_dataframe_mean_and_scenarios_single_header(
                timeseries, name, include_instance=include_instance
            )
        else:
            return _timeseries_to_dataframe_mean_and_scenarios(timeseries, name)
    # Unknown value type for time series
    raise ValueError(
        "Unknown ValueType: timeseries.value_type = " f"{timeseries.value_type()}"
    )


@deprecated(alt=timeseries_to_pandas_dataframe)
def timeseries_to_dataframe(timeseries, name=None, single_level_header=False):
    """
    DEPRECATED: Use ``timeseries_to_pandas_dataframe`` instead.

    Convert a time series to a ``pandas.DataFrame``.

    :param timeseries: The time series
    :type timeseries: energyquantified.data.Timeseries, required
    :param name: Set a custom name in the column header, Timeseries.curve.name \
        is used when this parameter is not set, defaults to None
    :type name: str, optional
    :param single_level_header: Set to True to use single-level header \
        in the DataFrame, defaults to False
    :type single_level_header: boolean, optional
    :return: A DataFrame
    :rtype: pandas.DataFrame
    :raises ImportError: When pandas is not installed on the system
    """
    return timeseries_to_pandas_dataframe(timeseries, name, single_level_header)


def _timeseries_to_dataframe_value(timeseries, name):
    """
    Private utility function for converting a time series of single values
    to a pandas dataframe.

    The DataFrame will have a three-level column header.

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
        [""],
    ]
    # Convert a time series of (date, value)
    df = pd.DataFrame.from_records(
        ((v.value,) for v in timeseries),
        columns=columns,
        index=[v.date for v in timeseries],
    )
    df.index.name = "date"
    return df


def _timeseries_to_dataframe_value_single_header(
    timeseries, name, include_instance=True
):
    """
    Private utility function for converting a time series of single values
    to a pandas dataframe.

    The DateFrame will have a single-level column header.

    :param timeseries: A time series object
    :type timeseries: Timeseries
    :param name: The time series name
    :type name: str
    :param include_instance: Include the instance in the header?
    :type include_instance: bool
    :return: A pandas DataFrame
    :rtype: pandas.DataFrame
    """
    # Column header
    if include_instance:
        instance = timeseries.instance_or_contract_dataframe_column_header()
        columns = [f"{name} {instance}".strip()]
    else:
        columns = [name]
    # Convert a time series of (date, value)
    df = pd.DataFrame.from_records(
        ((v.value,) for v in timeseries),
        columns=columns,
        index=[v.date for v in timeseries],
    )
    df.index.name = "date"
    return df


def _timeseries_to_dataframe_scenarios(timeseries, name):
    """
    Private utility function for converting a time series of scenario values
    to a pandas dataframe.

    The DataFrame will have a three-level column header.

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
        timeseries.scenario_names,
    ]
    # Convert a time series of (date, scenarios[])
    df = pd.DataFrame.from_records(
        (v.scenarios for v in timeseries.data),
        columns=columns,
        index=[v.date for v in timeseries],
    )
    df.index.name = "date"
    return df


def _timeseries_to_dataframe_scenarios_single_header(
    timeseries, name, include_instance=True
):
    """
    Private utility function for converting a time series of scenario values
    to a pandas dataframe.

    The DateFrame will have a single-level column header.

    :param timeseries: A time series object
    :type timeseries: Timeseries
    :param name: The time series name
    :type name: str
    :param include_instance: Include the instance in the header?
    :type include_instance: bool
    :return: A pandas DataFrame
    :rtype: pandas.DataFrame
    """
    width = timeseries.total_values_per_item()
    # Column header
    if include_instance:
        instance = timeseries.instance_or_contract_dataframe_column_header()
        columns = [
            f"{name} {instance} {scenario}".strip()
            for scenario in timeseries.scenario_names
        ]
    else:
        columns = [
            f"{name} {scenario}".strip() for scenario in timeseries.scenario_names
        ]
    # Convert a time series of (date, scenarios[])
    df = pd.DataFrame.from_records(
        (v.scenarios for v in timeseries.data),
        columns=columns,
        index=[v.date for v in timeseries],
    )
    df.index.name = "date"
    return df


def _timeseries_to_dataframe_mean_and_scenarios(timeseries, name):
    """
    Private utility function for converting a time series of a mean value
    and scenarios to a pandas dataframe.

    The DataFrame will have a three-level column header.

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
        [""] + timeseries.scenario_names,
    ]
    # Convert a time series of (date, scenarios[])
    df = pd.DataFrame.from_records(
        ((v.value, *v.scenarios) for v in timeseries.data),
        columns=columns,
        index=[v.date for v in timeseries],
    )
    df.index.name = "date"
    return df


def _timeseries_to_dataframe_mean_and_scenarios_single_header(
    timeseries, name, include_instance=True
):
    """
    Private utility function for converting a time series of a mean value
    and scenarios to a pandas dataframe.

    The DateFrame will have a single-level column header.

    :param timeseries: A time series object
    :type timeseries: Timeseries
    :param name: The time series name
    :type name: str
    :param include_instance: Include the instance in the header?
    :type include_instance: bool
    :return: A pandas DataFrame
    :rtype: pandas.DataFrame
    """
    width = timeseries.total_values_per_item()
    # Column headers
    scenario_names = [""] + timeseries.scenario_names
    if include_instance:
        instance = timeseries.instance_or_contract_dataframe_column_header()
        columns = [
            f"{name} {instance} {scenario}".strip() for scenario in scenario_names
        ]
    else:
        columns = [f"{name} {scenario}".strip() for scenario in scenario_names]
    # Convert a time series of (date, scenarios[])
    df = pd.DataFrame.from_records(
        ((v.value, *v.scenarios) for v in timeseries.data),
        columns=columns,
        index=[v.date for v in timeseries],
    )
    df.index.name = "date"
    return df


def timeseries_list_to_pandas_dataframe(timeseries_list, single_level_header=False):
    """
    Convert a list of time series to a ``pandas.DataFrame``.

    :param timeseries_list: [description]
    :type timeseries_list: [type]
    :param single_level_header: Set to True to use single-level header \
        in the DataFrame, defaults to False
    :type single_level_header: boolean, optional
    :return: A pandas DataFrame
    :rtype: pandas.DataFrame
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
    return pd.concat(
        [
            ts.to_pandas_dataframe(single_level_header=single_level_header)
            for ts in timeseries_list
        ],
        axis=1,
        sort=True,
    )


@deprecated(alt=timeseries_list_to_pandas_dataframe)
def timeseries_list_to_dataframe(timeseries_list, single_level_header=False):
    """
    DEPRECATED: Use ``timeseries_list_to_pandas_dataframe`` instead.
    
    Convert a list of time series to a ``pandas.DataFrame``.

    :param timeseries_list: [description]
    :type timeseries_list: [type]
    :param single_level_header: Set to True to use single-level header \
        in the DataFrame, defaults to False
    :type single_level_header: boolean, optional
    :return: A pandas DataFrame
    :rtype: pandas.DataFrame
    """
    return timeseries_list_to_pandas_dataframe(timeseries_list, single_level_header)


def ohlc_list_to_pandas_dataframe(ohlc_list):
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
    assert isinstance(
        ohlc_list, _get_ohlc_list_class()
    ), "ohlc_list must be an instance of energyquantified.data.OHLCList"
    # Conversion
    return pd.DataFrame.from_records(
        (
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
            }
            for ohlc in ohlc_list
        )
    )


@deprecated(alt=ohlc_list_to_pandas_dataframe)
def ohlc_list_to_dataframe(ohlc_list):
    """
    DEPRECATED: Use ``ohlc_list_to_pandas_dataframe`` instead.

    Convert an :py:class:`energyquantified.data.OHLCList` to a ``pandas.DataFrame``.

    :param ohlc_list: A list of OHLC objects
    :type ohlc_list: OHLCList
    :return: A DataFrame
    :rtype: pandas.DataFrame
    :raises ImportError: When pandas is not installed on the system
    """
    return ohlc_list_to_pandas_dataframe(ohlc_list)


def absolute_result_to_pandas_dataframe(
    absolute_result, name=None, single_level_index=False
):
    """
    Convert an :py:class:`energyquantified.data.AbsoluteResult` to a
    ``pandas.DataFrame``.

    :param absolute_result: The absolute result
    :type absolute_result: AbsoluteResult
    :param name: Set a name for the value column, defaults to None. Uses\
    the curve name if not set. The delivery date is appended to the name.
    :type name: str | None, optional
    :param single_level_index: Set to True to use single-level index in the\
    DataFrame, defaults to False
    :type single_level_index: bool, optional
    :return: A DataFrame
    :rtype: pandas.DataFrame
    :raises ImportError: When pandas is not installed on the system
    """
    assert_pandas_installed()
    assert isinstance(
        absolute_result, _get_absolute_result_class()
    ), "absolute_result must be an instance of energyquantified.data.AbsoluteResult"
    assert isinstance(
        name, (type(None), str)
    ), f"parameter name must be string or None, was {type(name)}"
    if name is None:
        name = absolute_result.curve.name
    if single_level_index:
        return _absolute_result_to_dataframe_single_index(absolute_result, name)
    else:
        return _absolute_result_to_dataframe(absolute_result, name)


@deprecated(alt=absolute_result_to_pandas_dataframe)
def absolute_result_to_dataframe(absolute_result, name=None, single_level_index=False):
    """
    DEPRECATED: Use ``absolute_result_to_pandas_dataframe`` instead.

    Convert an :py:class:`energyquantified.data.AbsoluteResult` to a
    ``pandas.DataFrame``.

    :param absolute_result: The absolute result
    :type absolute_result: AbsoluteResult
    :param name: Set a name for the value column, defaults to None. Uses\
    the curve name if not set. The delivery date is appended to the name.
    :type name: str | None, optional
    :param single_level_index: Set to True to use single-level index in the\
    DataFrame, defaults to False
    :type single_level_index: bool, optional
    :return: A DataFrame
    :rtype: pandas.DataFrame
    :raises ImportError: When pandas is not installed on the system
    """
    return absolute_result_to_pandas_dataframe(
        absolute_result, name, single_level_index
    )


def _absolute_result_to_dataframe(absolute_result, name):
    # Column headers
    columns = [f"{name} {absolute_result.delivery:%Y-%m-%d %H:%M}".strip()]
    # Create dataframe
    df = pd.DataFrame.from_records(
        ((item.value,) for item in absolute_result.items),
        columns=columns,
        index=pd.MultiIndex.from_arrays(
            [
                [
                    f"{item.instance.issued:%Y-%m-%d %H:%M}"
                    for item in absolute_result.items
                ],
                [item.instance.tag for item in absolute_result.items],
            ],
            names=["issued", "tag"],
        ),
    )
    return df


def _absolute_result_to_dataframe_single_index(absolute_result, name):
    # Column headers
    columns = [f"{name} {absolute_result.delivery:%Y-%m-%d %H:%M}".strip()]
    # Create dataframe
    df = pd.DataFrame.from_records(
        ((item.value,) for item in absolute_result.items),
        columns=columns,
        index=[
            item.instance.as_dataframe_column_header() for item in absolute_result.items
        ],
    )
    df.index.name = "instance"
    return df
