from enum import Enum

_event_lookup = {}

class EventType(Enum):
    """
    A field in a CurveUpdateEvent object, also used for filtering
    events from the stream. Describes the data operation of an event.

     * ``UPDATE`` – Data is created or modified
     * ``DELETE`` – Data is deleted
     * ``TRUNCATE`` – All data for a curve is deleted
    """

    CURVE_UPDATE = ("CURVE_UPDATE", "Curve Update", True, False, False)
    CURVE_DELETE = ("CURVE_DELETE", "Curve Delete", True, False, False)
    CURVE_TRUNCATE = ("CURVE_TRUNCATE", "Curve Truncate", True, False, False)
    DISCONNECTED = ("DISCONNECTED", "Disconnected", False, True, False)
    TIMEOUT = ("TIMEOUT", "Timeout", False, False, True)

    def __init__(self, tag, label, is_curve_type, is_connection_type, is_timeout_type):
        self.tag = tag
        self.label = label
        self._is_curve_type = is_curve_type
        self._is_connection_type = is_connection_type
        self._is_timeout_type = is_timeout_type
        _event_lookup[tag.lower()] = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()
    
    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether an EventType tag exists or not.

        :param tag: The tag to look up (case-insensitive)
        :type tag: str
        :return: True if the EventType tag exists, otherwise False
        :rtype: bool
        """
        return isinstance(tag, str) and tag.lower() in _event_lookup

    @staticmethod
    def by_tag(tag):
        """
        Look up an EventType by tag.

        :param tag: The tag to look up (case-insensitive)
        :type tag: str
        :return: The EventType for this tag
        :rtype: EventType
        :raises KeyError: if no EventType exists for this tag
        """
        return _event_lookup[tag.lower()]

    @property
    def is_curve_type(self):
        return self._is_curve_type

    @property
    def is_connection_type(self):
        return self._is_connection_type

    @property
    def is_timeout_type(self):
        return self._is_timeout_type