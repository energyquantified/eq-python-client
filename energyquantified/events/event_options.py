import json
from datetime import datetime, date
from ..metadata.curve import Curve, DataType
from ..metadata.area import Area
from . import EventType

class _BaseEventOptions:
    """
    Base class with filters shared between EventCurveOptions and EventFilterOptions. This includes
    begin, end, and event_types.
    """

    def __init__(self):
        self._begin = None
        self._end = None
        self._event_types = None

    def set_begin(self, begin):
        """
        Set the filters 'begin'. The begin/end range regards the data an event
        describes, not to be confused with created time of the event.

        :param begin: Start of range
        :type begin: datetime
        :raises ValueError: Invalid arg type
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventCurveOptions` | \
                :py:class:`energyquantified.events.EventFilterOptions`
        """
        if isinstance(begin, str):
            begin = datetime.fromisoformat(begin)
        if isinstance(begin, date):
            # TODO require tz-aware?
            if not isinstance(begin, datetime):
                begin = datetime.combine(begin, datetime.min.time())
        else:
            raise ValueError(f"'{begin}' is not type datetime or string")
        self._begin = begin
        return self

    def set_end(self, end):
        """
        Set the filters 'end'. The begin/end range regards the data an event
        describes, not to be confused with the created time of the event.

        :param end: End of range
        :type end: datetime
        :raises ValueError: Invalid arg type
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventCurveOptions` | \
                :py:class:`energyquantified.events.EventFilterOptions`
        """
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
        if isinstance(end, date):
            # TODO require tz-aware?
            if not isinstance(end, datetime):
                end = datetime.combine(end, datetime.min.time())
        else:
            raise ValueError(f"'{end}' is not type datetime or string")
        self._end = end
        return self

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
        self._event_types = new_event_types
        return self

    def to_json(self):
        raise NotImplementedError

    def to_dict(self):
        raise NotImplementedError

    def _to_dict(self, include_not_set=False):
        filters = {}
        # Event types
        if self._event_types is not None:
            filters["event_types"] = list(event_type.tag for event_type in self._event_types)
        elif include_not_set:
            filters["event_types"] = None
        # Begin
        if self._begin is not None:
            filters["begin"] = self._begin.isoformat(sep=" ")
        elif include_not_set:
            filters["begin"] = None
        # End
        if self._end is not None:
            filters["end"] = self._end.isoformat(sep=" ")
        elif include_not_set:
            filters["end"] = None
        return filters

class EventCurveOptions(_BaseEventOptions):
    """
    In addition to the inherited filters (begin, end, event_type), 
    this option provides filtering on exact curve_names(s).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._curve_names = None

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
        Represent this object as json.
        """
        return json.dumps(self.to_dict())

    def to_dict(self, include_not_set=False):
        """
        Represent this object as a dictionary, optionally excluding None-values.

        :param include_not_set: If variables that are not set should be included\
            in the dictionary. Defaults to False.
        :type include_not_set: bool, optional
        :return: A dict representation of this object
        :rtype: dict
        """
        filters = super()._to_dict(include_not_set=include_not_set)
        if self._curve_names is not None:
            filters["curve_names"] = self._curve_names
        elif include_not_set:
            filters["curve_names"] = None
        return filters
    
    def __str__(self):
        str_list = []
        if self._event_types:
            str_list.append(f"event_types={self._event_types}")
        if self._curve_names:
            str_list.append(f"curve_names={self._curve_names}")
        if self._begin:
            str_list.append(f"begin={self._begin.isoformat(sep=' ')}")
        if self._end:
            str_list.append(f"end={self._end.isoformat(sep=' ')}")
        return (
            f"<EventCurveOptions: "
            f"{', '.join(str_list)}"
            f">"
        )

    def __repr__(self):
        return self.__str__()

class EventFilterOptions(_BaseEventOptions):
    """
    In addition to the inherited filters (begin, end, event_type), 
    this option provides filtering on curves attributes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._q = None
        self._areas = None
        self._data_types = None
        self._commodities = None
        self._categories = None
        self._exact_categories = None
        self._location = None

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
            commodities = set([commodities])
        if not all(isinstance(commodity, str) for commodity in commodities):
            raise ValueError("commodities must be a str or a list/tuple/set of strings")
        self._commodities = commodities
        return self

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
            categories = set([categories])
        if not all(isinstance(category, str) for category in categories):
            raise ValueError("categories must be a str or a list/tuple/set of string")
        self._categories = categories
        return self

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
            exact_categories = set([exact_categories])
        if not all(isinstance(category, str) for category in exact_categories):
            raise ValueError("exact_categories must be a str or a list/tuple/set of strings")
        self._exact_categories = exact_categories
        return self

    def set_location(self, location):
        """
        Filter by location.

        :param location: Location
        :type location: str
        :raises ValueError: Invalid arg type
        :return: The instance this method was invoked upon
        :rtype: :py:class:`energyquantified.events.EventFilterOptions`
        """
        if not isinstance(location, str):
            raise ValueError(f"location: '{location}' is not a string")
        self._location = location
        return self
    
    def to_json(self):
        """
        Represent this object as json.
        """
        return json.dumps(self.to_dict())

    def to_dict(self, include_not_set=False):
        """
        Represent this object as a dictionary, optionally excluding None-values.

        :param include_not_set: If variables that are not set should be included\
            in the dictionary. Defaults to False.
        :type include_not_set: bool, optional
        :return: A dict representation of this object
        :rtype: dict
        """
        filters = super()._to_dict(include_not_set=include_not_set)
        # q (freetext)
        if self._q is not None:
            filters["q"] = self._q
        elif include_not_set:
            filters["q"] = None
        # Areas
        if self._areas is not None:
            filters["areas"] = list(area.tag for area in self._areas)
        elif include_not_set:
            filters["areas"] = None
        # Data type
        if self._data_types is not None:
            filters["data_types"] = list(data_type.tag for data_type in self._data_types)
        elif include_not_set:
            filters["data_type"] = None
        # Commodities
        if self._commodities is not None:
            filters["commodity"] = self._commodities
        elif include_not_set:
            filters["commodity"] = None
        # Categories
        if self._categories is not None:
            filters["category"] = self._categories
        elif include_not_set:
            filters["category"] = None
        if self._exact_categories is not None:
            filters["exact_category"] = self._exact_categories
        elif include_not_set:
            filters["exact_category"] = None
        # Location
        if self._location is not None:
            filters["location"] = self._location
        elif include_not_set:
            filters["location"] = None
        return filters
    
    def __str__(self):
        str_list = []
        if self._event_types:
            str_list.append(f"event_types={self._event_types}")
        if self._begin:
            str_list.append(f"begin={self._begin.isoformat(sep=' ')}")
        if self._end:
            str_list.append(f"end={self._end.isoformat(sep=' ')}")
        if self._q:
            str_list.append(f"q={self._q}")
        if self._areas:
            str_list.append(f"areas={self._areas}")
        if self._data_types:
            str_list.append(f"data_types={self._data_types}")
        if self._commodities:
            str_list.append(f"commodities={self._commodities}")
        if self._categories:
            str_list.append(f"categories={self._categories}")
        if self._exact_categories:
            str_list.append(f"exact_categories={self._exact_categories}")
        if self._location:
            str_list.append(f"location={self._location}")
        return (
            f"<EventFilterOptions: "
            f"{', '.join(str_list)}"
            f">"
        )

    def __repr__(self):
        return self.__str__()