"""CPU-only, non-destructive readout for the September 12 Newton rod rerun.

Legacy post-frame-fix output stores degrees(sum(abs(curvature))) instead of
an angle. Multiply by L/N exactly once. Pre-frame-fix output lacks both
out-of-plane observation arrays and is rejected rather than rescued by scaling.
The raw input is never changed. No Newton, Warp, network, or GPU import.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from rod_measure import control_drift_deg, total_absolute_bend_deg

RATES = (0.3, 1.0, 6.0)
BGS = (0.2, 0.3, 0.5)
CONDS = [(kr, bg) for kr in RATES for bg in BGS]
# Sanity bounds on total absolute planar bend, degrees. The pre-registration's original
# 1-40 deg was written against the 2026-09-03 run's 48x-inflated scale; the author adopted the
# corrected-unit bounds on 2026-09-12 (PREREG_2026-09-12.md, 'Amendment') before any full-run
# output existed. Pass --bend-bounds 1 40 to reproduce the pre-amendment reading.
BEND_BOUNDS_DEG = (0.05, 10.0)


def evaluate(payload, bend_bounds=BEND_BOUNDS_DEG):
    lo, hi = float(bend_bounds[0]), float(bend_bounds[1])
    if not (0 <= lo < hi):
        raise ValueError("bend bounds must satisfy 0 <= lo < hi")
    version = payload.get("measurement_schema_version", 1)
    if version not in (1, 2):
        raise ValueError("Unknown measurement schema; refuse a guessed unit conversion")
    params = payload["params"]
    length, nseg = float(params["L"]), int(params["n_seg"])
    if length <= 0 or not np.isfinite(length) or nseg < 2:
        raise ValueError("Invalid rod dimensions")
    seg_l = length / nseg
    factor = seg_l if version == 1 else 1.0
    obs, ctrl = payload["observations"], payload["control"]
    if "oop" not in obs or "oop" not in ctrl:
        raise ValueError("Pre-frame-fix or unproven output: missing planarity observations; do not interpret")
    if version == 2 and payload.get("measurement", {}).get("observation_age") != "end_of_month":
        raise ValueError("Schema 2 must explicitly declare end-of-month observations")
    conditions = payload.get("conditions")
    if conditions is not None and [(c["k_r"], c["B_g"]) for c in conditions] != CONDS:
        raise ValueError("Condition ordering differs from the registered nine-world protocol")
    a, c = np.asarray(obs["cobb"], float) * factor, np.asarray(ctrl["cobb"], float) * factor
    oop, ctrl_oop = np.asarray(obs["oop"], float), np.asarray(ctrl["oop"], float)
    ages = np.asarray(obs["age"], float) + (1 / 12 if version == 1 else 0)
    ctrl_ages = np.asarray(ctrl["age"], float) + (1 / 12 if version == 1 else 0)
    if (a.ndim != 2 or a.shape[1] != 9 or a.shape != c.shape or len(a) < 2
            or oop.shape != a.shape or ctrl_oop.shape != c.shape
            or ages.shape != (len(a),) or ctrl_ages.shape != ages.shape):
        raise ValueError("Malformed or mismatched observation arrays")
    if not all(np.isfinite(x).all() for x in (a, c, oop, ctrl_oop, ages, ctrl_ages)):
        raise ValueError("Non-finite observations")
    if (a < 0).any() or (c < 0).any() or (oop < 0).any() or (ctrl_oop < 0).any():
        raise ValueError("Magnitude observables must be nonnegative")
    if not np.allclose(ages, ctrl_ages) or not (np.diff(ages) > 0).all():
        raise ValueError("Control and experiment observation clocks do not match")
    months = int(params["months"])
    full = months == 180 and np.isclose(ages[-1], 20.0)
    if not np.isclose(ages[-1], 5 + months / 12):
        raise ValueError("Last observation does not match the declared simulated months")
    drift = control_drift_deg(c)
    ga = payload.get("gate_a1", {})
    a1 = bool(ga.get("pass")) and not ga.get("skipped", False)
    rows = []
    for i, (kr, bg) in enumerate(CONDS):
        raw = payload["rows"][f"k{kr}_bg{bg}"]
        kp = float(raw["rod_kappa_p_mean"])
        ode = float(raw["ode_kappa_p"]) * factor
        if not np.isfinite([kp, ode]).all() or kp < 0 or ode < 0:
            raise ValueError("Invalid permanent-curvature or scalar-comparator value")
        # mean(abs(kp_i))*(N-1)*ds equals sum(abs(kp_i))*ds, even without profiles.
        permanent = float(total_absolute_bend_deg(np.full(nseg - 1, kp), seg_l))
        observed = np.concatenate([a[:, i], c[:, i]])
        maximum_oop = float(max(oop[:, i].max(), ctrl_oop[:, i].max()))
        rows.append({
            "k_r": kr, "B_g": bg,
            "bend_first_deg": float(a[0, i]), "bend_last_deg": float(a[-1, i]),
            "all_observations_bend_min_deg": float(observed.min()),
            "all_observations_bend_max_deg": float(observed.max()),
            "control_first_deg": float(c[0, i]), "control_last_deg": float(c[-1, i]),
            "control_abs_drift_deg": float(drift[i]),
            "max_out_of_plane_tangent": maximum_oop,
            "angle_sanity_pass": bool(((observed >= lo) & (observed <= hi)).all()),
            "planarity_pass": maximum_oop < 1e-3,
            "control_drift_under_5_deg": bool(drift[i] < 5),
            "permanent_bend_deg": permanent if full else None,
            "rod_kappa_p_mean_rad_per_m": kp if full else None,
            "ode_kappa_p_unit_corrected_rad_per_m": ode if full else None,
            "rod_over_ode_unit_corrected": (kp / ode if ode else None) if full else None,
            "a2_recorded_window_pass": bool(drift[i] < permanent) if full else None,
        })
    by_bg = {}
    for bg in BGS:
        group = [r for r in rows if r["B_g"] == bg]
        sanity = all(r["angle_sanity_pass"] and r["planarity_pass"]
                     and r["control_drift_under_5_deg"] for r in group)
        a2 = all(r["a2_recorded_window_pass"] for r in group) if full else None
        order = (group[0]["rod_kappa_p_mean_rad_per_m"] > group[1]["rod_kappa_p_mean_rad_per_m"]
                 > group[2]["rod_kappa_p_mean_rad_per_m"]) if full else None
        by_bg[str(bg)] = {
            "sanity_pass": sanity, "a2_recorded_window_pass": a2,
            "descriptive_final_order": order,
            "gate_c_conditional_on_recorded_window": order if full and a1 and sanity and a2 else None,
        }
    # The old run records its first observation AFTER month 1. Never silently
    # call this a pre-treatment age-5 baseline or a complete 5-to-20-y drift gate.
    baseline = bool(np.isclose(ages[0], 5.0))
    status = ("SMOKE_ONLY_NO_GATES" if not full else
              "PREREQUISITE_FAILURE_NO_MECHANISTIC_VERDICT" if not a1 or not all(
                  b["sanity_pass"] and b["a2_recorded_window_pass"] for b in by_bg.values()) else
              "BASELINE_LIMITATION_REVIEW_REQUIRED" if not baseline else "FULL_READOUT")
    return {
        "readout_schema_version": 1, "status": status,
        "source_measurement_schema_version": version, "angle_conversion_factor": factor,
        "quantity": "total absolute planar rod bend; not clinical Cobb",
        "months": months, "full_180_month_output": bool(full), "gate_a1_pass": a1,
        "observed_age_start": float(ages[0]), "observed_age_end": float(ages[-1]),
        "pre_first_month_baseline_recorded": baseline,
        "registered_full_window_a2": "not adjudicated: baseline absent" if not baseline else "see per-world checks",
        "sanity_bounds": {"bend_deg": [lo, hi], "max_abs_t_y_exclusive": 1e-3, "control_drift_deg_exclusive": 5,
                          "bend_bounds_source": ("PREREG_2026-09-12.md Amendment (adopted 2026-09-12, corrected units)"
                                                 if (lo, hi) == BEND_BOUNDS_DEG else "command-line override")},
        "kappa_e0_unit_corrected_rad_per_m": float(np.mean(c[-1]) * np.pi / 180 / length),
        "by_bg": by_bg, "rows": rows,
        "limitations": [
            f"Bend sanity bounds applied: {lo}-{hi} deg. The original 1-40 deg was written on the 48x-inflated scale; "
            "the amended bounds were adopted before any full-run output existed (PREREG_2026-09-12.md, Amendment).",
            "A failed measurement/sanity prerequisite is not a biological null.",
            "Scalar amplitude retains the original mean-across-worlds/full-L definition; it is not a Bg-matched joint-mean calibration.",
            "No statement here validates AIS, vertebral growth, or a clinical Cobb measurement.",
        ],
    }


def markdown(r):
    lines = ["# Newton rod readout", "", f"Status: **{r['status']}**", "",
             f"Input SHA256: `{r.get('input_sha256', 'in-memory')}`.",
             f"Quantity: {r['quantity']}. Angle conversion factor: {r['angle_conversion_factor']:.12g}.",
             f"Recorded ages: {r['observed_age_start']:.6f} to {r['observed_age_end']:.6f} years.",
             f"Full-window A2: {r['registered_full_window_a2']}.", "",
             "| Bg | kr | bend min/max deg | control drift deg | permanent bend deg | bend sanity | A2 recorded window |",
             "|---|---|---|---|---|---|---|"]
    for x in r["rows"]:
        perm = "not read (smoke)" if x['permanent_bend_deg'] is None else f"{x['permanent_bend_deg']:.6g}"
        lines.append(f"| {x['B_g']} | {x['k_r']} | {x['all_observations_bend_min_deg']:.6g}/{x['all_observations_bend_max_deg']:.6g} | {x['control_abs_drift_deg']:.6g} | {perm} | {x['angle_sanity_pass']} | {x['a2_recorded_window_pass']} |")
    lines += ["", "Per-Bg checks:", "", "```json", json.dumps(r["by_bg"], indent=2), "```", ""]
    lines += [f"- {s}" for s in r["limitations"]]
    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--bend-bounds", type=float, nargs=2, metavar=("LO", "HI"), default=BEND_BOUNDS_DEG,
                   help="total-bend sanity window in degrees (default: the adopted amendment)")
    args = p.parse_args()
    data = args.input.read_bytes()
    try:
        result = evaluate(json.loads(data), bend_bounds=tuple(args.bend_bounds))
    except (KeyError, ValueError, TypeError) as exc:
        p.exit(2, f"REFUSED: {exc}\n")
    result["input_path"] = str(args.input.resolve())
    result["input_sha256"] = hashlib.sha256(data).hexdigest()
    outputs = [args.out_dir / "readout.json", args.out_dir / "READOUT.md"]
    if args.input.resolve() in [f.resolve() for f in outputs]:
        p.exit(2, "REFUSED: output would overwrite the raw input\n")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs[0].write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    outputs[1].write_text(markdown(result))
    print(f"{result['status']}: {outputs[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
