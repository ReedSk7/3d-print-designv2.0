"""Round adapter generator package."""

from .generator import RoundAdapterGenerator
from .v110 import RoundAdapterGeneratorV110

GENERATOR = RoundAdapterGenerator()
GENERATOR_V110 = RoundAdapterGeneratorV110()
GENERATORS = (GENERATOR, GENERATOR_V110)

__all__ = [
    "GENERATOR",
    "GENERATOR_V110",
    "GENERATORS",
    "RoundAdapterGenerator",
    "RoundAdapterGeneratorV110",
]
