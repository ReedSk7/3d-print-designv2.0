"""Legacy-only compatibility wrapper for check_project_outputs.py.

New automation must use validate_spec.py and generate_part.py. This wrapper
checks only the historical projects/ layout and cannot confirm physical fit.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from check_project_outputs import main as check_main


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Legacy projects/ file-presence compatibility wrapper."
    )
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

    print(
        "NOTICE: legacy file-presence check only; use validate_spec.py or "
        "generate_part.py for Parametric Part Workbench v3."
    )

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
