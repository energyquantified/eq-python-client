import json
import uuid
from datetime import datetime, date
from dateutil.parser import isoparse

from energyquantified.metadata.curve import Curve, DataType
from energyquantified.metadata.area import Area
from . import EventType

class CurveEventFilters:
    """
    Class for holding multiple filters and an event id.
    """
    def __init__(self):
        self.last_id = None
        self.filters = []

    def __str__(self):
        """
        Represent this object as a string, excluding not-set values.

        :return: A string representation of this object
        :rtype: str
        """
        str_list = []
        if self.has_last_id():
            str_list.append(f"last_id={self.last_id}")
        if self.has_filters():
            str_list.append(f"filters={self.filters}")
        return (
            f"<CurveEventFilters: "
            f"{', '.join(str_list)}"
            f">"
        )

    def __repr__(self):
        return self.__str__()

    def set_request_id(self, request_id): # TODO
        """
        Set the request id in this filter.

        :param request_id: The request id
        :type request_id: uuid v4 | str (in valid uuid v4 format)
        :raises AssertionError: Invalid request_id type
        :raises AssertionError: Invalid request_id format
        :return: CurveEventFilters
        :rtype: The instance this method was invoked upon
        """
        if request_id is None:
            self.request_id = None
            return self
        if isinstance(request_id, str):
            try:
                request_id = uuid.UUID(request_id, version=4)
            except ValueError:
                raise AssertionError(
                    "str request_id cannot be parsed to uuid v4 due to invalid format"
                    )
            except Exception as _:
                raise AssertionError("Failed to parse uuid from str request_id")
        assert isinstance(request_id, uuid.UUID), "request_id must be type uuid"
        assert request_id.version == 4, "request_id must be uuid v4"
        self.request_id = request_id
        return self

    def has_last_id(self):
        return self.last_id is not None

    def set_last_id(self, last_id):
        """
        Set the last_id in this filter.

        :param last_id: The id
        :type last_id: str
        :return: CurveEventFilters
        :rtype: The instance this method was invoked upon
        """
        assert last_id is None or isinstance(last_id, str), "last_id must be type str (or None)"
        self.last_id = last_id
        return self

    def has_filters(self):
        if not isinstance(self.filters, list):
            return False
        return len(self.filters) > 0

    def set_filters(self, filters):
        """
        Set the filters in this filter. Can be a single filter
        or a list of filters.

        :param filters: The filter(s)
        :type filters: list[EventCurveOptions | EventFilterOptions]
        :return: CurveEventFilters
        :rtype: The instance this method was invoked upon
        """
        if not isinstance(filters, list):
            filters = [filters]
        assert all(
            isinstance(filter, (EventCurveOptions, EventFilterOptions))
            for filter in filters), (
            "All objects in 'filters' must be type EventCurveOptions or EventFilterOptions"
            )
        self.filters = filters
        return self

    def validate(self):
        """
        Check the validity of this filter and discover reasons if invalid.

        :return: A tuple of two objects; (1) a bool representing the validity of\
            the object and (2) a list of potential errors.
        :rtype: tuple[bool, list[str]]
        """
        errors = []
        # Last (event) id
        if self.has_last_id():
            if not isinstance(self.last_id, str):
                errors.append("'last_id' must be type str (or None)")
        # Check all filters
        for filter in self.filters:
            # Check type
            if not isinstance(filter, (EventCurveOptions, EventFilterOptions)):
                errors.append(
                    f"objects in 'filters' must be type EventCurveOptions "
                    f"or EventFitlerOptions, found: {filter} with type {type(filter)}"
                )
            else: # Validate each filter
                filter_is_valid, filter_errors = filter.validate()
                if not filter_is_valid:
                    errors.append(
                        f"Filters contains an invalid filter: {filter}. "
                        f"Invalid for the following reasons: {filter_errors}"
                    )
        return len(errors) == 0, errors

class _BaseEventOptions:
    """
    Base class with filters shared between EventCurveOptions and EventFilterOptions. This includes
    begin, end, and event_types.
    """

    def __init__(self, begin=None, end=None, event_types=None):
        self._begin = None
        self._end = None
        self._event_types = None
        if begin:
            self.set_begin(begin)
        if end:
            self.set_end(end)
        if event_types:
            self.set_event_types(event_types)

    def has_begin(self):
        return self._begin is not None

    def set_begin(self, begin):
        """
        Set the filters 'begin'. The begin/end range regards the data an event
        describes, not to be confused with created time of the event.

        :param begin: Start of range
        :type begin: str, date, datetime
        :raises ValueError: Invalid arg type
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventCurveOptions` | \
                :py:class:`energyquantified.events.EventFilterOptions`
        """
        if isinstance(begin, str):
            begin = isoparse(begin)
        if isinstance(begin, date):
            if not isinstance(begin, datetime):
                begin = datetime.combine(begin, datetime.min.time())
        else:
            raise ValueError("begin must be a date, datetime, or an isoformatted string")
        self._begin = begin
        return self

    def has_end(self):
        return self._end is not None

    def set_end(self, end):
        """
        Set the filters 'end'. The begin/end range regards the data an event
        describes, not to be confused with the created time of the event.

        :param end: End of range
        :type end: str, date, datetime
        :raises ValueError: Invalid arg type
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventCurveOptions` | \
                :py:class:`energyquantified.events.EventFilterOptions`
        """
        if isinstance(end, str):
            end = isoparse(end)
        if isinstance(end, date):
            if not isinstance(end, datetime):
                end = datetime.combine(end, datetime.min.time())
        else:
            raise ValueError("end must be a date, datetime, or an isoformatted string")
        self._end = end
        return self

    def has_event_types(self):
        if not isinstance(self._event_types, list):
            return False
        return len(self._event_types) > 0

    def set_event_types(self, event_types):
        """
        Set one or more EventTypes in this filter, excluding events not matching
        at least one.

        :param event_types: EventTypes (optionally by tag) to include
        :type event_types: list[EventType, str]
        :raises ValueError: Invalid arg type
        :raises ValueError: Invalid event tag
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventCurveOptions` | \
                :py:class:`energyquantified.events.EventFilterOptions`
        """
        new_event_types = set()
        if not isinstance(event_types, (list, tuple, set)):
            event_types = [event_types]
        for event_type in event_types:
            if isinstance(event_type, str):
                if not EventType.is_valid_tag(event_type):
                    raise ValueError(f"EventType not found for tag: {event_type}")
                event_type = EventType.by_tag(event_type)
            if not isinstance(event_type, EventType):
                raise ValueError(f"'{event_type}' is not type 'EventType' or 'str'")
            new_event_types.add(event_type)
        self._event_types = list(new_event_types)
        return self

    def to_json(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def _to_dict(self, include_not_set=False):
        filters = {}
        # Event types
        if self.has_event_types():
            filters["event_types"] = list(event_type.tag for event_type in self._event_types)
        elif include_not_set:
            filters["event_types"] = None
        # Begin
        if self.has_begin():
            filters["begin"] = self._begin.isoformat(sep=" ")
        elif include_not_set:
            filters["begin"] = None
        # End
        if self.has_end():
            filters["end"] = self._end.isoformat(sep=" ")
        elif include_not_set:
            filters["end"] = None
        return filters

    def validate(self):
        raise NotImplementedError
    
    def _validate(self):
        errors = []
        if self.has_begin():
            if not isinstance(self._begin, datetime):
                errors.append("'begin' is not a datetime")
        if self.has_end():
            if not isinstance(self._end, datetime):
                errors.append("'end' is not a datetime")
        if self.has_event_types():
            if not all(isinstance(event_type, EventType) for event_type in self._event_types):
                errors.append("All objects in 'event_types' must be type EventType")
        return len(errors) == 0, errors


class EventCurveOptions(_BaseEventOptions):
    """
    In addition to the inherited filters (begin, end, event_type), 
    this option provides filtering on exact curve_names(s).
    """

    def __init__(
            self,
            begin=None,
            end=None,
            event_types=None,
            curve_names=None,
        ):

        super().__init__(begin=begin, end=end, event_types=event_types)
        self._curve_names = None
        if curve_names:
            self.set_curve_names(curve_names)

    def __str__(self):
        """
        Represent this object as a string, excluding not-set values.

        :return: A string representation of this object
        :rtype: str
        """
        str_list = []
        if self.has_event_types():
            str_list.append(f"event_types={self._event_types}")
        if self.has_curve_names():
            str_list.append(f"curve_names={self._curve_names}")
        if self.has_begin():
            str_list.append(f"begin={self._begin.isoformat(sep=' ')}")
        if self.has_end():
            str_list.append(f"end={self._end.isoformat(sep=' ')}")
        return (
            f"<EventCurveOptions: "
            f"{', '.join(str_list)}"
            f">"
        )

    def __repr__(self):
        return self.__str__()
    
    def has_curve_names(self):
        if not isinstance(self._curve_names, list):
            return False
        return len(self._curve_names) > 0

    def set_curve_names(self, curves):
        """
        Set one ore more curve names for this filter. Limit the events to events 
        with a curve matching one of the curve_names.

        :param curves: Filter events by exact curve names
        :type curves: list[Curve, str]
        :raises ValueError: Curve missing name attr
        :raises ValueError: Invalid arg type
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventCurveOptions`
        """
        new_curves = set()
        if not isinstance(curves, (list, tuple, set)):
            curves = [curves]
        for curve in curves:
            if isinstance(curve, Curve):
                if not isinstance(curve.name, str):
                    raise ValueError("curve.name must be a string")
                curve = curve.name
            if not isinstance(curve, str):
                raise ValueError(f"curve: '{curve}' is not type 'str' or 'Curve'")
            new_curves.add(curve)
        self._curve_names = list(new_curves)
        return self

    def to_json(self):
        """
        Represent the output of `to_dict` as json.
        """
        return json.dumps(self.to_dict())

    def to_dict(self, include_not_set=False):
        """
        Represent this object as a dictionary, optionally excluding None-values.

        :param include_not_set: If variables that are not set should be included\
            in the dictionary. Defaults to False.
        :type include_not_set: bool, optional
        :return: A dictionary representation of this object
        :rtype: dict
        """
        filters = self._to_dict(include_not_set=include_not_set)
        if self.has_curve_names():
            filters["curve_names"] = self._curve_names
        elif include_not_set:
            filters["curve_names"] = None
        return filters

    def validate(self):
        """
        Check the validity of this filter and discover reasons if invalid.

        :return: A tuple of two objects; (1) a bool representing the validity of\
            the object and (2) a list of potential errors.
        :rtype: tuple[bool, list[str]]
        """
        _, errors = self._validate()
        if self.has_curve_names():
            if not all(isinstance(curve_name, str) for curve_name in self._curve_names):
                errors.append("All objects in 'curve_names' must be type str")
        return len(errors) == 0, errors


class EventFilterOptions(_BaseEventOptions):
    """
    In addition to the inherited filters (begin, end, event_type), 
    this option provides filtering on curves attributes.
    """

    def __init__(
            self,
            begin=None,
            end=None,
            event_types=None,
            q=None,
            areas=None,
            data_types=None,
            commodities=None,
            categories=None,
            exact_categories=None,
        ):
        super().__init__(begin=begin, end=end, event_types=event_types)
        self._q = None
        self._areas = None
        self._data_types = None
        self._commodities = None
        self._categories = None
        self._exact_categories = None
        if q:
            self.set_q(q)
        if areas:
            self.set_areas(areas)
        if data_types:
            self.set_data_types(data_types)
        if commodities:
            self.set_commodities(commodities)
        if categories:
            self.set_categories(categories)
        if exact_categories:
            self.set_exact_categories(exact_categories)

    def __str__(self):
        """
        Represent this object as a string, excluding not-set values.

        :return: A string representation of this object
        :rtype: str
        """
        str_list = []
        if self.has_event_types():
            str_list.append(f"event_types={self._event_types}")
        if self.has_begin():
            str_list.append(f"begin={self._begin.isoformat(sep=' ')}")
        if self.has_end():
            str_list.append(f"end={self._end.isoformat(sep=' ')}")
        if self.has_q():
            str_list.append(f"q={self._q}")
        if self.has_areas():
            str_list.append(f"areas={self._areas}")
        if self.has_data_types():
            str_list.append(f"data_types={self._data_types}")
        if self.has_commodities():
            str_list.append(f"commodities={self._commodities}")
        if self.has_categories():
            str_list.append(f"categories={self._categories}")
        if self.has_exact_categories():
            str_list.append(f"exact_categories={self._exact_categories}")
        return (
            f"<EventFilterOptions: "
            f"{', '.join(str_list)}"
            f">"
        )

    def __repr__(self):
        return self.__str__()

    def has_q(self):
        return self._q is not None

    def set_q(self, q):
        """
        Filter events by a query/freetext search

        :param q: Query/freetext
        :type q: str, required
        :raises ValueError: If q is not a string
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventFilterOptions`
        """
        if not isinstance(q, str):
            raise ValueError(f"q: '{q}' is not a string")
        self._q = q
        return self

    def has_areas(self):
        if not isinstance(self._areas, list):
            return False
        return len(self._areas) > 0

    def set_areas(self, areas):
        """
        Set one or more areas in this filter. Limit events to events having
        a curve with a matching Area.

        :param areas: The areas or area tags to receive events
        :type areas: list[Area, str]
        :raises ValueError: Invalid arg type
        :raises ValueError: Tag is not a valid Area tag
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventFilterOptions`
        """
        new_areas = set()
        if not isinstance(areas, (list, tuple, set)):
            areas = [areas]
        for area in areas:
            # Get Area by tag if string
            if isinstance(area, str):
                if not Area.is_valid_tag(area):
                    raise ValueError(f"Area not found for tag: {area}")
                area = Area.by_tag(area)
            if not isinstance(area, Area):
                raise ValueError(f"'{area}' must be type Area or string")
            new_areas.add(area)
        self._areas = list(new_areas)
        return self

    def has_data_types(self):
        if not isinstance(self._data_types, list):
            return False
        return len(self._data_types) > 0

    def set_data_types(self, data_types):
        """
        Set one or more DataTypes. Limit events to events having a
        curve with a matching DataType.

        :param data_types: The DataTypes (optionally by tag) to receive events for
        :type data_types: list[DataType, str]
        :raises ValueError: Invalid arg type
        :raises ValueError: Tag is not a valid DataType tag
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventFilterOptions`
        """
        new_data_types = set()
        if not isinstance(data_types, (list, tuple, set)):
            data_types = [data_types]
        for data_type in data_types:
            # Get DataType by tag if string
            if isinstance(data_type, str):
                if not DataType.is_valid_tag(data_type):
                    raise ValueError(f"DataType not found for tag: {data_type}")
                data_type = DataType.by_tag(data_type)
            if not isinstance(data_type, DataType):
                raise ValueError(f"'{data_type}' must be type DataType or string")
            new_data_types.add(data_type)
        self._data_types = list(new_data_types)
        return self

    def has_commodities(self):
        if not isinstance(self._commodities, list):
            return False
        return len(self._commodities) > 0

    def set_commodities(self, commodities):
        """
        Set one or more commodities in this filter. Limit events to those having a
        curve with a matching commodity.

        :param commodities: The commidities to filter for
        :type commodities: list, str
        :raises ValueError: Invalid arg type
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventFilterOptions`
        """
        if not isinstance(commodities, (list, tuple, set)):
            # Set to remove duplicates
            commodities = set([commodities])
        if not all(isinstance(commodity, str) for commodity in commodities):
            raise ValueError("commodities must be a str or a list/tuple/set of strings")
        # Store as list
        self._commodities = list(commodities)
        return self

    def has_categories(self):
        if not isinstance(self._categories, list):
            return False
        return len(self._categories) > 0

    def set_categories(self, categories):
        """
        Set one or more categories. Limits events to those having a curve 
        with at least one matching category.

        :param categories: The categories to include
        :type categories: list, str
        :raises ValueError: Invalid arg type
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventFilterOptions`
        """
        if not isinstance(categories, (list, tuple, set)):
            # Set to remove duplicates
            categories = set([categories])
        if not all(isinstance(category, str) for category in categories):
            raise ValueError("categories must be a str or a list/tuple/set of string")
        # Store as list
        self._categories = list(categories)
        return self

    def has_exact_categories(self):
        if not isinstance(self._exact_categories, list):
            return False
        return len(self._exact_categories) > 0

    def set_exact_categories(self, exact_categories):
        """
        Set one or more exact categories. Limits events to those with a curve matching at least one
        of the exact_categories. An exact category should be one or more categories in a single str,
        separated by space.

        :param exact_categories: The exact categories to include
        :type exact_categories: list, str
        :raises ValueError: Invalid arg type
        :return: The instance this method was invoked upon
        :rtype: EventFilterOptions
        """
        if not isinstance(exact_categories, (list, tuple, set)):
            # Set to remove duplicates
            exact_categories = set([exact_categories])
        if not all(isinstance(category, str) for category in exact_categories):
            raise ValueError("exact_categories must be a str or a list/tuple/set of strings")
        # Store as list
        self._exact_categories = list(exact_categories)
        return self

    def to_json(self):
        """
        Represent the output of `to_dict` as json.
        """
        return json.dumps(self.to_dict())

    def to_dict(self, include_not_set=False):
        """
        Represent this object as a dictionary, optionally excluding None-values.

        :param include_not_set: If variables that are not set should be included\
            in the dictionary. Defaults to False.
        :type include_not_set: bool, optional
        :return: A dictionary representation of this object
        :rtype: dict
        """
        filters = self._to_dict(include_not_set=include_not_set)
        # q (freetext)
        if self.has_q():
            filters["q"] = self._q
        elif include_not_set:
            filters["q"] = None
        # Areas
        if self.has_areas():
            filters["areas"] = list(area.tag for area in self._areas)
        elif include_not_set:
            filters["areas"] = None
        # Data type
        if self.has_data_types():
            filters["data_types"] = list(data_type.tag for data_type in self._data_types)
        elif include_not_set:
            filters["data_types"] = None
        # Commodities
        if self.has_commodities():
            filters["commodities"] = self._commodities
        elif include_not_set:
            filters["commodities"] = None
        # Categories
        if self.has_categories():
            filters["categories"] = self._categories
        elif include_not_set:
            filters["categories"] = None
        if self.has_exact_categories():
            filters["exact_categories"] = self._exact_categories
        elif include_not_set:
            filters["exact_categories"] = None
        return filters

    def validate(self):
        """
        Check the validity of this filter and discover reasons if invalid.

        :return: A tuple of two objects; (1) a bool representing the validity of\
            the object and (2) a list of potential errors.
        :rtype: tuple[bool, list[str]]
        """
        _, errors = self._validate()
        if self.has_q():
            if not isinstance(self._q, str):
                errors.append("q must be type str")
        if self.has_areas():
            if not all(isinstance(area, Area) for area in self._areas):
                errors.append(
                    "All objects in 'areas' must be type Area"
                )
        if self.has_data_types():
            if not all(isinstance(data_type, DataType) for data_type in self._data_types):
                errors.append(
                    "All objects in 'data_types' must be type DataType"
                )
        if self.has_commodities():
            if not all(isinstance(commodity, str) for commodity in self._commodities):
                errors.append(
                    "All objects in 'commodities' must be type str"
                )
        if self.has_categories():
            if not all(isinstance(category, str) for category in self._categories):
                errors.append(
                    "All objects in 'categories' must be type str"
                )
        if self.has_exact_categories():
            if not all(isinstance(category, str) for category in self._exact_categories):
                errors.append(
                    "All objects in 'exact_categories' must be type str"
                )
        return len(errors) == 0, errors
