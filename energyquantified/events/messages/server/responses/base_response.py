import uuid
from enum import Enum
from energyquantified.events.messages.server.base import _BaseServerMessage
from energyquantified.events.event_options import (
    CurveAttributeFilter,
    CurveNameFilter,
)


_response_status_lookup = {}

class ResponseStatus(Enum):
    """
    A field in server responses. Indicates if the request succeeded or not.

     * ``OK`` – The request succeeded
     * ``ERROR`` – The request failed
    """
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


class ServerResponse(_BaseServerMessage):
    REQUEST_ID_KEY = "request_id"
    STATUS_KEY = "status"
    DATA_KEY = "data"
    ERRORS_KEY = "errors"

    def __init__(self):
        self.request_id = None
        self.status = None
        self.data = None
        self.errors = None

    @property
    def success(self):
        """
        Check if the request being responded to was successful or not.

        :return: True if status indicates success, otherwise False
        :rtype: bool
        """
        return self.status == ResponseStatus.OK

    @property
    def error(self):
        """
        Check if the request being responded to failed or not.

        :return: True if status indicates failure, else False
        :rtype: bool
        """
        return not self.success

    @staticmethod
    def from_message(_):
        raise NotImplementedError

    def _parse_message(self, json):
        self._set_status(json)
        self._set_request_id(json)
        if self.status == ResponseStatus.ERROR:
            self._set_errors(json)
        else:
            self._set_data(json)

    def _set_request_id(self, json):
        request_id = json.get(self.REQUEST_ID_KEY)
        if request_id is None:
            raise ValueError(
                f"Failed parsing StreamMessageResponse due to "
                f"missing field '{self.REQUEST_ID_KEY}'"
            )
        self.request_id = uuid.UUID(request_id, version=4)

    def _set_status(self, json):
        status_tag = json.get(self.STATUS_KEY)
        if not ResponseStatus.is_valid_tag(status_tag):
            raise ValueError(
                f"Failed parsing StreamMessageResponse due to invalid "
                f"status: {status_tag}"
            )
        self.status = ResponseStatus.by_tag(status_tag)

    def _set_data(self, _):
        raise NotImplementedError

    def _set_errors(self, json):
        errors = json.get(self.ERRORS_KEY)
        if errors is None:
            raise ValueError(
                f"Failed parsing stream response due to "
                f"missing field '{self.ERRORS_KEY}'"
            )
        if not isinstance(errors, list):
            raise ValueError(
                f"Failed parsing stream response, "
                f"expected field '{self.ERRORS_KEY}' to be a list"
                )
        if not all(isinstance(err, str) for err in errors):
            raise ValueError(
                f"Failed parsing stream response, expected all elements in "
                f"field '{self.ERRORS_KEY}' to be strings"
            )
        self.errors = errors

    def _parse_curve_filter(self, json):
        # Event type
        curves = json.get("curve_names")
        # Either CurveNameFilter or CurveAttributeFilter
        if curves is not None:
            return _parse_curve_options(json, curves)
        return _parse_filter_options(json)

def _parse_curve_options(json, curves):
    # CurveNameFilter
    options = CurveNameFilter().set_curves(curves)
    options = _parse_shared_options(json, options)
    return options

def _parse_filter_options(json):
    # CurveAttributeFilter
    options = CurveAttributeFilter()
    options = _parse_shared_options(json, options)
    # Areas
    areas = json.get("areas")
    if areas is not None:
        options.set_areas(areas)
    # Data types
    data_types = json.get("data_types")
    if data_types is not None:
        options.set_data_types(data_types)
    # Commodities
    commodities = json.get("commodities")
    if commodities is not None:
        options.set_commodities(commodities)
    # Categories
    categories = json.get("categories")
    if categories is not None:
        options.set_categories(categories)
    # Exact categories
    exact_categories = json.get("exact_categories")
    if exact_categories is not None:
        options.set_exact_categories(exact_categories)
    return options

def _parse_shared_options(json, options):
    # Variables in both CurveOption and FilterOptions
    # Event type
    event_types = json.get("event_types")
    if event_types is not None:
        options.set_event_types(event_types)
    # Begin
    begin = json.get("begin")
    if begin is not None:
        options.set_begin(begin)
    # End
    end = json.get("end")
    if end is not None:
        options.set_end(end)
    # Tags
    tags = json.get("tags")
    if tags is not None:
        options.set_tags(tags)
    # Exclude tags
    exclude_tags = json.get("exclude_tags")
    if exclude_tags is not None:
        options.set_exclude_tags(exclude_tags)
    return options
