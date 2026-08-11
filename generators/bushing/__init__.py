"""Bushing generator package."""

from .generator import BushingGenerator
from .v110 import BushingGeneratorV110

GENERATOR = BushingGenerator()
GENERATOR_V110 = BushingGeneratorV110()
GENERATORS = (GENERATOR, GENERATOR_V110)

__all__ = [
    "GENERATOR",
    "GENERATOR_V110",
    "GENERATORS",
    "BushingGenerator",
    "BushingGeneratorV110",
]
