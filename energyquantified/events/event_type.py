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

    CURVE_UPDATE = ("CURVE_UPDATE", "Curve Update")
    CURVE_DELETE = ("CURVE_DELETE", "Curve Delete")
    CURVE_TRUNCATE = ("CURVE_TRUNCATE", "Curve Truncate")

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