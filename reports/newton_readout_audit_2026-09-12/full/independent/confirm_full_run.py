"""Independent stdlib-only recomputation of the completed Newton result table.

Reads the original raw result and the saved amended readout, without importing
ratchet_rod_readout or rod_measure. Writes only separate confirmation artifacts.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("/home/sayuj/life"))
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    raw_path = args.repo / "results/newton_ratchet_rod/ratchet_rod.json"
    raw_bytes = raw_path.read_bytes()
    raw = json.loads(raw_bytes)
    saved_path = args.repo / "reports/newton_readout_audit_2026-09-12/full/readout.json"
    saved = json.loads(saved_path.read_text())
    sha = hashlib.sha256(raw_bytes).hexdigest()
    assert sha == saved["input_sha256"], "Saved readout is not from this raw file"
    assert raw.get("measurement_schema_version", 1) == 1, "This audit targets the completed schema-1 run"
    assert raw["params"]["months"] == 180
    ds = raw["params"]["L"] / raw["params"]["n_seg"]
    span = ds * (raw["params"]["n_seg"] - 1)
    angles, control = raw["observations"]["cobb"], raw["control"]["cobb"]
    ages = [age + 1 / 12 for age in raw["observations"]["age"]]
    bounds = saved["sanity_bounds"]["bend_deg"]
    assert bounds == [0.05, 10.0], "Unexpected amended protocol"
    assert math.isclose(ages[-1], 20)
    assert len(ages) == len(angles) == len(control) == 31
    rows, checked = [], 0
    for i, (kr, bg) in enumerate(( (k, b) for k in (.3, 1., 6.) for b in (.2, .3, .5))):
        raw_row = raw["rows"][f"k{kr}_bg{bg}"]
        saved_row = saved["rows"][i]
        assert (saved_row["k_r"], saved_row["B_g"]) == (kr, bg)
        bend = [sample[i] * ds for sample in angles]
        ctrl = [sample[i] * ds for sample in control]
        assert all(math.isfinite(x) for x in bend + ctrl)
        checks = {
            "bend_last_deg": bend[-1],
            "control_abs_drift_deg": abs(ctrl[-1] - ctrl[0]),
            "permanent_bend_deg": math.degrees(raw_row["rod_kappa_p_mean"] * span),
            "ode_kappa_p_unit_corrected_rad_per_m": raw_row["ode_kappa_p"] * ds,
            "rod_over_ode_unit_corrected": raw_row["rod_kappa_p_mean"] / (raw_row["ode_kappa_p"] * ds),
        }
        for key, value in checks.items():
            assert math.isclose(value, saved_row[key], rel_tol=1e-12, abs_tol=1e-12), (key, value, saved_row[key])
            checked += 1
        sane = all(bounds[0] <= v <= bounds[1] for v in bend + ctrl)
        a2 = checks["control_abs_drift_deg"] < checks["permanent_bend_deg"]
        assert sane == saved_row["angle_sanity_pass"]
        assert a2 == saved_row["a2_recorded_window_pass"]
        checked += 2
        crossing = next((j for j, value in enumerate(bend) if value > 10), None)
        bracket = [ages[crossing - 1], ages[crossing]] if crossing else None
        rows.append({"B_g": bg, "k_r": kr, **checks,
                     "rod_kappa_p_mean_rad_per_m": raw_row["rod_kappa_p_mean"],
                     "angle_sanity_pass": sane, "a2_recorded_window_pass": a2,
                     "first_observed_10deg_crossing_bracket_years": bracket,
                     "late_trajectory": list(zip(ages[-6:], bend[-6:]))})
    for bg in (.2, .3, .5):
        group = [r for r in rows if r["B_g"] == bg]
        ordering = group[0]["rod_kappa_p_mean_rad_per_m"] > group[1]["rod_kappa_p_mean_rad_per_m"] > group[2]["rod_kappa_p_mean_rad_per_m"]
        assert ordering == saved["by_bg"][str(bg)]["descriptive_final_order"]
        checked += 1
    assert raw["gate_a1"]["pass"] is True
    assert max(v for key in ("observations", "control") for row in raw[key]["oop"] for v in row) == 0
    summary = {
        "source_sha256": sha, "independently_matched_fields": checked,
        "sample_count": len(ages), "recorded_age_window": [ages[0], ages[-1]],
        "adopted_bounds_deg": bounds, "gate_a1_pass": True, "max_abs_t_y": 0,
        "rows": rows, "status": "MATCHES_SAVED_READOUT",
    }
    text = ["# Independent confirmation of the full Newton run", "",
            f"Raw SHA256: `{sha}`. Independently recomputed {checked} numeric/gate fields; all match Claude's saved readout.",
            "The run completed at 16:09 IST, exit=0. It used 180 model months and has 31 observations.",
            "The author-approved amendment at 15:05 IST precedes the output. This confirmation uses its 0.05–10 degree range; the original range is not substituted.", "",
            "| Bg | kr | final total bend (deg) | permanent bend (deg) | rod/ODE | amended angle sanity |",
            "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (-r["B_g"], r["k_r"])):
        text.append(f"| {r['B_g']} | {r['k_r']} | {r['bend_last_deg']:.3f} | {r['permanent_bend_deg']:.3f} | {r['rod_over_ode_unit_corrected']:.3f} | {r['angle_sanity_pass']} |")
    text += ["", "## Interpretation", "",
        "At Bg 0.3 and 0.5, sanity and recorded-window A2 pass and permanent set decreases with increasing restoration rate. This establishes the expected ordering within this imposed rod law and protocol. It is not clinical validation or evidence distinguishing the ratchet from all competing growth laws.",
        "At Bg 0.2, kr 0.3 and 1.0 reach 86.510 and 27.892 degrees, exceeding the adopted 10-degree ceiling. That group remains excluded from Gate C; descriptive ordering there is not promoted to a pass. The whole-run status remains PREREQUISITE_FAILURE_NO_MECHANISTIC_VERDICT.",
        "The first sampled exceedances are bracketed by ages 11.583–12.083 and 12.083–12.583 years, respectively. These are sampling intervals, not precise crossing times. By ages 17.583–20, the largest trajectory rises slowly from 84.728 to 86.510 degrees. These finite data do not establish mathematical divergence.",
        "A stable law-off control and zero out-of-plane tangent narrow the explanation but do not prove the high-bend law-on solution is numerically converged. The existing description of runaway cementing should be read as a mechanistic hypothesis until timestep, solver-iteration, and mesh checks are available. Large deformation alone cannot classify a solution as either solver failure or physical instability.",
        "The rod/ODE ratio uses a pooled full-rod-length calibration; Bg-matched calibration has not been applied. The quantity measured is total absolute planar rod bend, not clinical Cobb. A2 uses the recorded 5.083–20-year window; no pretreatment age-5 sample exists.",
        "", "## Next numerical check (proposed, not an adopted preregistration)", "",
        "1. Preserve this run and its amendment. Use a separate output directory and freeze the follow-up protocol before generating new results.",
        "2. Start with the informative Bg 0.2/kr 0.3 condition and a Bg 0.3/kr 0.3 reference, each with matched law-off controls. Retain all original nine conditions for any subsequent confirmatory ordering claim.",
        "3. Check mechanical timestep, VBD iterations, and segment count separately. Preserve forcing frequency, amplitude, total physical shake/settling duration, mass, length, and EI when refining. Changing only DT while leaving step counts fixed would change the experiment. Calibrate mesh-dependent statics rather than treating the discrete buckling threshold as fixed.",
        "4. Check the monthly remodeling update separately while preserving the forcing exposure per modeled year. Save an age-5 state, per-joint signed curvature and permanent set, quaternions, and stretch/constraint diagnostics so high-bend solutions can be inspected directly.",
        "5. Predeclare numerical-agreement criteria before those runs. Evaluate finite-trajectory agreement and threshold-crossing intervals; do not infer divergence from a terminal magnitude or simply raise the existing angle ceiling. Only after this should load-dependent amplification become a separate mechanistic hypothesis test.",
        "", "No new simulation, service change, manuscript edit, tag change, or hypothesis amendment was performed for this confirmation."]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "confirmation.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    (args.out_dir / "CONFIRMATION.md").write_text("\n".join(text) + "\n")
    print(json.dumps({"status": summary["status"], "matched_fields": checked, "source_sha256": sha}))


if __name__ == "__main__":
    main()
