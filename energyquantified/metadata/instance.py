

class Instance:
    """
    An instance identifies a forecast or any other time series that
    was issued at a specific time.

    It is typically used to specify a weather forecast that a specific
    forecast is based on.

    An instance is identified by the combination of ``(issued, tag)``.
    """

    def __init__(self, issued, tag='', scenarios=None,
                 created=None, modified=None):
        assert issued, "issued cannot be None"
        assert tag is not None, "tag cannot be None"
        #: The issue date of this instance
        self.issued = issued
        #: The tag for this instance
        self.tag = tag
        #: The number of scenarios available in this instance (default=0)
        self.scenarios = scenarios
        #: When this instance was created (if available)
        self.created = created
        #: When this instance was modified (if available)
        self.modified = modified

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.scenarios:
            return (
                f"<Instance: issued=\"{self.issued}\", tag=\"{self.tag}\", "
                f"scenarios={self.scenarios}>"
            )
        else:
            return f"<Instance: issued=\"{self.issued}\", tag=\"{self.tag}\">"