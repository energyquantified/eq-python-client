import json
from datetime import datetime, date
from ..metadata.curve import Curve, DataType
from ..metadata.area import Area
from .events import EventType

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
        Set the filters 'begin'. # TODO This is earliest date of changed data to 

        # TODO accept date and localize?
        # TODO require tz-aware?
        Args:
            begin (datetime): _description_

        Raises:
            ValueError: If invalid input

        Returns:
            _BaseEventOptions: The same instance this method was invoked upon
        """
        if isinstance(begin, str):
            begin = datetime.fromisoformat(begin)
        if isinstance(begin, date):
            # TODO require tz-aware?
            if not isinstance(begin, datetime):
                begin = datetime.combine(begin, datetime.min.time())
        else:
            raise ValueError(f"'{begin}' is not type datetime or str")
        self._begin = begin
        return self

    def set_end(self, end):
        """
        Set the filters 'end'. 

        # TODO accept date and localize?
        # TODO require tz-aware?
        Args:
            end (_type_): _description_

        Raises:
            ValueError: If invalid input

        Returns:
            _BaseEventOptions: The instance this method was invoked upon
        """
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
        if isinstance(end, date):
            # TODO require tz-aware?
            if not isinstance(end, datetime):
                end = datetime.combine(end, datetime.min.time())
        else:
            raise ValueError(f"'{end}' is not type datetime or str")
        self._end = end
        return self

    def set_event_types(self, *event_types):
        """
        Set one or more EventTypes in this filter, excluding any events not matching at least one.

        *event_types:
            (EventType, str): EventType or a valid tag

        Raises:
            ValueError: If invalid input
            
        Returns:
            _BaseEventOptions: The instance this method was invoked upon
        """
        self._event_types = self._parse_event_types(event_types)
        return self

    def _parse_event_types(self, event_types):
        new_event_types = set()
        for event_type in event_types:
            if isinstance(event_type, (list, tuple, set)):
                new_event_types.update(self._parse_event_types(event_type))
            else:
                if isinstance(event_type, str):
                    if not EventType.is_valid_tag(event_type):
                        raise ValueError(f"EventType not found for tag: {event_type}")
                    evt_type = EventType.by_tag(event_type)
                if not isinstance(evt_type, EventType):
                    raise ValueError(f"'{event_type}' is not type 'EventType' or 'str'")
                new_event_types.add(event_type)
        return new_event_types

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
 
    def set_curve_names(self, *curves):
        """
        Set one or more curve_names for this filter.

        Limit the events to events with a curve matching one of the curve_names.

        Returns:
            EventCurveOptions: The instance this method was invoked upon
        """
        self._curve_names = self._parse_curve_names(curves)
        return self

    def _parse_curve_names(self, curves):
        new_curves = set()
        for curve in curves:
            if isinstance(curve, (list, tuple, set)):
                new_curves.update(self._parse_curve_names(curve))
            else:
                if isinstance(curve, str):
                    name = curve
                elif isinstance(curve, Curve):
                    name = curve.name
                else:
                    raise ValueError(f"curve: '{curve}' is not type 'str' or 'Curve'")
                new_curves.add(name)
        return new_curves

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self, include_not_set=False):
        """
        Return the object as a dictionary.

        Args:
            include_not_set (bool, optional): If values that are not set should be included
            or not. Defaults to False (excludes).

        Returns:
            dict: This obj as a dictionary, optionally including not-set values
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
        Filter events by a query/freetext search.

        Args:
            q (str): Freetext

        Raises:
            ValueError: Invalid input type

        Returns:
            EventFilterOptions: The instance this method was invoked upon
        """
        if not isinstance(q, str):
            raise ValueError(f"q: '{q}' is not a str")
        self._q = q
        return self

    # def set_q(self, *q):
    #     self._q = self._parse_q(q)
    #     return self

    # def _parse_q(self, txt):
    #     new_q = set()
    #     for q in txt:
    #         if isinstance(q, (list, tuple, set)):
    #             new_q.update(self._parse_q(q))
    #         else:
    #             if not isinstance(q, str):
    #                 raise ValueError(f"q: '{q}' is not a str")

    def set_areas(self, *areas):
        """
        Set one or more areas in this filter. Limit events to events having a curve with a matching Area.

        *areas:
            (Area, str, iterable(Area, str)): Each arg must either be an Area
              or a str (valid area tag), or an iterable of those.
        
        Raises:
            ValueError: If invalid input
            
        Returns:
            EventFilterOptions: The instance this method was invoked upon
        """
        self._areas = self._parse_areas(areas)
        return self
    
    def _parse_areas(self, areas):
        new_areas = set()
        for area in areas:
            if isinstance(area, (list, tuple, set)):
                new_areas.update(self._parse_areas(area))
            else:
                if isinstance(area, str):
                    if not Area.is_valid_tag(area):
                        raise ValueError(f"Area not found for tag: {area}")
                    area = Area.by_tag(area)
                if not isinstance(area, Area):
                    raise ValueError(f"'{area}' must be type Area or str")
                new_areas.add(area)
        return new_areas

    def set_data_types(self, *data_types):
        """
        Set one or more DataTypes. Limit events to events having a curve with a matching DataType.

        *data_types:
            (DataType, str, list(DataType, str), tuple(DataType, str), set(DataType, str)):
              Each arg must either be a DataType object, a valid DataType tag (str),
                or and iterable of those

        Raises:
            ValueError: If invalid input

        Returns:
            EventFilterOptions: The instance this method was invoked upon
        """
        self._data_types = self._parse_data_types(data_types)
        return self
    
    def _parse_data_types(self, *data_types):
        new_data_types = set()
        for data_type in data_types:
            if isinstance(data_type, (list, tuple, set)):
                new_data_types.update(self._parse_data_types(data_type))
            else:
                # Find DataType by tag if str
                if isinstance(data_type, str):
                    if not DataType.is_valid_tag(data_type):
                        raise ValueError(f"DataType not found for tag: {data_type}")
                    data_type = DataType.by_tag(data_type)
                if not isinstance(data_type, DataType):
                    raise ValueError(f"'{data_type}' must be type DataType or str")
                new_data_types.add(data_type)
        return new_data_types

    def set_commodities(self, *commodities):
        """
        Set one or more commodities - limit events to events having a curve with a matching commodity.

        Raises:
            ValueError: If invalid input

        Returns:
            EventFilterOptions: The instance this method was invoked upon
        """
        self._commodities = self._parse_commodities(commodities)
        return self
    
    def _parse_commodities(self, commodities):
        new_commodities = set()
        for commodity in commodities:
            if isinstance(commodity, (list, tuple, set)):
                new_commodities.update(self._parse_commodities(commodity))
            else:
                if not isinstance(commodity, str):
                    raise ValueError(f"Commodity: '{commodity}' is not a str")
                new_commodities.add(commodity)
        return new_commodities

    def set_categories(self, *categories):
        """
        Set one or more categories. 
        
        If set, events must have a curve that match at least one of the categories.

        Returns:
            EventFilterOptions: The instance this method was invoked upon
        """
        self._categories = self._parse_categories(categories)
        return self

    def _parse_categories(self, categories):
        new_categories = set()
        for category in categories:
            if isinstance(category, (list, tuple, set)):
                new_categories.update(self._parse_categories(category))
            else:
                if not isinstance(category, str):
                    raise ValueError(f"Category: '{category}' is not a str")
                new_categories.add(category)
        return new_categories

    def set_exact_categories(self, *exact_categories):
        """
        Set one or more exact categories.

        Events must have a curve matching at least one of the exact categories.

        *exact_categories:
            (str, list(str), set(str), tuple(str)): A str or an iterable of strings. An exact category
            should be one or more categories in a single string, separated by space.

        Returns:
            EventFilterOptions: The instance this method was invoked upon
        """
        self._exact_categories = self._parse_exact_categories(exact_categories)
        return self

    def _parse_exact_categories(self, exact_categories):
        new_exact_categories = set()
        for exact_category in exact_categories:
            if isinstance(exact_category, (list, tuple, set)):
                new_exact_categories.update(self._parse_exact_categories(exact_category))
            else:
                if not isinstance(exact_category, str):
                    raise ValueError(f"Exact category: '{exact_category}' is not a str")
                new_exact_categories.add(exact_category)
        return new_exact_categories

    def set_location(self, location):
        """
        Set the location.

        Args:
            location (str): _description_ # TODO

        Raises:
            ValueError: If invalid input

        Returns:
            EventFilterOptions: The instance this method was invoked upon
        """
        if not isinstance(location, str):
            raise ValueError(f"location: '{location}' is not a str")
        self._location = location
        return self
    
    def to_json(self):
        return json.dumps(self.to_dict())

    def to_dict(self, include_not_set=False):
        """
        Represent this object as a dictionary.

        Args:
            include_not_set (bool, optional): If filters not-set should be included.
            Defaults to False (excludes).

        Returns:
            dict: dictionary of self
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
            filters["data_type"] = list(data_type.tag for data_type in self._data_types)
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