from dataclasses import dataclass
from datetime import date

from ..metadata import ContractStructure, PPADuration, Technology
from ..utils.pandas import ppa_list_to_pandas_dataframe
from ..utils.polars import ppa_list_to_polars_dataframe


@dataclass(frozen=True)
class PPAProduct:
    """
    The dimensions that identify a power purchase agreement (PPA) price: the
    quote date, the technology, the contract structure, the delivery start
    and the duration.
    """

    date: date
    technology: Technology
    contract_structure: ContractStructure
    delivery_begin: date
    duration: PPADuration

    def __str__(self):
        return (
            f"<PPAProduct: date={self.date.isoformat()}, "
            f"technology={self.technology.name}, "
            f"contract_structure={self.contract_structure.name}, "
            f"delivery_begin={self.delivery_begin.isoformat()}, "
            f"duration={self.duration.name}>"
        )

    def __repr__(self):
        return self.__str__()


@dataclass(frozen=True)
class PPA:
    """
    A power purchase agreement (PPA) price for one product.
    """

    product: PPAProduct
    price: float

    def __str__(self):
        return f"<PPA: {self.product}, price={self.price}>"

    def __repr__(self):
        return self.__str__()


class PPAList(list):
    """
    A collection of power purchase agreement (PPA) prices for one curve. Can
    contain prices for all technologies, contract structures, delivery
    starts and durations.
    """

    def __init__(self, elements, curve=None, unit=None, denominator=None):
        super().__init__(elements)
        # --- Public members ---
        #: The curve holding these PPA objects
        self.curve = curve
        #: The unit of the prices
        self.unit = unit
        #: The denominator of the prices
        self.denominator = denominator

    def append(self, value):
        raise NotImplementedError("PPAList does not support append")

    def extend(self, iterable):
        raise NotImplementedError("PPAList does not support extend")

    def insert(self, index, value):
        raise NotImplementedError("PPAList does not support insert")

    def remove(self, value):
        raise NotImplementedError("PPAList does not support remove")

    def pop(self, index=-1):
        raise NotImplementedError("PPAList does not support pop")

    def clear(self):
        raise NotImplementedError("PPAList does not support clear")

    def __setitem__(self, key, value):
        raise NotImplementedError("PPAList does not support __setitem__")

    def __delitem__(self, key):
        raise NotImplementedError("PPAList does not support __delitem__")

    def __add__(self, rhs):
        raise NotImplementedError("PPAList does not support __add__")

    def __iadd__(self, rhs):
        raise NotImplementedError("PPAList does not support __iadd__")

    def __mul__(self, rhs):
        raise NotImplementedError("PPAList does not support multiply")

    def __rmul__(self, rhs):
        raise NotImplementedError("PPAList does not support multiply")

    def __imul__(self, rhs):
        raise NotImplementedError("PPAList does not support multiply")

    def __str__(self):
        parts = []
        if self.curve:
            parts.append(f'curve="{self.curve}"')
        if self.unit:
            parts.append(f'unit="{self.unit}"')
        if self.denominator:
            parts.append(f'denominator="{self.denominator}"')
        if len(self) > 0:
            parts.append(f"items={super().__repr__()}")
        return f"<PPAList: {', '.join(parts)}>"

    def to_pd_df(self):
        """
        Convert this PPAList to a ``pandas.DataFrame`` with a column for
        date, technology, contract structure, delivery begin, duration and
        price.

        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return self.to_pandas_dataframe()

    def to_pandas_dataframe(self):
        """
        Convert this PPAList to a ``pandas.DataFrame`` with a column for
        date, technology, contract structure, delivery begin, duration and
        price.

        :return: A DataFrame
        :rtype: pandas.DataFrame
        :raises ImportError: When pandas is not installed on the system
        """
        return ppa_list_to_pandas_dataframe(self)

    def to_pl_df(self):
        """
        Convert this PPAList to a ``polars.DataFrame`` with a column for
        date, technology, contract structure, delivery begin, duration and
        price.

        :return: A DataFrame
        :rtype: polars.DataFrame
        :raises ImportError: When polars is not installed on the system
        """
        return self.to_polars_dataframe()

    def to_polars_dataframe(self):
        """
        Convert this PPAList to a ``polars.DataFrame`` with a column for
        date, technology, contract structure, delivery begin, duration and
        price.

        :return: A DataFrame
        :rtype: polars.DataFrame
        :raises ImportError: When polars is not installed on the system
        """
        return ppa_list_to_polars_dataframe(self)
