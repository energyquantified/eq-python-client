import uuid
import re
from energyquantified.events import EventCurveOptions, EventFilterOptions, CurveEventFilters

def assert_uuid(id, version=None):
    assert isinstance(id, uuid.UUID)
    if version is not None:
        assert id.version == version, f"Expected uuid version 4, got: {id.version}"

def assert_last_id(id):
    assert isinstance(id, str), "'last_id' must be a str"
    re.match
    assert re.fullmatch("^\\d{13}-{1}\\d+$", id), (
        f"Invalid last_id format: '{id}'. "
        f"Expected two numbers separated by a dash ('-'), where the first number is exactly 13 digits long.")

def assert_filters(filters):
    assert isinstance(filters, list)
    for filter in filters:
        assert isinstance(filter, (EventFilterOptions, EventCurveOptions)), f"filter must be type EventFilterOptions or EventCurveOptions"
        is_valid, errors = filter.validate()
        assert is_valid, f"fitler: {filter} is not valid for the following reason(s): {errors}"
    