"""Report local workspace capabilities without installations or printer access."""
from __future__ import annotations

import argparse
import json
import sys

# Even a first diagnostic run should not create bytecode caches.
sys.dont_write_bytecode = True

from _repo_bootstrap import add_repo_root

add_repo_root()



def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable diagnostic results.")
    args = parser.parse_args()
    if sys.version_info[:2] not in ((3, 12), (3, 13)):
        report = {"required_checks_passed": False, "required_failures": ["Python"],
                  "read_only": True, "corrective_action": "Select Python 3.12 or 3.13, then run scripts/setup.ps1."}
        print(json.dumps(report) if args.json else "ENVIRONMENT CHECK FAILED: " + report["corrective_action"])
        return 1
    from core.environment import collect_environment, format_environment
    report = collect_environment()
    print(json.dumps(report, indent=2) if args.json else format_environment(report))
    return 0 if report["required_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
