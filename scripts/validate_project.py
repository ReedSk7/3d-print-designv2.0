"""Compatibility wrapper for check_project_outputs.py.

Use scripts/check_project_outputs.py for new automation.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from check_project_outputs import main as check_main


def main() -> int:
    parser = argparse.ArgumentParser(description="Compatibility wrapper.")
    parser.add_argument("project_dir")
    parser.add_argument("--version", default="v01")
    parser.add_argument(
        "--task-mode",
        default="reference_based_reconstruction",
        choices=(
            "original_product_design",
            "reference_based_reconstruction",
            "mesh_cleanup_and_remodel",
        ),
    )
    args = parser.parse_args()

    import sys

    sys.argv = [
        "check_project_outputs.py",
        "--project",
        str(Path(args.project_dir)),
        "--task-mode",
        args.task_mode,
        "--version",
        args.version,
    ]
    return check_main()


if __name__ == "__main__":
    raise SystemExit(main())
