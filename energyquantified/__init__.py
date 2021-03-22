"""
Energy Quantified Time Series API client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""

# Add a default void log handler to avoid "No handler found" warnings
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())


# Package info
from .__version__ import (
    __title__,
    __description__,
    __url__,
    __version__,
)


# The client implementation
from .base import EnergyQuantified, RealtoConnection


__all__ = [
    "EnergyQuantified",
    "RealtoConnection",
]
