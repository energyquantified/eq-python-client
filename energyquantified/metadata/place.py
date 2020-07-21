import enum


class Place:
    """
    A place is a general concept of a physical location, such as a powerplant,
    a weather station, a position on a river etc.
    """

    def __init__(self, kind, key, name, unit=None, fuels=None, area=None,
                 location=None, children=None, curves=None):
        #: The place type. See :py:class:`PlaceType`.
        self.kind = kind
        #: The identifier
        self.key = key
        #: The name of the place
        self.name = name
        #: The unit name (if it is a powerplant unit)
        self.unit = unit
        #: The fuel types (if it is a powerplant unit)
        self.fuels = fuels or []
        #: The area in which this place lies, see :py:class:`Area`.
        self.area = area
        #: The geolocation of this place: ``(latitude, longitude)``
        self.location = location or None
        #: A list of children (typically used for a powerplants with sub-units)
        self.children = children or []
        #: A list of curves with data for this place. See :py:class:`Curve`.
        self.curves = curves or []

    @property
    def latitude(self):
        """
        The latitude of this place.
        """
        return self.location[0]

    @property
    def longitude(self):
        """
        The longitude of this place.
        """
        return self.location[1]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        parts = []
        parts.append(f"<Place: key=\"{self.key}\", name=\"{self.name}\"")
        if self.unit:
            parts.append(f", unit=\"{self.unit}\"")
        if self.kind:
            parts.append(f", kind={self.kind}")
        if self.fuels:
            parts.append(f", fuels={self.fuels}")
        if self.location:
            parts.append(f", location={self.location}")
        parts.append(">")
        return "".join(parts)


_placetypes_lookup = {}

class PlaceType(enum.Enum):
    """
    Enumerator of place types. Used to describe type type of a
    :py:class:`Place`.
    """
    #: A city
    CITY = ("city",)
    #: A power consumer, such as a factory
    CONSUMER = ("consumer",)
    #: A power producer (power plant)
    PRODUCER = ("producer",)
    #: A river location
    RIVER = ("river",)
    #: A weather station
    WEATHERSTATION = ("weatherstation",)
    #: Unspecified
    OTHER = ("other",)

    def __init__(self, tag):
        self.tag = tag
        _placetypes_lookup[tag.lower()] = self

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.name

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a place type tag exists or not.

        :param tag: A place type tag
        :type tag: str
        :return: True if it exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _placetypes_lookup

    @staticmethod
    def by_tag(tag):
        """
        Look up place type by tag.

        :param tag: A place type tag
        :type tag: str
        :return: The place type for the given tag
        :rtype: PlaceType
        """
        return _placetypes_lookup[tag.lower()]
