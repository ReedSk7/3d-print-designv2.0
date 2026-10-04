"""Record immutable physical-fit evidence for an exported complete part."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _repo_bootstrap import add_repo_root

add_repo_root()

from core.evidence import record_physical_fit, verify_physical_fit  # noqa: E402


def _load_array(path: str, label: str) -> list[dict[str, object]]:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(document, dict):
        document = document.get(label)
    if not isinstance(document, list) or not all(isinstance(item, dict) for item in document):
        raise ValueError(f"{label} input must be a JSON array of objects.")
    return document


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bind complete-part physical-fit results to exact exported artifacts."
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--confirmed-by", required=True)
    parser.add_argument("--confirmed-at", required=True, help="Timezone-aware ISO-8601 date-time.")
    parser.add_argument(
        "--interface-results-json",
        required=True,
        help="JSON array (or object key interface_results) with one passing result per protected interface.",
    )
    parser.add_argument(
        "--measured-dimensions-json",
        help="Optional JSON array (or object key measured_dimensions) of measured dimensions.",
    )
    parser.add_argument("--notes", default="")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        interface_results = _load_array(args.interface_results_json, "interface_results")
        measured_dimensions = (
            _load_array(args.measured_dimensions_json, "measured_dimensions")
            if args.measured_dimensions_json
            else []
        )
        output = record_physical_fit(
            args.manifest,
            expected_manifest_sha256=args.manifest_sha256,
            confirmed_by=args.confirmed_by,
            confirmed_at=args.confirmed_at,
            interface_results=interface_results,
            measured_dimensions=measured_dimensions,
            notes=args.notes,
        )
        verified = verify_physical_fit(output)
    except Exception as exc:
        print("PHYSICAL-FIT RECORDING FAILED", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1
    print("PHYSICAL-FIT EVIDENCE RECORDED")
    print(f"Evidence: {output}")
    print(f"Evidence SHA-256: {verified.evidence_binding.sha256}")
    print("Reached state: physical_fit_confirmed")
    print("This record makes no untested durability, load, temperature, safety, or certification claim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
