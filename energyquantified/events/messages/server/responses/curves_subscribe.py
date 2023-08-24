from dataclasses import dataclass
from typing import Optional, List, Union
from energyquantified.events import EventFilterOptions, EventCurveOptions
from .base_response import _ServerResponse

@dataclass(frozen=True)
class CurvesSubscribeData:
    last_id: Optional[str] = None
    filters: Optional[List[Union[EventFilterOptions, EventCurveOptions]]] = None

    def has_last_id(self):
        return self.last_id is not None

    def has_filters(self):
        return self.filters is not None
    
    def __str__(self):
        return (
            f"<CurvesSubscribeData: "
            f"last_id={self.last_id}, "
            f"filters={self.filters}"
            f">"
        )

    def __repr__(self):
        return self.__str__()

class ServerResponseCurvesSubscribe(_ServerResponse):
    DATA_FILTERS_KEY = "filters"
    DATA_LAST_ID_KEY = "last_id"

    @staticmethod
    def from_message(json):
        response_obj = ServerResponseCurvesSubscribe()
        response_obj._parse_message(json)
        return response_obj

    def _set_data(self, json):
        data_obj = json.get(self.DATA_KEY)
        if data_obj is None:
            raise ValueError(f"Failed parsing response from stream, missing field '{self.DATA_KEY}'")
        # Last id
        last_id = data_obj.get(self.DATA_LAST_ID_KEY)
        # Filters
        filters = data_obj.get(self.DATA_FILTERS_KEY)
        if filters is not None:
            filters = [self._parse_curve_filter(filter) for filter in filters]
        self.data = CurvesSubscribeData(last_id=last_id, filters=filters)