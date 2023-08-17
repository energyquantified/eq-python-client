from dataclasses import dataclass
from typing import Optional, List, Union
from energyquantified.events import EventFilterOptions, EventCurveOptions
from energyquantified.events.parser import _parse_event_options
from .base_response import _ServerResponse

@dataclass(frozen=True)
class CurvesFiltersData:
    filters: Optional[List[Union[EventFilterOptions, EventCurveOptions]]] = None

    def has_filters(self):
        return self.filters is not None

class ServerResponseCurvesFilters(_ServerResponse):
    DATA_FILTERS_KEY = "filters"

    @staticmethod
    def from_message(json):
        response_obj = ServerResponseCurvesFilters()
        response_obj._parse_message(json)

    def _set_data(self, json):
        data_obj = json.get(self.DATA_KEY)
        if data_obj is None:
            raise ValueError(f"Failed parsing response from stream, missing field '{self.DATA_KEY}'")
        # Parse filters
        filters = data_obj.get(self.DATA_FILTERS_KEY)
        if filters is not None:
            filters = [_parse_event_options(filter for filter in filters)]
        self.data = CurvesFiltersData(filters=filters)
