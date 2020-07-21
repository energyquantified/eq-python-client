import enum


class Allocation(enum.Enum):
    """
    Enumerator of border allocation types between two price areas.
    """
    #: Explicit exchange border
    EXPLICIT = ("E", "Explicit")
    #: Implicit exchange border
    IMPLICIT = ("I", "Implicit")
    #: Flow-based exchange border
    FLOW_BASED = ("F", "Flow-based")
    #: No commercial exchange available
    NO_COMMERCIAL_CAPACITY = ("N", "No commercial capacity")

    def __init__(self, tag, label):
        self.tag = tag
        self.label = label

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Area:
    """
    A representation of a price area or country.

    Areas do have a reference to all exchange borders with available
    commercial capacity allocation properties. Access the borders via
    ``area.borders[]``. If you just want direct access neighbour
    listing, use ``area.exchange_neighbours[]``.

    Some areas, such as Nord Pool, consist of smaller areas. In these
    cases, you can access their children via ``area.children[]``. You can
    also find the parent area via ``area.parent``.

    All areas has a ``tag``, which you will find in the curve names, and a
    full ``name``.
    """

    __lookup_tags = {}
    __enum_ordering = []

    @classmethod
    def is_valid_tag(cls, tag):
        """
        Check whether an area tag exists or not.

        :param tag: An area tag
        :type tag: str
        :return: True if it exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in cls.__lookup_tags

    @classmethod
    def by_tag(cls, tag):
        """
        Look up area by tag.

        :param tag: An area tag
        :type tag: str
        :return: The area for the given tag
        :rtype: Area
        """
        return cls.__lookup_tags[tag.lower()]

    @classmethod
    def by_tags(cls, *tags):
        """
        Return multiple areas by tags.

        :return: A list of areas by the provided tags
        :rtype: list[Area]
        """
        return [cls.__lookup_tags[t.lower()] for t in tags]

    @classmethod
    def all(cls):
        """
        Return a list of all areas.

        :return: A list of all areas
        :rtype: list[Area]
        """
        return list(cls.__enum_ordering)

    def __init__(
        self,
        tag,
        name,
        country=False,
        price_area=False,
        control_area=False,
        external=False,
    ):
        # Validations
        assert tag is not None, "Parameter tag is missing"
        assert name is not None, "Parameter name is missing"
        assert tag not in self.__lookup_tags, "Duplicate tag '%s'" % tag
        # --- Attributes ---
        #: The area tag (used in curve names)
        self.tag = tag
        #: The full name of the area
        self.name = name
        #: True when this area is a country, otherwise False
        self.country = country
        #: True when this area is a price area, otherwise False
        self.price_area = price_area
        #: True when this area is a control area/TSO area, otherwise False
        self.control_area = control_area
        #: True when this area is outside of the supported region (used
        # for exchange areas)
        self.external = external
        # Lookups and ordering
        Area.__lookup_tags[tag.lower()] = self
        Area.__enum_ordering.append(self)
        # --- Set of exchange neighbours ---
        #: Set of neighbouring areas
        self.exchange_neighbours = set()
        #: Set of exchange borders with exchange allocation types
        self.borders = set()
        # --- Parent/children relationship ---
        #: The parent area (set if this is a sub-area of another area)
        self.parent = None
        #: Set of child areas (set if this area is split into other,
        #: smaller areas)
        self.children = set()
        # Convert tag to variable name ("-" becomes "_")
        setattr(Area, self.tag.replace("-", "_"), self)

    _ordering_nb = []
    _ordering_borders = []
    _ordering_children = []
    _variable = None

    def get_family(self):
        """
        Get all descendants in a flat list for this Area.

        :return: A list of all descendants/sub-areas for this area
        :rtype: list[Area]
        """
        the_list = []
        self._family_internal(the_list)
        return the_list

    def _family_internal(self, the_list):
        the_list.append(self)
        for c in self.children:
            c._family_internal(the_list)

    def __repr__(self):
        return "<Area: %s>" % self.tag

    def __str__(self):
        return "<Area: %s>" % self.tag

    def _add_exchange_neighbours(self, *neighbours):
        """
        Private method. Add a list of exchange neighbours to self and
        self to the neighbour.
        """
        Area._ordering_nb.append(self)
        # Add neighbour relationships
        for nb in neighbours:
            assert nb != self, "Cannot add self to neighbour list: %s" % self.tag
            self.exchange_neighbours.add(nb)
            nb.exchange_neighbours.add(self)
        return self

    def _add_borders(self, *borders):
        """
        Private method. Add borders and exchange neighbours.
        """
        Area._ordering_borders.append(self)
        # Add exchange neighbours
        self._add_exchange_neighbours(*tuple(area for (area, allocations) in borders))
        # Add borders
        for nb, allocs in borders:
            assert nb != self, "Cannot add self to border list: %s" % self.tag
            allocations = tuple(a for a in list(Allocation) if a.tag in allocs)
            assert (
                allocations and len(allocations) > 0
            ), "At least one allocation required for %s -> %s" % (self, nb)
            self.borders.add(Border(self, nb, allocations))
            nb.borders.add(Border(nb, self, allocations))
        return self

    def _add_children(self, *children):
        """
        Private method. Add children to this area.
        """
        Area._ordering_children.append(self)
        # Add children to relationships
        for child in children:
            assert not child.parent, "Cannot add %s twice to children list: %s" % (
                child.tag,
                self.tag,
            )
            assert child != self, "Cannot add self to children list: %s" % self.tag
            child.parent = self
            self.children.add(child)


class Border:
    """
    A one-way border between two price areas.

    The `source` area is where the power is exported from, and the
    `sink` area is where to power is imported to.

    Each border has a list of capacity allocations describing how the
    commercial capacities on the border are set.
    """

    def __init__(self, source, sink, allocations=None):
        #: The source area (the exporter)
        self.source = source
        #: The sink area (the importer)
        self.sink = sink
        #: A tuple of the exchange allocation types (flow-based, implicit, etc.)
        self.allocations = allocations

    def is_explicit(self):
        """
        Returns True if this border has explicit allocations.

        :return: True if this border has explicit allocations, otherwise False
        :rtype: bool
        """
        return Allocation.EXPLICIT in self.allocations

    def is_implicit(self):
        """
        Returns True if this border has implicit allocations.

        :return: True if this border has implicit allocations, otherwise False
        :rtype: bool
        """
        return Allocation.IMPLICIT in self.allocations

    def is_flow_based(self):
        """
        Returns True if this border is flow-based.

        :return: True if this border is flow-based, otherwise False
        :rtype: bool
        """
        return Allocation.FLOW_BASED in self.allocations

    def as_tuple(self):
        """
        Convert this border to a tuple of (source, sink, allocations)

        :return: This border as a tuple of (source, sink, allocations)
        :rtype: tuple
        """
        return (self.source, self.sink, self.allocations)

    def __hash__(self):
        return hash(self.as_tuple())

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()

    def __repr__(self):
        return "<Border: %s – %s, allocations=%s>" % (
            self.source.tag,
            self.sink.tag,
            sorted(self.allocations),
        )

    def __str__(self):
        return "<Border: %s – %s, allocations=%s>" % (
            self.source.tag,
            self.sink.tag,
            sorted(self.allocations),
        )


## Unknown area

NOAREA = Area(tag="", name="")


## Nordics

NP = Area(tag="NP", name="Nord Pool", price_area=True)

NO = Area(tag="NO", name="Norway", country=True)
NO1 = Area(tag="NO1", name="NO1 – Oslo", price_area=True)
NO2 = Area(tag="NO2", name="NO2 – Kristiansand", price_area=True)
NO3 = Area(tag="NO3", name="NO3 – Trondheim", price_area=True)
NO4 = Area(tag="NO4", name="NO4 – Tromsø", price_area=True)
NO5 = Area(tag="NO5", name="NO5 – Bergen", price_area=True)
NO._add_children(NO1, NO2, NO3, NO4, NO5)

SE = Area(tag="SE", name="Sweden", country=True)
SE1 = Area(tag="SE1", name="SE1 – Luleå", price_area=True)
SE2 = Area(tag="SE2", name="SE2 – Sundsvall", price_area=True)
SE3 = Area(tag="SE3", name="SE3 – Stockholm", price_area=True)
SE4 = Area(tag="SE4", name="SE4 – Malmö", price_area=True)
SE._add_children(SE1, SE2, SE3, SE4)

DK = Area(tag="DK", name="Denmark", country=True)
DK1 = Area(tag="DK1", name="DK1 – Jylland", price_area=True)
DK2 = Area(tag="DK2", name="DK2 – København", price_area=True)
DK._add_children(DK1, DK2)

FI = Area(tag="FI", name="Finland", country=True, price_area=True)

NP._add_children(NO, SE, DK, FI)


## Baltics

EE = Area(tag="EE", name="Estonia", country=True, price_area=True)
LV = Area(tag="LV", name="Latvia", country=True, price_area=True)
LT = Area(tag="LT", name="Lithuania", country=True, price_area=True)


## Central Western Europe

DE = Area(tag="DE", name="Germany", country=True, price_area=True)
DE_50Hertz = Area(tag="DE-50Hertz", name="Germany – 50Hertz", control_area=True)
DE_Amprion = Area(tag="DE-Amprion", name="Germany – Amprion", control_area=True)
DE_TenneT = Area(tag="DE-TenneT", name="Germany – TenneT GER", control_area=True)
DE_TransnetBW = Area(tag="DE-TransnetBW", name="Germany – TransnetBW", control_area=True)
DE._add_children(DE_50Hertz, DE_Amprion, DE_TenneT, DE_TransnetBW)

FR = Area(tag="FR", name="France", country=True, price_area=True)
FR_ARA = Area(tag="FR-ARA", name="France – Auvergne-Rhône-Alpes", control_area=True)
FR_BFC = Area(tag="FR-BFC", name="France – Bourgogne-Franche-Comté", control_area=True)
FR_BRE = Area(tag="FR-BRE", name="France – Bretagne", control_area=True)
FR_COR = Area(tag="FR-COR", name="France – Corse", control_area=True)
FR_CVL = Area(tag="FR-CVL", name="France – Centre-Val de Loire", control_area=True)
FR_GES = Area(tag="FR-GES", name="France – Grand-Est", control_area=True)
FR_HDF = Area(tag="FR-HDF", name="France – Hauts-de-France", control_area=True)
FR_IDF = Area(tag="FR-IDF", name="France – Île-de-France", control_area=True)
FR_NAQ = Area(tag="FR-NAQ", name="France – Nouvelle-Aquitaine", control_area=True)
FR_NOR = Area(tag="FR-NOR", name="France – Normandie", control_area=True)
FR_OCC = Area(tag="FR-OCC", name="France – Occitanie", control_area=True)
FR_PAC = Area(
    tag="FR-PAC", name="France – Provence-Alpes-Côte d'Azur", control_area=True
)
FR_PDL = Area(tag="FR-PDL", name="France – Pays de la Loire", control_area=True)
FR._add_children(
    FR_ARA,
    FR_BFC,
    FR_BRE,
    FR_CVL,
    FR_GES,
    FR_HDF,
    FR_IDF,
    FR_NAQ,
    FR_NOR,
    FR_OCC,
    FR_PAC,
    FR_PDL,  # Removed: FR_COR (Corsica)
)

NL = Area(tag="NL", name="Netherlands", country=True, price_area=True)
BE = Area(tag="BE", name="Belgium", country=True, price_area=True)
AT = Area(tag="AT", name="Austria", country=True, price_area=True)
CH = Area(tag="CH", name="Switzerland", country=True, price_area=True)


## United Kingdom/Ireland

# National Grid
GB = Area(tag="GB", name="Great Britain", country=True, price_area=True)
# SONI
NIE = Area(tag="NIE", name="Northern Ireland", country=True, price_area=True, control_area=True)
# EirGrid
IE = Area(tag="IE", name="Ireland", country=True, price_area=True, control_area=True)


## Central Eastern Europe

PL = Area(tag="PL", name="Poland", country=True, price_area=True)
CZ = Area(tag="CZ", name="Czech Republic", country=True, price_area=True)
HU = Area(tag="HU", name="Hungary", country=True, price_area=True)
SK = Area(tag="SK", name="Slovakia", country=True, price_area=True)


## Iberian Peninsula

ES = Area(tag="ES", name="Spain", country=True, price_area=True)
PT = Area(tag="PT", name="Portugal", country=True, price_area=True)


## Southern Europe

IT = Area(tag="IT", name="Italy", country=True, price_area=True)
IT_NORD = Area(tag="IT-NORD", name="Italy – Northern", price_area=True)
IT_SUD = Area(tag="IT-SUD", name="Italy – Southern", price_area=True)
IT_CNOR = Area(tag="IT-CNOR", name="Italy – Central-Northern", price_area=True)
IT_CSUD = Area(tag="IT-CSUD", name="Italy – Central-Southern", price_area=True)
IT_SARD = Area(tag="IT-SARD", name="Italy – Sardegna", price_area=True)
IT_SICI = Area(tag="IT-SICI", name="Italy – Sicily", price_area=True)
IT._add_children(IT_NORD, IT_SUD, IT_CNOR, IT_CSUD, IT_SARD, IT_SICI)


SI = Area(tag="SI", name="Slovenia", country=True, price_area=True)
RO = Area(tag="RO", name="Romania", country=True, price_area=True)
HR = Area(tag="HR", name="Croatia", country=True, price_area=True)
BA = Area(tag="BA", name="Bosnia and Herzegovina", country=True, price_area=True)
RS = Area(tag="RS", name="Serbia", country=True, price_area=True)
ME = Area(tag="ME", name="Montenegro", country=True, price_area=True)
BG = Area(tag="BG", name="Bulgaria", country=True, price_area=True)
AL = Area(tag="AL", name="Albania", country=True, price_area=True)
MK = Area(tag="MK", name="North Macedonia", country=True, price_area=True)
GR = Area(tag="GR", name="Greece", country=True, price_area=True)


## South-Eastern Europe

TR = Area(tag="TR", name="Turkey", country=True, price_area=True)


## Other

RU = Area(tag="RU", name="Russia", country=True, external=True)
RU_KGD = Area(tag="RU-KGD", name="Kaliningrad (Russia)", country=True, external=True)
BY = Area(tag="BY", name="Belarus", country=True, external=True)
UA = Area(tag="UA", name="Ukraine", country=True, external=True)
MD = Area(tag="MD", name="Moldova", country=True, external=True)
MT = Area(tag="MT", name="Malta", country=True, external=True)


## Nordic borders

NO1._add_borders((NO2, "I"), (NO3, "I"), (NO5, "I"), (SE3, "I"))
NO2._add_borders((DK1, "I"), (NL, "I"), (NO1, "I"), (NO5, "I"))
NO3._add_borders((NO1, "I"), (NO4, "I"), (NO5, "I"), (SE2, "I"))
NO4._add_borders((FI, "N"), (NO3, "I"), (SE1, "I"), (SE2, "I"))
NO5._add_borders((NO1, "I"), (NO2, "I"), (NO3, "I"))

SE1._add_borders((FI, "I"), (NO4, "I"), (SE2, "I"))
SE2._add_borders((NO3, "I"), (NO4, "I"), (SE1, "I"), (SE3, "I"))
SE3._add_borders((DK1, "I"), (FI, "I"), (NO1, "I"), (SE2, "I"), (SE4, "I"))
SE4._add_borders((DE, "I"), (DK2, "I"), (LT, "I"), (PL, "I"), (SE3, "I"))

DK1._add_borders((DE, "I"), (DK2, "EI"), (NL, "I"), (NO2, "I"), (SE3, "I"))
DK2._add_borders((DE, "I"), (DK1, "EI"), (SE4, "I"))

FI._add_borders((EE, "I"), (NO4, "N"), (RU, "E"), (SE1, "I"), (SE3, "I"))


## Baltic borders

EE._add_borders((FI, "I"), (LV, "I"), (RU, "N"))
LV._add_borders((EE, "I"), (LT, "I"), (RU, "N"))
LT._add_borders((BY, "E"), (LV, "I"), (PL, "I"), (RU_KGD, "E"), (SE4, "I"))


## Central Western Europe

DE._add_borders(
    (AT, "F"),
    (CH, "E"),
    (CZ, "E"),
    (DK1, "I"),
    (DK2, "I"),
    (FR, "EF"),
    (NL, "EF"),
    (PL, "E"),
    (SE4, "I"),
)
AT._add_borders((CH, "E"), (CZ, "E"), (DE, "F"), (HU, "E"), (IT_NORD, "EI"), (SI, "EI"))
FR._add_borders(
    (BE, "F"), (CH, "E"), (DE, "EF"), (ES, "EI"), (GB, "EI"), (IT_NORD, "EI")
)
FR_COR._add_borders((IT_SARD, "I"))
NL._add_borders((BE, "F"), (DE, "EF"), (DK1, "I"), (GB, "EI"), (NO2, "I"))
BE._add_borders((FR, "F"), (GB, "EI"), (NL, "F"))
CH._add_borders((AT, "E"), (DE, "E"), (FR, "E"), (IT_NORD, "E"))


## United Kingdom/Ireland

GB._add_borders((BE, "EI"), (FR, "EI"), (NL, "EI"), (NIE, "I"), (IE, "I"))
NIE._add_borders((IE, "I"), (GB, "I"))
IE._add_borders((NIE, "I"), (GB, "I"))


## Central Eastern Europe

PL._add_borders((CZ, "E"), (DE, "E"), (LT, "I"), (SE4, "I"), (SK, "E"), (UA, "E"))
CZ._add_borders((AT, "E"), (DE, "E"), (PL, "E"), (SK, "EI"))
HU._add_borders((AT, "E"), (HR, "E"), (RO, "EI"), (RS, "E"), (SK, "EI"), (UA, "E"))
SK._add_borders((CZ, "EI"), (HU, "EI"), (PL, "E"), (UA, "E"))


## Iberian Peninsula

ES._add_borders((FR, "EI"), (PT, "I"))
PT._add_borders((ES, "I"))


## Southern Europe

IT_NORD._add_borders((AT, "EI"), (CH, "E"), (FR, "EI"), (IT_CNOR, "I"), (SI, "EI"))
IT_CNOR._add_borders((IT_CSUD, "I"), (IT_NORD, "I"), (IT_SARD, "I"))
IT_CSUD._add_borders((IT_CNOR, "I"), (IT_SARD, "I"), (IT_SUD, "I"), (ME, "E"))
IT_SUD._add_borders((GR, "E"), (IT_CSUD, "I"), (IT_SICI, "I"))
IT_SICI._add_borders((IT_SUD, "I"), (MT, "I"))
IT_SARD._add_borders((FR_COR, "I"), (IT_CNOR, "I"), (IT_CSUD, "I"))

SI._add_borders((AT, "EI"), (HR, "EI"), (IT_NORD, "EI"))
RO._add_borders((BG, "E"), (HU, "EI"), (RS, "E"), (UA, "E"))
HR._add_borders((BA, "E"), (HU, "E"), (RS, "E"), (SI, "EI"))
BA._add_borders((HR, "E"), (ME, "E"), (RS, "E"))
RS._add_borders(
    (AL, "E"),
    (BA, "E"),
    (BG, "E"),
    (HR, "E"),
    (HU, "E"),
    (ME, "E"),
    (MK, "E"),
    (RO, "E"),
)
ME._add_borders((AL, "E"), (BA, "E"), (IT_CSUD, "E"), (RS, "E"))
BG._add_borders((GR, "E"), (MK, "E"), (RO, "E"), (RS, "E"), (TR, "E"))
AL._add_borders((GR, "E"), (ME, "E"), (RS, "E"))
MK._add_borders((BG, "E"), (GR, "E"), (RS, "E"))
GR._add_borders((AL, "E"), (BG, "E"), (IT_SUD, "E"), (MK, "E"), (TR, "E"))


## South-Eastern Europe

TR._add_borders((BG, "E"), (GR, "E"))


## Others

RU._add_borders((EE, "N"), (FI, "E"), (LV, "N"))
RU_KGD._add_borders((LT, "E"))
BY._add_borders((LT, "E"))
UA._add_borders((HU, "E"), (PL, "E"), (RO, "E"), (SK, "E"))
MT._add_borders((IT_SICI, "I"))
