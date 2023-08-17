from .base_request import _BaseRequest

class RequestCurvesFilters(_BaseRequest):
    @property
    def type(self):
        return "curves.filters"

    def __init__(self, request_id):
        super().__init__(request_id)

    def to_message(self):
        return super().to_message()