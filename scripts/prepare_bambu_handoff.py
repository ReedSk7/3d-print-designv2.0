"""Prepare verified geometry/source copies and a manual P2S import checklist."""
import argparse
from pathlib import Path
from _repo_bootstrap import add_repo_root
add_repo_root()
from core.workflow.bambu import prepare_bambu_handoff


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--revision", default="r01")
    args = parser.parse_args()
    try:
        result = prepare_bambu_handoff(args.manifest, revision=args.revision)
    except Exception as exc:
        print(f"HANDOFF FAILED: {exc}")
        return 1
    print(f"MANUAL IMPORT HANDOFF: {result}")
    print("Bambu project: NOT VERIFIED. Automated 3MF packaging: NOT AVAILABLE. Physical fit: NOT CONFIRMED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
