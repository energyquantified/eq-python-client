from dataclasses import dataclass
from typing import Optional, List
from .messages.server.responses.curves_subscribe import CurvesSubscribeData
from .messages.server.responses.curves_filters import CurvesFiltersData

@dataclass(frozen=True)
class _Response:
    status: bool # TODO rename status to "ok"?
    errors: Optional[List[str]] = None

@dataclass(frozen=True)
class CurvesSubscribeResponse(_Response):
    data: Optional[CurvesSubscribeData] = None

@dataclass(frozen=True)
class CurvesFiltersResponse(_Response):
    data: Optional[CurvesFiltersData] = None
