#!/usr/bin/env python3
"""Overlay the model instability window on published AIS onset ages.

The growth curve itself is a model sigmoid. Published windows are loaded from
data/literature_epidemiology_anchors.csv (values already cited in
scripts/validate_tau_clinical.py). No patient-level PHV measurements are used.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
ANCHORS_PATH = PROJECT_DIR / "data" / "literature_epidemiology_anchors.csv"
OUTPUT_DIR = PROJECT_DIR / "manuscript" / "figures"
SUMMARY_PATH = PROJECT_DIR / "results" / "open_data" / "phv_overlay_summary.json"


def simulate_phv_timing() -> None:
    print("Model PHV overlay against published AIS onset windows...")
    if not ANCHORS_PATH.exists():
        raise FileNotFoundError(f"Missing literature anchors: {ANCHORS_PATH}")

    anchors = pd.read_csv(ANCHORS_PATH)
    onset = anchors[anchors["endpoint"] == "AIS_onset_window"].copy()
    model_phv = anchors[anchors["endpoint"] == "model_PHV"].copy()

    age = np.linspace(8, 18, 100)
    l_max = 0.45
    l_min = 0.25
    k_growth = 1.2
    t_mid = 12.0
    l_t = l_min + (l_max - l_min) / (1 + np.exp(-k_growth * (age - t_mid)))
    dl_dt = np.gradient(l_t, age)
    r_t = 10.0 * l_t
    r_eff = r_t * (1 + 5.0 * dl_dt)
    r_crit = 3.5

    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.set_xlabel("Age (years)")
    ax1.set_ylabel("Model growth velocity (cm/year)", color="tab:blue")
    ax1.plot(age, dl_dt * 100, color="tab:blue", linewidth=2, label="Model growth velocity")
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    ax2 = ax1.twinx()
    ax2.set_ylabel("Model metabolic deficit ratio", color="tab:red")
    ax2.plot(age, r_eff, color="tab:red", linewidth=2, linestyle="--", label="Model R_eff")
    ax2.axhline(y=r_crit, color="black", linestyle=":", label="Model R_crit")
    ax2.tick_params(axis="y", labelcolor="tab:red")

    instability = np.where(r_eff > r_crit)[0]
    instability_lo = float(age[instability[0]]) if len(instability) else float("nan")
    instability_hi = float(age[instability[-1]]) if len(instability) else float("nan")
    if len(instability) > 0:
        ax2.axvspan(instability_lo, instability_hi, color="red", alpha=0.15, label="Model instability window")

    colors = {"F": "tab:pink", "M": "tab:cyan"}
    for _, row in onset.iterrows():
        sex = str(row["sex"])
        ax1.axvspan(
            float(row["age_lo"]),
            float(row["age_hi"]),
            color=colors.get(sex, "gray"),
            alpha=0.12,
            label=f"{row['source']} {sex} onset window",
        )

    plt.title(
        "Model instability window vs published AIS onset windows\n"
        "Literature ages from Cheng 2015 (already cited in-repo); not patient PHV data"
    )
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left", fontsize=8)
    plt.grid(True, alpha=0.3)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "fig_phv_timing.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Wrote {output_path}")

    overlap: list[dict[str, object]] = []
    for _, row in onset.iterrows():
        lo = max(instability_lo, float(row["age_lo"]))
        hi = min(instability_hi, float(row["age_hi"]))
        overlap.append(
            {
                "source": row["source"],
                "sex": row["sex"],
                "literature_window": [float(row["age_lo"]), float(row["age_hi"])],
                "model_window": [instability_lo, instability_hi],
                "overlap_years": max(0.0, hi - lo),
            }
        )

    summary = {
        "evidence_level": "model overlay on published epidemiology windows",
        "model_phv_parameters": model_phv.to_dict(orient="records"),
        "overlap": overlap,
        "gap": (
            "No measured PHV, Risser, or serial Cobb trajectories are in this "
            "repository. Overlap with Cheng 2015 windows is qualitative."
        ),
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    simulate_phv_timing()
