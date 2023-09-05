from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from typing import Union
from .event_options import CurveNameFilter, CurveAttributeFilter


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


@dataclass(frozen=True)
class BaseServerResponse:
    """
    Base model for push feed responses. The ``status`` of a response indicates
    if the request being responded to was successful or not. One of
    ``errors`` and ``data`` (included in child classes) is always None
    and the other is set. If the request failed then ``errors`` is set and
    ``data`` is None, otherwise (request succeded) ``errors`` is set and
    ``data`` is None. Check the status through the properties
    :py:attr:`BaseServerresponse.success <energyquantified.events.responses.BaseServerResponse.success>`
    and
    :py:attr:`BaseServerresponse.error <energyquantified.events.responses.BaseServerResponse.error>`
    .
    """
    #: Status of the request being responded to; ResponseStatus.OK if the
    #: request succeeded, otherwise ResponseStatus.ERROR. Quickly check the
    #: status with ``success`` and ``error`` properties.
    status: ResponseStatus
    #: A list of errors messages describing reason of failure. Is None if
    #: the request succeeded (see
    #: :py:attr:`BaseServerResponse.success <energyquantified.events.responses.BaseServerResponse.success>`
    #: ).
    errors: Optional[List[str]] = None

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


@dataclass(frozen=True)
class CurvesSubscribeData:
    """
    Response model from a successful subscribe to curve events.
    """
    #: A list of filters subscribed to, confirmed by the server.
    filters: List[Union[CurveAttributeFilter, CurveNameFilter]]
    #: The event ID subscribed from. None if it was not incldued in the
    #: subscribe request.
    last_id: Optional[str] = None

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


@dataclass(frozen=True)
class CurvesSubscribeResponse(BaseServerResponse):
    """
    Response model from subscribing to curve events. See also
    :py:class:`~energyquantified.events.responses.BaseServerResponse`.
    """
    #: A :py:class:`energyquantified.events.CurvesSubscribeData` object
    #: with the filters and event ID used for subscribing. Is None if the
    #: request failed (see
    #: :py:attr:`CurvesSubscribeResponse.error <energyquantified.events.CurvesSubscribeResponse.error>`
    #: ).
    data: Optional[CurvesSubscribeData] = None

    def __str__(self):
        return (
            f"<CurvesSubscribeResponse: "
            f"status={self.status}, "
            f"data={self.data}, "
            f"errors={self.errors}"
            f">"
        )

    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class CurvesFiltersData:
    """
    Response model from requesting active curve event filters.
    """
    #: List of active curve event filters from the server. Is None if not
    #: subscribed.
    filters: Optional[List[Union[CurveAttributeFilter, CurveNameFilter]]] = None

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


@dataclass(frozen=True)
class CurvesFiltersResponse(BaseServerResponse):
    """
    Response model from requesting active curve filters. See also
    :py:class:`~energyquantified.events.responses.BaseServerResponse`.
    """
    #: A :py:class:`energyquantified.events.CurvesFiltersData` object
    #: with the active curve event filters. Is None if the
    #: request failed (see
    #: :py:attr:`CurvesFiltersResponse.error <energyquantified.events.CurvesFiltersResponse.error>`
    #: ).
    data: Optional[CurvesFiltersData] = None

    def __str__(self):
        return (
            f"<CurvesFiltersResponse: "
            f"status={self.status}, "
            f"data={self.data}, "
            f"errors={self.errors}"
            f">"
        )

    def __repr__(self):
        return self.__str__()
