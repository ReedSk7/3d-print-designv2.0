"""Flange plate generator package."""

from .generator import FlangePlateGenerator
from .v110 import FlangePlateGeneratorV110

GENERATOR = FlangePlateGenerator()
GENERATOR_V110 = FlangePlateGeneratorV110()
GENERATORS = (GENERATOR, GENERATOR_V110)

__all__ = [
    "GENERATOR",
    "GENERATOR_V110",
    "GENERATORS",
    "FlangePlateGenerator",
    "FlangePlateGeneratorV110",
]
