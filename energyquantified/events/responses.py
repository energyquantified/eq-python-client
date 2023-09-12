from dataclasses import dataclass
from typing import Optional, List
from typing import Union
from .event_options import CurveNameFilter, CurveAttributeFilter


@dataclass(frozen=True)
class CurvesSubscribeResponse:
    """
    Response model from successfully subscribing to curve events.
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
        last_id_str = f"last_id={self.last_id}, " if self.last_id is not None else ''
        return (
            f"<CurvesSubscribeData: "
            f"{last_id_str}"
            f"filters={self.filters}"
            f">"
        )

    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class CurvesFiltersResponse:
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
