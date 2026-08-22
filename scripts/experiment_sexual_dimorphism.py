#!/usr/bin/env python3
"""Sex-specific model deficit curves overlaid on published AIS onset windows.

R_peak values (2.7 female / 2.4 male) are model parameters, not measured
cohort statistics. Published onset windows come from
data/literature_epidemiology_anchors.csv.
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
SUMMARY_PATH = PROJECT_DIR / "results" / "open_data" / "sexual_dimorphism_overlay_summary.json"


def simulate_sexual_dimorphism() -> None:
    print("Sex-specific model overlay against published onset windows...")
    if not ANCHORS_PATH.exists():
        raise FileNotFoundError(f"Missing literature anchors: {ANCHORS_PATH}")

    anchors = pd.read_csv(ANCHORS_PATH)
    onset = anchors[anchors["endpoint"] == "AIS_onset_window"].copy()
    model_phv = anchors[anchors["endpoint"] == "model_PHV"].copy()

    age = np.linspace(8, 18, 100)
    t_mid_f = float(model_phv.loc[model_phv["sex"] == "F", "age_mid"].iloc[0])
    t_mid_m = float(model_phv.loc[model_phv["sex"] == "M", "age_mid"].iloc[0])
    l_min = 0.25
    l_max_f = 0.43
    l_max_m = 0.48
    l_t_f = l_min + (l_max_f - l_min) / (1 + np.exp(-1.3 * (age - t_mid_f)))
    l_t_m = l_min + (l_max_m - l_min) / (1 + np.exp(-1.1 * (age - t_mid_m)))
    dl_dt_f = np.gradient(l_t_f, age)
    dl_dt_m = np.gradient(l_t_m, age)

    r_peak_f = 2.7
    r_peak_m = 2.4
    r_t_f = (r_peak_f / l_max_f) * l_t_f
    r_t_m = (r_peak_m / l_max_m) * l_t_m
    r_eff_f = r_t_f + dl_dt_f * (r_peak_f - np.max(r_t_f)) / np.max(dl_dt_f)
    r_eff_m = r_t_m + dl_dt_m * (r_peak_m - np.max(r_t_m)) / np.max(dl_dt_m)
    r_crit = 2.5

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(age, r_eff_f, color="tab:pink", linewidth=2.5, label=f"Female model R (peak parameter {r_peak_f})")
    ax.plot(age, r_eff_m, color="tab:blue", linewidth=2.5, label=f"Male model R (peak parameter {r_peak_m})")
    ax.axhline(y=r_crit, color="black", linestyle="--", label="Model R_crit = 2.5")

    inst_f = np.where(r_eff_f > r_crit)[0]
    inst_m = np.where(r_eff_m > r_crit)[0]
    if len(inst_f) > 0:
        ax.axvspan(age[inst_f[0]], age[inst_f[-1]], color="tab:pink", alpha=0.15, label="Female model window")
    if len(inst_m) > 0:
        ax.axvspan(age[inst_m[0]], age[inst_m[-1]], color="tab:blue", alpha=0.15, label="Male model window")

    for _, row in onset.iterrows():
        color = "tab:pink" if row["sex"] == "F" else "tab:blue"
        ax.plot(
            [float(row["age_lo"]), float(row["age_hi"])],
            [r_crit - 0.08, r_crit - 0.08] if row["sex"] == "F" else [r_crit - 0.16, r_crit - 0.16],
            color=color,
            linewidth=6,
            alpha=0.45,
            solid_capstyle="butt",
            label=f"{row['source']} {row['sex']} onset window",
        )

    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Model metabolic deficit ratio R")
    ax.set_title(
        "Sex-specific model windows vs published AIS onset windows\n"
        "R_peak values are model parameters; Cheng 2015 windows are literature, not patient data"
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "fig_sexual_dimorphism.png"
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Wrote {output_path}")

    summary = {
        "evidence_level": "model overlay on published epidemiology windows",
        "model_parameters": {
            "female_R_peak": r_peak_f,
            "male_R_peak": r_peak_m,
            "R_crit": r_crit,
            "female_PHV_y": t_mid_f,
            "male_PHV_y": t_mid_m,
        },
        "literature_windows": onset.to_dict(orient="records"),
        "gap": (
            "This repository has no sex-stratified patient cohort. The widely "
            "cited 8:1 female predominance is an epidemiological fact from the "
            "literature, not a statistic computed here."
        ),
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    simulate_sexual_dimorphism()
