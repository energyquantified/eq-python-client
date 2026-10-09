from .classes import (
    _get_absolute_result_class,
    _get_ohlc_list_class,
    _get_ppa_list_class,
    _get_timeseries_class,
    _get_trade_ohlc_series_class,
    _get_trade_ohlc_series_list_class,
    _get_value_type_class,
)

INDEX_NAME = "date"
DEFAULT_COLUMN_NAME = "value"
PERIOD_COLUMNS = [
    "begin",
    "end",
    "value",
    "capacity",
]

pl = None
_is_polars_installed = None


def is_polars_installed():
    """
    Private utility to both lazy-load and to check if polars is installed.

    :return: True when polars is available on the system, otherwise False
    :rtype: bool
    """
    global pl, _is_polars_installed
    if _is_polars_installed is None:
        try:
            import polars as pl

            _is_polars_installed = True
        except ImportError as e:
            _is_polars_installed = False
    return _is_polars_installed


def assert_polars_installed():
    """
    Assert that polars is installed.

    :raises ImportError: When polars is not installed on the system
    """
    if not is_polars_installed():
        if not is_polars_installed():
            raise ImportError(
                'You must install the "polars" data analysis library '
                "to use this functionality. Visit "
                "https://docs.pola.rs/ for more information."
            )


def timeseries_to_polars_dataframe(timeseries, name=None):
    """
    Convert a time series to a ``polars.DataFrame``.

    NOTE: Polar dataframes do not have an index. Instead, we add a column named
    `date` with the datetimes.

    :param timeseries: The time series
    :type timeseries: energyquantified.data.Timeseries, required
    :param name: Set a custom name in the column header, Timeseries.curve.name \
        is used when this parameter is not set, defaults to None
    :type name: str, optional
    :return: A DataFrame
    :rtype: polars.DataFrame
    :raises ImportError: When polars is not installed on the system
    """
    # Checks
    assert_polars_installed()
    assert isinstance(timeseries, _get_timeseries_class()), (
        "timeseries must be an instance of energyquantified.data.Timeseries"
    )
    assert isinstance(name, (type(None), str)), (
        f"parameter name must be string or None, was {type(name)}"
    )
    if name is None:
        name = timeseries.name
        include_instance = True
        if name is None:
            name = DEFAULT_COLUMN_NAME
    else:
        include_instance = False
    # Conversion
    ValueType = _get_value_type_class()
    if timeseries.value_type() == ValueType.VALUE:
        # Convert a time series of (date, value)
        return _timeseries_to_dataframe_value(
            timeseries, name, include_instance=include_instance
        )
    if timeseries.value_type() == ValueType.SCENARIOS:
        # Convert a time series of (date, scenarios[])
        return _timeseries_to_dataframe_scenarios(
            timeseries, name, include_instance=include_instance
        )
    if timeseries.value_type() == ValueType.MEAN_AND_SCENARIOS:
        # Convert a time series of (date, value, scenarios[])
        return _timeseries_to_dataframe_mean_and_scenarios(
            timeseries, name, include_instance=include_instance
        )
    # Unknown value type for time series
    raise ValueError(
        f"Unknown ValueType: timeseries.value_type = {timeseries.value_type()}"
    )


def _timeseries_to_dataframe_value(timeseries, name, include_instance=True):
    """
    Private utility function for converting a time series of single values
    to a polars dataframe.

    :param timeseries: A time series object
    :type timeseries: Timeseries
    :param name: The time series name
    :type name: str
    :param include_instance: Include the instance in the header?
    :type include_instance: bool
    :return: A polars DataFrame
    :rtype: polars.DataFrame
    """
    # Column header
    if include_instance:
        instance = timeseries.instance_or_contract_dataframe_column_header()
        name = f"{name} {instance}".strip()
    # Convert a time series of (date, value)
    return pl.DataFrame(
        {
            INDEX_NAME: [value.date for value in timeseries],
            name: [value.value for value in timeseries],
        },
        schema={INDEX_NAME: pl.Datetime, name: pl.Float64},
    ).with_columns(
        pl.col(INDEX_NAME).dt.convert_time_zone(timeseries.resolution.timezone.zone)
    )


def _timeseries_to_dataframe_scenarios(timeseries, name, include_instance=True):
    """
    Private utility function for converting a time series of scenario values
    to a polars dataframe.

    :param timeseries: A time series object
    :type timeseries: Timeseries
    :param name: The time series name
    :type name: str
    :param include_instance: Include the instance in the header?
    :type include_instance: bool
    :return: A polars DataFrame
    :rtype: polars.DataFrame
    """
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
    return pl.DataFrame(
        {
            INDEX_NAME: [value.date for value in timeseries],
            **dict(
                zip(
                    columns,
                    [list(row) for row in zip(*[ts.scenarios for ts in timeseries])],
                )
            ),
        },
        schema={
            INDEX_NAME: pl.Datetime,
            **{col: pl.Float64 for col in columns},
        },
    ).with_columns(
        pl.col(INDEX_NAME).dt.convert_time_zone(timeseries.resolution.timezone.zone)
    )


def _timeseries_to_dataframe_mean_and_scenarios(
    timeseries, name, include_instance=True
):
    """
    Private utility function for converting a time series of a mean value
    and scenarios to a polars dataframe.

    :param timeseries: A time series object
    :type timeseries: Timeseries
    :param name: The time series name
    :type name: str
    :param include_instance: Include the instance in the header?
    :type include_instance: bool
    :return: A polars DataFrame
    :rtype: polars.DataFrame
    """
    # Column headers
    if include_instance:
        instance = timeseries.instance_or_contract_dataframe_column_header()
        mean_name = f"{name} {instance}".strip()
        columns = [
            f"{name} {instance} {scenario}".strip()
            for scenario in timeseries.scenario_names
        ]
    else:
        mean_name = f"{name}".strip()
        columns = [
            f"{name} {scenario}".strip() for scenario in timeseries.scenario_names
        ]
    # Convert a time series of (date, scenarios[])
    return pl.DataFrame(
        {
            INDEX_NAME: [value.date for value in timeseries],
            mean_name: [value.value for value in timeseries],
            **dict(
                zip(
                    columns,
                    [list(row) for row in zip(*[ts.scenarios for ts in timeseries])],
                )
            ),
        },
        schema={
            INDEX_NAME: pl.Datetime,
            mean_name: pl.Float64,
            **{col: pl.Float64 for col in columns},
        },
    ).with_columns(
        pl.col(INDEX_NAME).dt.convert_time_zone(timeseries.resolution.timezone.zone)
    )


def timeseries_list_to_polars_dataframe(timeseries_list):
    """
    Convert a list of time series to a ``polars.DataFrame``.

    :param timeseries_list: [description]
    :type timeseries_list: [type]
    :return: A polars DataFrame
    :rtype: polars.DataFrame
    """
    # Checks
    assert_polars_installed()
    assert timeseries_list, "timeseries list is empty"
    for index, timeseries in enumerate(timeseries_list):
        assert isinstance(timeseries, _get_timeseries_class()), (
            f"timeseries_list[{index}] must be an instance of "
            f"energyquantified.data.Timeseries, but was: {type(timeseries)}"
        )
    # Merge into one data frame
    df = timeseries_to_polars_dataframe(timeseries_list[0])
    for ts in timeseries_list[1:]:
        df = df.join(
            timeseries_to_polars_dataframe(ts),
            on=INDEX_NAME,
            how="outer",
            coalesce=True,
        )
    return df


def ohlc_list_to_polars_dataframe(ohlc_list):
    """
    Convert an :py:class:`energyquantified.data.OHLCList` to a
    ``polars.DataFrame``.

    :param ohlc_list: A list of OHLC objects
    :type ohlc_list: OHLCList
    :return: A DataFrame
    :rtype: polars.DataFrame
    :raises ImportError: When polars is not installed on the system
    """
    # Checks
    assert_polars_installed()
    assert isinstance(ohlc_list, _get_ohlc_list_class()), (
        "ohlc_list must be an instance of energyquantified.data.OHLCList"
    )
    # Conversion
    return pl.DataFrame(
        [
            pl.Series(
                "traded", [ohlc.product.traded for ohlc in ohlc_list], dtype=pl.Date
            ),
            pl.Series(
                "period",
                [ohlc.product.period.tag for ohlc in ohlc_list],
                dtype=pl.String,
            ),
            pl.Series(
                "front", [ohlc.product.front for ohlc in ohlc_list], dtype=pl.Int32
            ),
            pl.Series(
                "delivery", [ohlc.product.delivery for ohlc in ohlc_list], dtype=pl.Date
            ),
            pl.Series("open", [ohlc.open for ohlc in ohlc_list], dtype=pl.Float64),
            pl.Series("high", [ohlc.high for ohlc in ohlc_list], dtype=pl.Float64),
            pl.Series("low", [ohlc.low for ohlc in ohlc_list], dtype=pl.Float64),
            pl.Series("close", [ohlc.close for ohlc in ohlc_list], dtype=pl.Float64),
            pl.Series(
                "settlement", [ohlc.settlement for ohlc in ohlc_list], dtype=pl.Float64
            ),
            pl.Series("volume", [ohlc.volume for ohlc in ohlc_list], dtype=pl.Float64),
            pl.Series(
                "open_interest",
                [ohlc.open_interest for ohlc in ohlc_list],
                dtype=pl.Float64,
            ),
        ]
    )


def ppa_list_to_polars_dataframe(ppa_list):
    """
    Convert an :py:class:`energyquantified.data.PPAList` to a
    ``polars.DataFrame``.

    :param ppa_list: A list of PPA objects
    :type ppa_list: PPAList
    :return: A DataFrame
    :rtype: polars.DataFrame
    :raises ImportError: When polars is not installed on the system
    """
    # Checks
    assert_polars_installed()
    assert isinstance(ppa_list, _get_ppa_list_class()), (
        "ppa_list must be an instance of energyquantified.data.PPAList"
    )
    # Conversion
    return pl.DataFrame(
        [
            pl.Series("date", [ppa.product.date for ppa in ppa_list], dtype=pl.Date),
            pl.Series(
                "technology",
                [ppa.product.technology.tag for ppa in ppa_list],
                dtype=pl.String,
            ),
            pl.Series(
                "contract_structure",
                [ppa.product.contract_structure.tag for ppa in ppa_list],
                dtype=pl.String,
            ),
            pl.Series(
                "delivery_begin",
                [ppa.product.delivery_begin for ppa in ppa_list],
                dtype=pl.Date,
            ),
            pl.Series(
                "duration",
                [ppa.product.duration.years for ppa in ppa_list],
                dtype=pl.Int32,
            ),
            pl.Series("price", [ppa.price for ppa in ppa_list], dtype=pl.Float64),
        ]
    )


def absolute_result_to_polars_dataframe(absolute_result, name=None):
    """
    Convert an :py:class:`energyquantified.data.AbsoluteResult` to a
    ``polars.DataFrame``.

    :param absolute_result: The absolute result
    :type absolute_result: AbsoluteResult
    :param name: Set a name for the value column, defaults to None. Uses\
    the curve name if not set. The delivery date is appended to the name.
    :type name: str | None, optional
    :return: A DataFrame
    :rtype: polars.DataFrame
    :raises ImportError: When polars is not installed on the system
    """
    assert_polars_installed()
    assert isinstance(absolute_result, _get_absolute_result_class()), (
        "absolute_result must be an instance of energyquantified.data.AbsoluteResult"
    )
    assert isinstance(name, (type(None), str)), (
        f"parameter name must be string or None, was {type(name)}"
    )
    if name is None:
        name = absolute_result.curve.name
    # Create dataframe
    # TODO compare result with pandas
    return pl.DataFrame(
        {
            "instance": [
                item.instance.as_dataframe_column_header()
                for item in absolute_result.items
            ],
            f"{name} {absolute_result.delivery:%Y-%m-%d %H:%M}".strip(): [
                item.value for item in absolute_result.items
            ],
        }
    )


def trade_ohlc_series_to_polars_dataframe(series):
    """
    Convert an :py:class:`energyquantified.data.TradeOHLCSeries` to a
    ``polars.DataFrame``.

    The frame is in a flat, CSV-like layout with one row per trading-time
    bucket and columns for the contract (``period`` and ``delivery``), the
    ``traded_at`` bucket, and the OHLC fields.

    :param series: A trade OHLC series
    :type series: TradeOHLCSeries
    :return: A DataFrame
    :rtype: polars.DataFrame
    :raises ImportError: When polars is not installed on the system
    """
    # Checks
    assert_polars_installed()
    assert isinstance(
        series, _get_trade_ohlc_series_class()
    ), "series must be an instance of energyquantified.data.TradeOHLCSeries"
    # Conversion
    return _trade_ohlc_polars_dataframe([series])


def trade_ohlc_series_list_to_polars_dataframe(series_list):
    """
    Convert an :py:class:`energyquantified.data.TradeOHLCSeriesList` to a
    ``polars.DataFrame``.

    The frame is in a flat, CSV-like layout with one row per contract and
    trading-time bucket and columns for the contract (``period`` and
    ``delivery``), the ``traded_at`` bucket, and the OHLC fields.

    :param series_list: A list of trade OHLC series
    :type series_list: TradeOHLCSeriesList
    :return: A DataFrame
    :rtype: polars.DataFrame
    :raises ImportError: When polars is not installed on the system
    """
    # Checks
    assert_polars_installed()
    assert isinstance(
        series_list, _get_trade_ohlc_series_list_class()
    ), (
        "series_list must be an instance of "
        "energyquantified.data.TradeOHLCSeriesList"
    )
    # Conversion
    return _trade_ohlc_polars_dataframe(series_list)


def _trade_ohlc_polars_dataframe(series_iterable):
    periods = []
    deliveries = []
    traded_at = []
    opens = []
    highs = []
    lows = []
    closes = []
    vwaps = []
    volumes = []
    counts = []
    for series in series_iterable:
        contract = series.contract
        period = contract.period.tag if contract else None
        delivery = contract.delivery if contract else None
        for ohlc in series.data:
            periods.append(period)
            deliveries.append(delivery)
            traded_at.append(ohlc.traded_at)
            opens.append(ohlc.open)
            highs.append(ohlc.high)
            lows.append(ohlc.low)
            closes.append(ohlc.close)
            vwaps.append(ohlc.vwap)
            volumes.append(ohlc.volume)
            counts.append(ohlc.count)
    return pl.DataFrame(
        [
            pl.Series("period", periods, dtype=pl.String),
            pl.Series("delivery", deliveries, dtype=pl.Datetime),
            pl.Series("traded_at", traded_at, dtype=pl.Datetime),
            pl.Series("open", opens, dtype=pl.Float64),
            pl.Series("high", highs, dtype=pl.Float64),
            pl.Series("low", lows, dtype=pl.Float64),
            pl.Series("close", closes, dtype=pl.Float64),
            pl.Series("vwap", vwaps, dtype=pl.Float64),
            pl.Series("volume", volumes, dtype=pl.Float64),
            pl.Series("count", counts, dtype=pl.Int64),
        ]
    )
