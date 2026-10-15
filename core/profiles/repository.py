"""Read-only repository for versioned local calibration profiles."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Mapping, Sequence

from .models import CalibrationProfile, validate_calibration_profile


_PROFILE_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
_DATA_DIR = Path(__file__).resolve().parent / "data"


class CalibrationProfileNotFound(KeyError):
    pass


@dataclass(frozen=True, slots=True)
class CalibrationProfileRecord:
    """A validated profile plus a platform-independent content fingerprint."""

    profile: CalibrationProfile
    content_sha256: str


def available_calibration_profiles() -> tuple[str, ...]:
    return tuple(sorted(path.stem for path in _DATA_DIR.glob("*.json") if path.is_file()))


def _canonical_profile_value(value: object) -> object:
    if isinstance(value, Decimal):
        rendered = format(value.normalize(), "f")
        return "0" if rendered in {"-0", ""} else rendered
    if isinstance(value, Mapping):
        return {
            str(key): _canonical_profile_value(item)
            for key, item in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_canonical_profile_value(item) for item in value]
    return value


def _profile_record(profile_id: str) -> CalibrationProfileRecord:
    """Read, validate, and fingerprint one exact semantic profile document.

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
    document = json.loads(
        path.read_text(encoding="utf-8"),
        parse_float=Decimal,
        parse_int=Decimal,
    )
    if not isinstance(document, dict):
        raise ValueError(f"Calibration profile must contain a JSON object: {path}")
    profile = CalibrationProfile.from_dict(document)
    if profile.profile_id != normalized:
        raise ValueError(
            f"Calibration profile ID mismatch: filename {normalized!r}, document {profile.profile_id!r}."
        )
    validate_calibration_profile(profile)
    canonical = json.dumps(
        _canonical_profile_value(document),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return CalibrationProfileRecord(
        profile=profile,
        content_sha256=sha256(canonical).hexdigest(),
    )


def load_calibration_profile_record(profile_id: str) -> CalibrationProfileRecord:
    """Return a profile and digest computed from the same parsed document."""

    return _profile_record(profile_id)


def load_calibration_profile(profile_id: str) -> CalibrationProfile:
    """Load and validate a bundled profile by ID."""

    return _profile_record(profile_id).profile
