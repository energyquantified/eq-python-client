from dataclasses import dataclass
from typing import Optional, List
from energyquantified.events.messages.server.responses import CurvesSubscribeData, CurvesFiltersData

@dataclass(frozen=True)
class _Response:
    """
    Base model for push feed responses.
    """
    status: bool
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
class CurvesSubscribeResponse(_Response):
    """
    Response model from subscribing to curve events.
    """
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
class CurvesFiltersResponse(_Response):
    """
    Response model from requesting currently active curve filters.
    """
    data: Optional[CurvesFiltersData] = None

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