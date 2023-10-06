from dataclasses import dataclass

from ..metadata import Instance


@dataclass(frozen=True)
class AbsoluteItem:
    instance: Instance
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
        self.curve = curve
        self.resolution = resolution
        self.delivery = delivery
        self.filters = filters
        self.aggregation = aggregation
        self.unit = unit
        self.items = items

    def set_curve(self, curve):
        self.curve = curve
        return self

    def frequency(self):
        return self.resolution.frequency

    def zone(self):
        return self.resolution.timezone

    def size(self):
        return len(self.items)

    def is_empty(self):
        return self.size() == 0

    def begin(self):
        return self.delivery

    def end(self):
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