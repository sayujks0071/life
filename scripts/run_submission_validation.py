#!/usr/bin/env python3
"""Run the in-repo computational/open-data checks that feed the submission pack."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]


def run(label: str, argv: list[str]) -> int:
    print(f"\n=== {label} ===")
    completed = subprocess.run(argv, cwd=PROJECT_DIR, check=False)
    if completed.returncode != 0:
        print(f"FAILED: {label} (exit {completed.returncode})")
    return completed.returncode


def main() -> int:
    python = sys.executable
    steps = [
        ("literature Cobb anchors", [python, "scripts/validate_clinical_data.py"]),
        ("PHV overlay", [python, "scripts/experiment_phv_timing.py"]),
        ("sex-specific overlay", [python, "scripts/experiment_sexual_dimorphism.py"]),
        ("SpineWeb features", [python, "scripts/validation/open_data_spineweb_features.py"]),
        ("SpineWeb geometry validation", [python, "scripts/validation/open_data_spineweb_geometry_validation.py"]),
        ("manuscript graphics", [python, "scripts/check_manuscript_figures.py"]),
    ]
    failures = 0
    for label, argv in steps:
        failures += int(run(label, argv) != 0)
    print("\n=== SUMMARY ===")
    if failures:
        print(f"{failures} step(s) failed.")
        return 1
    print("All in-repo validation steps completed.")
    print("Compile the manuscript with: make -C manuscript")
    print("See REMAINING_ITEMS.md for what is still blocking a full clinical paper.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
