from dataclasses import dataclass

from ..metadata import Area, Curve
from .ohlc import OHLCList
from .timeseries import Timeseries
from .periodseries import Periodseries

@dataclass(frozen=True)
class SRMCOptions:
    """
    A data class with all factors for an SRMC calculations.
    """
    fuel_type: str = None
    api2_tonne_to_mwh: float = None
    gas_therm_to_mwh: float = None
    hhv_to_lhv: float = None
    efficiency: float = None
    carbon_emissions: float = None
    carbon_tax_area: Area = None

    def __str__(self):
        if self.fuel_type == 'GAS':
            return (
                f"<SRMCOptions: {self.fuel_type}, "
                f"gas_therm_to_mwh={self.gas_therm_to_mwh}, "
                f"hhv_to_lhv={self.hhv_to_lhv}, "
                f"efficiency={self.efficiency}, "
                f"carbon_emissions={self.carbon_emissions}, "
                f"carbon_tax_area={self.carbon_tax_area}"
                f">"
            )
        elif self.fuel_type == 'COAL':
            return (
                f"<SRMCOptions: {self.fuel_type}, "
                f"api2_tonne_to_mwh={self.api2_tonne_to_mwh}, "
                f"efficiency={self.efficiency}, "
                f"carbon_emissions={self.carbon_emissions}, "
                f"carbon_tax_area={self.carbon_tax_area}"
                f">"
            )
        else:
            raise ValueError("fuel_type must be either GAS or COAL")

    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class SRMC:
    """
    A data class for the API response from an SRMC calculation. It can
    either contain a list of OHLC objects, a time series, or a period-based
    series.
    """
    curve: Curve = None
    contract: Contract = None
    options: SRMCOptions = None
    ohlc: OHLCList = None
    timeseries: Timeseries = None
    periodseries: Periodseries = None

    def has_ohlc(self):
        """
        Check whether this SRMC calculation did return OHLC objects.

        :return: True when this SRMC calculation did return OHLC objects,\
            otherwise False
        :rtype: bool
        """
        return self.ohlc is not None

    def has_timeseries(self):
        """
        Check whether this SRMC calculation did return a time series.

        :return: True when this SRMC calculation did return a time series,\
            otherwise False
        :rtype: bool
        """
        return self.timeseries is not None

    def has_periodseries(self):
        """
        Check whether this SRMC calculation did return a period-based series.

        :return: True when this SRMC calculation did return a period-based\
            series, otherwise False
        :rtype: bool
        """
        return self.periodseries is not None

    def __str__(self):
        if self.has_ohlc():
            return f"<SRMCResponse: ohlc={self.ohlc}, options={self.options}>"
        if self.has_timeseries():
            return f"<SRMCResponse: timeseries={self.timeseries}, options={self.options}>"
        if self.has_periodseries():
            return f"<SRMCResponse: periodseries={self.periodseries}, options={self.options}>"

    def __repr__(self):
        return self.__str__()