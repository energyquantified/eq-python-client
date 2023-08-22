import uuid
from enum import Enum
from energyquantified.events.messages.server.base import _BaseServerMessage

_response_status_lookup = {}

class _ResponseStatus(Enum):
    OK = ("OK", "Ok")
    ERROR = ("ERROR", "Error")

    def __init__(self, tag, label):
        self.tag = tag
        self.label = label
        _response_status_lookup[tag.lower()] = self
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def is_valid_tag(tag):
        return isinstance(tag, str) and tag.lower() in _response_status_lookup

    @staticmethod
    def by_tag(tag):
        return _response_status_lookup[tag.lower()]

class _ServerResponse(_BaseServerMessage):
    REQUEST_ID_KEY = "request_id"
    STATUS_KEY = "status"
    DATA_KEY = "data"
    ERRORS_KEY = "errors"

    def __init__(self):
        self.request_id = None
        self.status = None
        self.data = None
        self.errors = None

    @staticmethod
    def from_message(_):
        raise NotImplementedError

    def _parse_message(self, json):
        self._set_status(json)
        self._set_request_id(json)
        if not self.status:
            self._set_errors(json)
        else:
            self._set_data(json)

    def _set_request_id(self, json):
        # TODO how to handle if server failed to parse request_id (and how to know)
        request_id = json.get(self.REQUEST_ID_KEY)
        if request_id is None:
            raise ValueError(f"Failed parsing StreamMessageResponse due to missing field '{self.REQUEST_ID_KEY}'")
        self.request_id = uuid.UUID(request_id, version=4)

    def _set_status(self, json):
        status_tag = json.get(self.STATUS_KEY)
        if not _ResponseStatus.is_valid_tag(status_tag):
            raise ValueError(f"Failed parsing StreamMessageResponse due to invalid status: {status_tag}")
        self.status = _ResponseStatus.by_tag(status_tag) == _ResponseStatus.OK

    def _set_data(self, _):
        raise NotImplementedError

    def _set_errors(self, json):
        errors = json.get(self.ERRORS_KEY)
        if errors is None:
            raise ValueError(f"Failed parsing stream response due to missing field '{self.ERRORS_KEY}'")
        if not isinstance(errors, list):
            raise ValueError(f"Failed parsing stream response, expected field '{self.ERRORS_KEY}' to be a list")
        if not all(isinstance(err, str) for err in errors):
            raise ValueError(f"Failed parsing stream response, expected all elements in field '{self.ERRORS_KEY}' to be strings")
        self.errors = errors