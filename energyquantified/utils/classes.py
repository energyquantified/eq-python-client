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

_absolute_result_class = None
def _get_absolute_result_class():
    """
    Private utility function for lazy-loading the AbsoluteResult class.

    :return: The AbsoluteResult class
    :rtype: class
    """
    global _absolute_result_class
    if not _absolute_result_class:
        from energyquantified.data import AbsoluteResult
        _absolute_result_class = AbsoluteResult
    return _absolute_result_class