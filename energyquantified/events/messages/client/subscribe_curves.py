from energyquantified.events.messages.validations import assert_last_id, assert_filters
from .base_request import _BaseRequest

class RequestCurvesSubscribe(_BaseRequest):
    LAST_ID_KEY = "last_id"
    FILTERS_KEY = "filters"

    @property
    def type(self):
        return "curves.subscribe"

    def __init__(self, request_id, last_id=None, filters=None):
        super().__init__(request_id)
        # Last id
        if last_id is not None:
            assert_last_id(last_id)
        self.last_id = last_id
        # Filters
        if filters is not None:
            assert_filters(filters)
        self.filters = filters

    def to_message(self):
        msg = super().to_message()
        if self.last_id is not None:
            msg[self.LAST_ID_KEY] = self.last_id
        if self.filters is not None:
            msg[self.FILTERS_KEY] = [curve_filter.to_dict() for curve_filter in self.filters]
        return msg
