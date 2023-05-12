from enum import Enum

_message_lookup = {}
class MessageType(Enum):
    """
    Type of response from event stream.
    """

    EVENT = ("EVENT", "Event")
    INFO = ("INFO", "Info")
    FILTERS = ("FILTERS", "Filters")
    ERROR = ("ERROR", "Error")
    TIMEOUT = ("TIMEOUT", "Timeout")
    DISCONNECTED = ("DISCONNECTED", "Disconnected")
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