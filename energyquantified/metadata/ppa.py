import enum

_technology_lookup = {}


class Technology(enum.Enum):
    """
    The generation technology of a power purchase agreement (PPA).

     * ``SOLAR`` – Solar power
     * ``WIND_ONSHORE`` – Onshore wind power
     * ``WIND_OFFSHORE`` – Offshore wind power
    """

    SOLAR = ("solar", "Solar")
    WIND_ONSHORE = ("wind_onshore", "Wind onshore")
    WIND_OFFSHORE = ("wind_offshore", "Wind offshore")

    def __init__(self, tag, label):
        self.tag = tag
        self.label = label
        _technology_lookup[tag.lower()] = self

    @staticmethod
    def by_tag(tag):
        """
        Look up a technology by tag.

        :param tag: The tag to look up
        :type tag: str
        :return: A Technology for this tag
        :rtype: Technology
        """
        return _technology_lookup[tag.lower()]

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a technology tag exists or not.

        :param tag: The tag to look up
        :type tag: str
        :return: True if the technology tag exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _technology_lookup

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


_contract_structure_lookup = {}


class ContractStructure(enum.Enum):
    """
    The contract structure of a power purchase agreement (PPA).

     * ``YEARLY_BASELOAD`` – Yearly baseload
     * ``MONTHLY_BASELOAD`` – Monthly baseload
     * ``PROXY`` – Proxy
     * ``PAY_AS_PRODUCED`` – Pay as produced
    """

    YEARLY_BASELOAD = ("year", "Yearly baseload")
    MONTHLY_BASELOAD = ("month", "Monthly baseload")
    PROXY = ("proxy", "Proxy")
    PAY_AS_PRODUCED = ("pay_as_produced", "Pay as produced")

    def __init__(self, tag, label):
        self.tag = tag
        self.label = label
        _contract_structure_lookup[tag.lower()] = self

    @staticmethod
    def by_tag(tag):
        """
        Look up a contract structure by tag.

        :param tag: The tag to look up
        :type tag: str
        :return: A ContractStructure for this tag
        :rtype: ContractStructure
        """
        return _contract_structure_lookup[tag.lower()]

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a contract structure tag exists or not.

        :param tag: The tag to look up
        :type tag: str
        :return: True if the contract structure tag exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _contract_structure_lookup

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


_ppa_duration_lookup = {}


class PPADuration(enum.Enum):
    """
    The duration of a power purchase agreement (PPA) in years.

     * ``THREE_YEARS`` – 3 years
     * ``FIVE_YEARS`` – 5 years
     * ``TEN_YEARS`` – 10 years
     * ``FIFTEEN_YEARS`` – 15 years
    """

    THREE_YEARS = (3,)
    FIVE_YEARS = (5,)
    TEN_YEARS = (10,)
    FIFTEEN_YEARS = (15,)

    def __init__(self, years):
        self.years = years
        _ppa_duration_lookup[years] = self

    @staticmethod
    def by_years(years):
        """
        Look up a PPA duration by its number of years.

        :param years: The number of years
        :type years: int
        :return: A PPADuration for this number of years
        :rtype: PPADuration
        """
        return _ppa_duration_lookup[years]

    @staticmethod
    def is_valid_years(years):
        """
        Check whether a PPA duration exists for a number of years or not.

        :param years: The number of years
        :type years: int
        :return: True if the PPA duration exists, otherwise False
        :rtype: bool
        """
        return years in _ppa_duration_lookup

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
