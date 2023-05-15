from enum import Enum

_message_lookup = {}
class MessageType(Enum):
    """
    Describes the type of response received when listening to
    the curve events stream. It is the first element in the
    tuple of two elements returned from ``get_next()``, and
    describes the second element.
    
    See also :py:meth:`get_next() <energyquantified.api.CurveUpdateEventAPI.get_next>`.

     * ``EVENT`` – A curve event (type: :py:class:`energyquantified.events.CurveUpdateEvent`)
     * ``INFO`` – An informative message (type: str)
     * ``FILTERS`` – List of filters (type:\
            [:py:class:`energyquantified.events.EventCurveOptions` | \
            :py:class:`energyquantified.events.EventFilterOptions`])
     * ``ERROR`` – Informative error message from the stream (type: str)
     * ``TIMEOUT`` – No new messages or events received (type: None)
     * ``DISCONNECTED`` – A connection event\
            (type: :py:class:`energyquantified.events.ConnectionEvent`)
    """
    EVENT = ("EVENT", "Event")
    INFO = ("INFO", "Info")
    FILTERS = ("FILTERS", "Filters")
    ERROR = ("ERROR", "Error")
    TIMEOUT = ("TIMEOUT", "Timeout")
    DISCONNECTED = ("DISCONNECTED", "Disconnected")

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