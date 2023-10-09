from dataclasses import dataclass

from ..metadata import Instance


@dataclass(frozen=True)
class AbsoluteItem:
    """
    Data class for an instance-value pair used by
    :py:class:`energyquantified.data.AbsoluteResult`.
    """
    #: The instance, see :py:class:`energyquantified.metadata.Instance`
    instance: Instance
    #: The value
    value: float

    def __str__(self):
        return (
            f"<AbsoluteItem: "
            f"instance={self.instance}, "
            f"value={self.value}"
            f">"
        )
    def __repr__(self):
        return self.__str__()


class AbsoluteResult:
    def __init__(
        self,
        curve,
        resolution,
        delivery,
        filters,
        aggregation,
        unit,
        items,
    ):
        #: The curve, see :py:class:`energyquantified.metadata.Curve`
        self.curve = curve
        #: Resolution of the delivery, see
        #: :py:class:`energyquantified.time.Resolution`
        self.resolution = resolution
        #: The delivery (point in time to load values for)
        self.delivery = delivery
        #: The filter used when aggregating values (only relevant if frequency
        #: of the delivery is lower than the Curve's frequency), see
        #: :py:class:`energyquantified.metadata.Filter`
        self.filters = filters
        #: The aggregation method used (only relevant if frequency of the
        #: delivery is lower than the Curve's frequency), see
        #: :py:class:`energyquantified.metadata.Aggregation`
        self.aggregation = aggregation
        #: The unit of the result
        self.unit = unit
        #: List of :py:class:`energyquantified.data.AbsoluteItem` (instance and
        #: value pairs)
        self.items = items

    def set_curve(self, curve):
        self.curve = curve
        return self

    def frequency(self):
        """
        Get the delivery frequency (resolution.frequency).

        :return: The delivery frequency
        :rtype: Frequency
        """
        return self.resolution.frequency

    def zone(self):
        """
        Get the delivery zone (resolution.timezone).

        :return: Timezone of the delivery
        :rtype: datetime.tzinfo
        """
        return self.resolution.timezone

    def size(self):
        """
        The number of elements in :py:attr:`AbsoluteResult.items`

        :return: The number of elements in the result
        :rtype: int
        """
        return len(self.items)

    def is_empty(self):
        """
        Check if the result contains any AbsoluteItem's.

        :return: True if empty, otherwise False
        :rtype: bool
        """
        return self.size() == 0

    def begin(self):
        """
        Begin of the delivery (inclusive).

        :return: The delivery datetime
        :rtype: datetime.datetime
        """
        return self.delivery

    def end(self):
        """
        End of the delivery

        :return: End of delivery (exclusive)
        :rtype: datetime.datetime
        """
        return self.resolution.shift(self.delivery, 1)

    def __str__(self):
        parts = []
        parts.append(f"curve=\"{self.curve}\"")
        parts.append(f"resolution={self.resolution}")
        parts.append(f"delivery={self.delivery.isoformat(sep=' ')}")
        if self.filters:
            parts.append(f"filters={self.filters}")
        if self.aggregation:
            parts.append(f"aggregation={self.aggregation}")
        if self.unit:
            parts.append(f"unit={self.unit}")
        parts.append(f"items={', '.join([str(item) for item in self.items])}")
        return (
            f"<AbsoluteResult: "
            f"{', '.join(parts)}"
            f">"
        )

    def __repr__(self):
        return self.__str__()
