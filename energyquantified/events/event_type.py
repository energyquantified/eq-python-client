from enum import Enum

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