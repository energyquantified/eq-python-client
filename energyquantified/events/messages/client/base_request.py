from energyquantified.events.messages.constants import TYPE_FIELD
from energyquantified.events.messages.validations import assert_uuid

class _BaseRequest:
    TYPE_KEY = TYPE_FIELD
    REQUEST_ID_KEY = "request_id"

    def __init__(self, request_id):
        # Request id
        assert_uuid(request_id, version=4)
        self.request_id = request_id

    @property
    def type():
        raise NotImplementedError

    def to_message(self):
        return {
            self.TYPE_KEY: self.type,
            self.REQUEST_ID_KEY: str(self.request_id)
        }
