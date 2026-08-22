#!/usr/bin/env python3
"""Overlay literature-extracted Cobb anchors on the model L_crit age.

The CSV in data/clinical_cohort_targets.csv contains five aggregate points
digitized from published figures/tables (Weinstein 1983, Lonstein 1984).
These are not patient-level records and are too few for inferential claims.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats


PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_DIR / "data" / "clinical_cohort_targets.csv"
OUTPUT_DIR = PROJECT_DIR / "manuscript" / "figures"
SUMMARY_PATH = PROJECT_DIR / "results" / "open_data" / "clinical_cohort_overlay_summary.json"


def main() -> None:
    print("Literature Cobb-anchor overlay (not patient-level validation)...")
    if not DATA_PATH.exists():
        print(f"Error: {DATA_PATH} not found.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(DATA_PATH)
    required = {"source", "age", "cobb_angle", "sex", "n_patients", "notes"}
    missing = required.difference(df.columns)
    if missing:
        print(f"Error: {DATA_PATH} missing columns: {sorted(missing)}")
        sys.exit(1)

    print(f"Loaded {len(df)} literature-extracted aggregate points from {DATA_PATH}.")
    print(df.to_string(index=False))

    output_path = OUTPUT_DIR / "fig_clinical_cohort_data.png"
    plt.figure(figsize=(10, 6))
    for source in df["source"].unique():
        subset = df[df["source"] == source]
        plt.scatter(subset["age"], subset["cobb_angle"], label=source, s=100, alpha=0.8)

    l_crit_age = 11.67
    plt.axvline(l_crit_age, color="r", linestyle="--", label=f"Model L_crit = 0.35 m (~{l_crit_age:.2f} y)")
    plt.axvspan(11.0, 14.0, color="red", alpha=0.1, label="Model energy-deficit window")
    plt.xlabel("Age (years)")
    plt.ylabel("Reported mean Cobb angle (degrees)")
    plt.title(
        "Literature-extracted Cobb anchors vs model L_crit\n"
        "n=5 aggregate points from published figures; not patient-level data"
    )
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Wrote {output_path}")

    summary: dict[str, object] = {
        "evidence_level": "literature-extracted aggregate anchors",
        "n_points": int(len(df)),
        "sources": sorted(df["source"].astype(str).unique().tolist()),
        "gap": (
            "No patient-level Cobb series, Risser/Sanders staging, or serial "
            "progression outcomes are in this repository. Do not treat the "
            "Pearson statistic below as clinical validation."
        ),
    }
    if len(df) >= 3:
        r, p = stats.pearsonr(df["age"].to_numpy(dtype=float), df["cobb_angle"].to_numpy(dtype=float))
        summary["age_vs_cobb_pearson_r"] = float(r)
        summary["age_vs_cobb_pearson_p"] = float(p)
        print(
            f"Descriptive Pearson r(age, Cobb) on these {len(df)} literature "
            f"points: r={r:.3f}, p={p:.2e}. Too few points for inference; "
            "not a clinical validation statistic."
        )
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {SUMMARY_PATH}")
    print("GAP: patient-level AIS cohort data are not present in this repo.")


if __name__ == "__main__":
    main()
