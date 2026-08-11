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
def _discover_generator_versions() -> tuple[
    dict[str, PartGenerator], dict[tuple[str, str], PartGenerator]
]:
    defaults: dict[str, PartGenerator] = {}
    versioned: dict[tuple[str, str], PartGenerator] = {}
    for module_info in pkgutil.iter_modules(generators.__path__):
        if not module_info.ispkg or module_info.name.startswith("_"):
            continue
        module = importlib.import_module(f"generators.{module_info.name}")
        default_generator = getattr(module, "GENERATOR", None)
        if default_generator is None:
            continue
        if not isinstance(default_generator, PartGenerator):
            raise TypeError(f"generators.{module_info.name}.GENERATOR is not a PartGenerator")
        generator_id = default_generator.metadata.generator_id
        if generator_id in defaults:
            raise RuntimeError(f"Duplicate generator ID discovered: {generator_id}")
        defaults[generator_id] = default_generator
        candidates = getattr(module, "GENERATORS", (default_generator,))
        for generator in candidates:
            if not isinstance(generator, PartGenerator):
                raise TypeError(
                    f"generators.{module_info.name}.GENERATORS contains a non-generator"
                )
            key = (generator.metadata.generator_id, generator.metadata.version)
            if generator.metadata.generator_id != generator_id:
                raise RuntimeError(
                    f"Generator package {module_info.name!r} mixes generator IDs."
                )
            if key in versioned:
                raise RuntimeError(
                    f"Duplicate generator version discovered: {key[0]} {key[1]}"
                )
            versioned[key] = generator
    return dict(sorted(defaults.items())), dict(sorted(versioned.items()))


def discover_generators() -> dict[str, PartGenerator]:
    """Return stable default generators (the original v1.0.0 implementations)."""

    defaults, _ = _discover_generator_versions()
    return dict(defaults)


def available_generator_versions(generator_id: str) -> tuple[str, ...]:
    defaults, versioned = _discover_generator_versions()
    if generator_id not in defaults:
        available = ", ".join(defaults) or "none"
        raise GeneratorNotFoundError(
            f"Unknown generator ID '{generator_id}'. Available generators: {available}."
        )
    return tuple(version for item_id, version in versioned if item_id == generator_id)


def get_generator(generator_id: str, version: str | None = None) -> PartGenerator:
    registry, versioned = _discover_generator_versions()
    try:
        generator = registry[generator_id]
    except KeyError as exc:
        available = ", ".join(registry) or "none"
        raise GeneratorNotFoundError(
            f"Unknown generator ID '{generator_id}'. Available generators: {available}."
        ) from exc
    if version is None:
        return generator
    try:
        return versioned[(generator_id, version)]
    except KeyError as exc:
        installed = ", ".join(available_generator_versions(generator_id))
        raise GeneratorNotFoundError(
            f"Generator '{generator_id}' version '{version}' is unavailable; "
            f"installed versions: {installed}."
        ) from exc
