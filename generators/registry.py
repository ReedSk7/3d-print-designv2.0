"""Generator discovery by package metadata, without CLI-specific branching."""

from __future__ import annotations

import importlib
import pkgutil
from functools import lru_cache

import generators

from .base import PartGenerator


class GeneratorNotFoundError(LookupError):
    pass


@lru_cache(maxsize=1)
def discover_generators() -> dict[str, PartGenerator]:
    discovered: dict[str, PartGenerator] = {}
    for module_info in pkgutil.iter_modules(generators.__path__):
        if not module_info.ispkg or module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"generators.{module_info.name}")
        generator = getattr(module, "GENERATOR", None)
        if generator is None:
            continue
        if not isinstance(generator, PartGenerator):
            raise TypeError(f"generators.{module_info.name}.GENERATOR is not a PartGenerator")
        generator_id = generator.metadata.generator_id
        if generator_id in discovered:
            raise RuntimeError(f"Duplicate generator ID discovered: {generator_id}")
        discovered[generator_id] = generator
    return dict(sorted(discovered.items()))


def get_generator(generator_id: str, version: str | None = None) -> PartGenerator:
    registry = discover_generators()
    try:
        generator = registry[generator_id]
    except KeyError as exc:
        available = ", ".join(registry) or "none"
        raise GeneratorNotFoundError(
            f"Unknown generator ID '{generator_id}'. Available generators: {available}."
        ) from exc
    if version is not None and generator.metadata.version != version:
        raise GeneratorNotFoundError(
            f"Generator '{generator_id}' version '{version}' is unavailable; "
            f"installed version is '{generator.metadata.version}'."
        )
    return generator
