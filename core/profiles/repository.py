"""Read-only repository for versioned local calibration profiles."""

from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path

from .models import CalibrationProfile, validate_calibration_profile


_PROFILE_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
_DATA_DIR = Path(__file__).resolve().parent / "data"


class CalibrationProfileNotFound(KeyError):
    pass


def available_calibration_profiles() -> tuple[str, ...]:
    return tuple(sorted(path.stem for path in _DATA_DIR.glob("*.json") if path.is_file()))


def load_calibration_profile(profile_id: str) -> CalibrationProfile:
    """Load and validate a bundled profile by ID.

    The ID is resolved through an allowlisted filename shape; arbitrary paths
    are never accepted.
    """

    normalized = profile_id.strip()
    if not _PROFILE_ID_RE.fullmatch(normalized):
        raise ValueError(f"Invalid calibration profile ID: {profile_id!r}.")
    path = _DATA_DIR / f"{normalized}.json"
    if not path.is_file():
        available = ", ".join(available_calibration_profiles()) or "none"
        raise CalibrationProfileNotFound(
            f"Calibration profile {normalized!r} was not found; available: {available}."
        )
    document = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    if not isinstance(document, dict):
        raise ValueError(f"Calibration profile must contain a JSON object: {path}")
    profile = CalibrationProfile.from_dict(document)
    if profile.profile_id != normalized:
        raise ValueError(
            f"Calibration profile ID mismatch: filename {normalized!r}, document {profile.profile_id!r}."
        )
    validate_calibration_profile(profile)
    return profile
