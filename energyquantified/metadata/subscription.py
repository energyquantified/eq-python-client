import enum


class Subscription:
    """
    A subscription describing the access to a curve
    """

    def __init__(self, access, type, label, package=None, area=None,
                 collection=None, collection_perms=None):
        #: The access level for this subscription, :py:class:`SubscriptionAccess`
        self.access = access
        #: The type of subscription, :py:class:`SubscriptionType`
        self.type = type
        #: Human-readable label for this subscription
        self.label = label
        if self.type == SubscriptionType.package or self.type == SubscriptionType.package_area:
            #: The unique name of the package, only available if the type equals `package` or `package_area`
            self.package = package
        else:
            self.package = None
        if self.type == SubscriptionType.package_area:
            #: A tag representing the area, only available if the type equals `package_area`
            self.area = area
        else:
            self.area = None
        if self.type == SubscriptionType.collection:
            #: The unique name of the collection, only available if the type equals `collection`
            self.collection = collection
            #: The user's permissions for this collection, only available if the type equals `collection`,
            #: :py:class:`SubscriptionCollectionPerm`
            self.collection_perms = collection_perms
        else:
            self.collection = None
            self.collection_perms = None

    def __str__(self):
        return self.label

    def __repr__(self):
        return f"<Subscription: \"{self.label}\", access={self.access}, type={self.type}>"


_access_lookup = {}


class SubscriptionAccess(enum.Enum):
    """
    Access levels for a subscription
    """

    #: Area is included in the freemium tier
    FREEMIUM = "FREEMIUM"
    #: No access
    BLOCKED = "BLOCKED"
    #: Access is granted during a trial period
    TRIAL = "TRIAL"
    #: Access is provided through a paid subscription
    PAYING = "PAYING"
    #: Access is provided with a www.realto.io subscription
    REALTO = "REALTO"
    #: Access is provided through partner agreements
    INTERNAL = "INTERNAL"
    #: Access is available at no cost
    FREE = "FREE"
    #: Missing access information
    NONE = "NONE"

    def __init__(self, tag):
        self.tag = tag
        _access_lookup[tag.upper()] = self

    def __str__(self):
        return self.tag

    def __repr__(self):
        return f"<Access: \"{self.tag}\">"

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether an access tag exists or not.

        :param tag: An access tag
        :type tag: str
        :return: True if it exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _access_lookup[tag.upper()]

    @staticmethod
    def by_tag(tag):
        """
        Look up access by tag.

        :param tag: An access tag
        :type tag: str
        :return: The access for the given tag
        :rtype: SubscriptionAccess
        """
        return _access_lookup[tag.upper()]


_type_lookup = {}


class SubscriptionType(enum.Enum):
    """
    The type of subscription
    """

    #: A subscription related to collections
    collection = "collection"
    #: No subscription required for provided content
    free = "free"
    #: Limited access due to no subscription defined for provided content
    freemium = "freemium"
    #: A subscription associated with a package of services
    package = "package"
    #: A subscription tied to a combination of a specific package and area
    package_area = "package_area"
    #: A private subscription with restricted access
    private = "private"

    def __init__(self, tag):
        self.tag = tag
        _type_lookup[tag.lower()] = self

    def __str__(self):
        return self.tag

    def __repr__(self):
        return f"<Type: \"{self.tag}\">"

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a subscription type tag exists or not.

        :param tag: A subscription type tag
        :type tag: str
        :return: True if it exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _type_lookup

    @staticmethod
    def by_tag(tag):
        """
        Look up subscription type by tag.

        :param tag: A subscription type tag
        :type tag: str
        :return: The subscription type for the given tag
        :rtype: SubscriptionType
        """
        return _type_lookup[tag.lower()]


_collection_perm_lookup = {}


class SubscriptionCollectionPerm(enum.Enum):
    """
    The user's permissions for this collection
    """

    #: Read-only access
    r = "r"
    #: Read-write access
    rw = "rw"

    def __init__(self, tag):
        self.tag = tag
        _collection_perm_lookup[tag.lower()] = self

    def __str__(self):
        return self.tag

    def __repr__(self):
        return f"<CollectionPerm: \"{self.tag}\">"

    @staticmethod
    def is_valid_tag(tag):
        """
        Check whether a collection permission tag exists or not.

        :param tag: A collection permission tag
        :type tag: str
        :return: True if it exists, otherwise False
        :rtype: bool
        """
        return tag.lower() in _collection_perm_lookup

    @staticmethod
    def by_tag(tag):
        """
        Look up collection permission by tag.

        :param tag: A collection permission tag
        :type tag: str
        :return: The collection permission for the given tag
        :rtype: SubscriptionCollectionPerm
        """
        return _collection_perm_lookup[tag.lower()]
