from energyquantified.events.responses import CurvesFiltersResponse
from .base_response import ServerResponse


class ServerResponseCurvesFilters(ServerResponse):
    DATA_FILTERS_KEY = "filters"

    @staticmethod
    def from_message(json):
        response_obj = ServerResponseCurvesFilters()
        response_obj._parse_message(json)
        return response_obj

    def _set_data(self, json):
        data_obj = json.get(self.DATA_KEY)
        if data_obj is None:
            raise ValueError(
                f"Failed parsing response from stream, "
                f"missing field '{self.DATA_KEY}'"
            )
        # Parse filters
        filters = data_obj.get(self.DATA_FILTERS_KEY)
        if filters is not None:
            filters = [self._parse_curve_filter(filter) for filter in filters]
        self.data = CurvesFiltersResponse(filters=filters)
