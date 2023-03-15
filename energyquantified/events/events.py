from enum import Enum
from energyquantified.metadata import CurveType
from energyquantified.parser.metadata import parse_curve, parse_instance
from energyquantified.exceptions import APIError
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class DisconnectEvent:
    status_code: int
    message: Optional[str] = None


_message_lookup = {}
class MessageType(Enum):
    """
    Type of response from event stream.
    """

    EVENT = ("EVENT", "Event")
    INFO = ("INFO", "Info")
    FILTERS = ("FILTERS", "Filters")
    TIMEOUT = ("TIMEOUT", "Timeout")
    MESSAGE = ("MESSAGE", "Message") # TODO fix var naming
    DISCONNECT = ("DISCONNECT", "Disconnect")
    UNAVAILABLE = ("UNAVAILABLE", "Unavailable")

    def __init__(self, tag=None, label=None):
        self.tag = tag
        self.label = label
        _message_lookup[tag.lower()] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def is_valid_tag(tag):
        return tag.lower() in _message_lookup

    @staticmethod
    def by_tag(tag):
        return _message_lookup[tag.lower()]

_event_lookup = {}
class EventType(Enum):

    CREATE = ("CREATE", "Create")
    UPDATE = ("UPDATE", "Update")
    DELETE = ("DELETE", "Delete")
    TRUNCATE = ("TRUNCATE", "Truncate")

    def __init__(self, tag=None, label=None):
        self.tag = tag
        self.label = label
        _event_lookup[tag.lower()] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def is_valid_tag(tag):
        return tag.lower() in _event_lookup

    @staticmethod
    def by_tag(tag):
        return _event_lookup[tag.lower()]

class CurveUpdateEvent:
    def __init__(
        self,
        event_id,
        curve,
        event_type,
        begin = None,
        end = None,
        instance = None,
        num_values = None,
    ):
        self.event_id = event_id
        self.curve = curve
        self.event_type = event_type
        self.begin = begin
        self.end = end
        self.instance = instance
        self.num_values = num_values
    
    def __str__(self):
        begin_str = self.begin.isoformat(sep=" ") if self.begin is not None else None
        end_str = self.end.isoformat(sep=" ") if self.end is not None else None
        return (
            f"<CurveUpdateEvent: "
            f"event_id={self.event_id}, "
            f"curve={self.curve}, "
            f"event_type={self.event_type}, "
            f"begin={begin_str}, "
            f"end={end_str}, "
            f"instance={self.instance}, "
            f"num_values:{self.num_values}"
            f">"
        )

    def __repr__(self):
        return self.__str__()

    def load_data(self, eq):
        try:
            data = self._load_data(eq)
        except APIError as e:
            # TODO
            data = e
        return data
        
    def _load_data(self, eq):
        if self.event_type in [EventType.TRUNCATE, EventType.DELETE]:
            print(f"Can't load data for {self.event_type} event")
            return None
        # Timeseries and scenarios
        if self.curve.curve_type in [CurveType.TIMESERIES, CurveType.SCENARIO_TIMESERIES]:
            return eq.timeseries.load(
                self.curve,
                begin=self.begin,
                end=self.end,
                )
        # Instance
        if self.curve.curve_type == CurveType.INSTANCE:
            return eq.instances.get(
                self.curve,
                issued=self.instance.issued,
                tag=self.instance.tag,
                )
        # Periods
        if self.curve.curve_type == CurveType.PERIOD:
            assert not self.curve.frequency.is_iterable
            # Periods
            return eq.periods.load(
                self.curve,
                begin=self.begin,
                end=self.end,
                )
        # Instance periods
        if self.curve.curve_type == CurveType.INSTANCE_PERIOD:
            assert self.instance is not None
            assert not self.curve.frequency.is_iterable
            # InstancePeriod
            return eq.period_instances.get(
                self.curve,
                begin=self.begin,
                end=self.end,
                issued=self.instance.issued,
                tag=self.instance.tag,
                )
        # OHLC
        if self.curve.curve_type == CurveType.OHLC:
            return eq.ohlc.load(
                self.curve, 
                begin=self.begin, 
                end=self.end,
                )
