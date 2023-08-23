from dataclasses import dataclass
from typing import Optional, List, Union
from energyquantified.events import EventFilterOptions, EventCurveOptions
from .base_response import _ServerResponse

@dataclass(frozen=True)
class CurvesFiltersData:
    filters: Optional[List[Union[EventFilterOptions, EventCurveOptions]]] = None

    def has_filters(self):
        return self.filters is not None

    def __str__(self):
        return (
            f"<CurvesFiltersData: "
            f"filters={self.filters}"
            f">"
        )
    def __repr__(self):
        return self.__str__()

class ServerResponseCurvesFilters(_ServerResponse):
    DATA_FILTERS_KEY = "filters"

    @staticmethod
    def from_message(json):
        response_obj = ServerResponseCurvesFilters()
        response_obj._parse_message(json)
        return response_obj

    def _set_data(self, json):
        data_obj = json.get(self.DATA_KEY)
        if data_obj is None:
            raise ValueError(f"Failed parsing response from stream, missing field '{self.DATA_KEY}'")
        # Parse filters
        filters = data_obj.get(self.DATA_FILTERS_KEY)
        if filters is not None:
            filters = [self._parse_curve_filter(filter for filter in filters)]
        self.data = CurvesFiltersData(filters=filters)
