from dataclasses import dataclass
from typing import Optional, List
from typing import Union
from .event_options import CurveNameFilter, CurveAttributeFilter

@dataclass(frozen=True)
class BaseServerResponse:
    """
    Base model for push feed responses. The ``status`` of a response indicates
    if the request being responded to was successful or not. One of
    ``errors`` and ``data`` (included by child classes) is always None
    and the other is set. If status is False (request failed) then ``errors``
    is set and ``data`` is None, otherwise (request succeded) ``errors`` is set
    and ``data`` is None.
    """
    #: Status of the request being responded to; True if the request succeeded,
    #: otherwise False.
    status: bool
    #: A list of errors messages describing reason of failure. Is None if
    #: ``status`` is True (request succeeded).
    errors: Optional[List[str]] = None

    @property
    def status_ok(self):
        return self.status is True

    @property
    def ok(self):
        return self.status is True

    @property
    def success(self):
        return self.status is True

    @property
    def failed(self):
        return self.status is False


@dataclass(frozen=True)
class CurvesSubscribeData:
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
    #: with the filters and event ID used for subscribing. Is None if ``status``
    #: is False (subscribe failed).
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
    #: with the active curve event filters. Is None if ``status``
    #: is False (request failed).
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
