"""Pure protocol, geometry, loading, and comparison functions (no GPU imports)."""
from __future__ import annotations
import hashlib
import json
import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import numpy as np

IST = ZoneInfo("Asia/Kolkata")
RATES = [0.3, 1.0, 6.0]
BGS = [0.2, 0.3, 0.5]
BASE_DS = 0.5 / 24
REFERENCE_MASS = 0.07500238442636259


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def atomic_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    tmp.replace(path)


def default_protocol():
    configs = [("baseline", 60, 150, 24), ("dt120", 120, 150, 24),
               ("iter300", 60, 300, 24), ("mesh48", 60, 150, 48),
               ("dt240", 240, 150, 24), ("iter600", 60, 600, 24),
               ("mesh96", 60, 150, 96)]
    jobs = [{"id": name, "hz": hz, "iterations": it, "segments": n,
             "months": 180, "material": "corrected", "waveform": "exact"}
            for name, hz, it, n in configs]
    diagnostics = [{"id": name, "hz": 60, "iterations": 150, "segments": 24,
                    "months": 12, "material": mat, "waveform": wave}
                   for name, mat, wave in [("diag_legacy", "legacy", "legacy"),
                                          ("diag_material", "corrected", "legacy"),
                                          ("diag_exact", "corrected", "exact")]]
    return {"schema": 1, "purpose": "implementation and numerical falsification; no clinical inference",
            "active_hours_cap": 48.0, "night_exclusion_ist": [23, 1],
            "min_available_gib": 6.0, "stop_available_gib": 3.0,
            "conditions": [{"kr": kr, "bg": bg, "law_on": law} for law in (False, True) for kr in RATES for bg in BGS],
            "geometry": {"length_m": .5, "radius_m": .006, "fixed_root_length_m": BASE_DS,
                         "free_mass_kg": REFERENCE_MASS, "gravity_m_s2": 9.81, "seed_tilt_deg": .5,
                         "reference_stretch_N_per_m": 1e7, "linear_damping": 0.0,
                         "angular_relaxation_time_s": 1.0},
            "load": {"shake_seconds": 8.0, "settle_seconds": 10.0, "hz": .25, "amplitude_m": .004},
            "growth": {"peak_years": 12.0, "sigma_years": 1.6, "baseline": .08, "kg_peak": 1.0},
            "agreement": {"absolute_bend_deg": .1, "relative_peak": .05, "crossing_age_years": 1/12,
                          "quaternion_norm_error": 1e-3, "planarity": 1e-3, "anchor_strain": .01},
            "jobs": diagnostics + jobs,
            "combined": {"id": "combined", "hz": 120, "iterations": 300, "segments": 48,
                         "months": 180, "material": "corrected", "waveform": "exact"},
            "growth_update_refinement": "not part of the accepted fixed matrix; requires a separate protocol if numerical results demand it",
            "policy": "No angle ceiling is a solver-validity test in this campaign; retain historical exclusions separately. No successful ordering alone establishes biology."}


def validate_protocol(p):
    if p.get("schema") != 1 or not (0 < p["active_hours_cap"] <= 48):
        raise ValueError("Unknown protocol or cap outside approved 48 hours")
    if p["conditions"] != default_protocol()["conditions"]:
        raise ValueError("The registered 18 matched worlds must remain in order")
    expected=default_protocol()
    if p["jobs"]!=expected["jobs"] or p["combined"]!=expected["combined"]:
        raise ValueError("Registered diagnostic and refinement matrix changed")
    if p["night_exclusion_ist"]!=[23,1] or p["min_available_gib"]<6 or p["stop_available_gib"]<3:
        raise ValueError("Approved resource exclusions changed")
    for j in p["jobs"] + [p["combined"]]:
        if j["hz"] not in (60, 120, 240) or j["iterations"] not in (150, 300, 600):
            raise ValueError("Unregistered timestep or iteration count")
        if j["segments"] not in (24, 48, 96) or j["months"] not in (12, 180):
            raise ValueError("Unregistered geometry or horizon")
        if j["material"] not in ("legacy", "corrected") or j["waveform"] not in ("legacy", "exact"):
            raise ValueError("Unknown diagnostic variant")
    return p


def geometry(n, g):
    lengths = np.full(n, (g["length_m"] - g["fixed_root_length_m"]) / (n - 1))
    lengths[0] = g["fixed_root_length_m"]
    dual = (lengths[:-1] + lengths[1:]) / 2
    return lengths, dual


def waveform(step, hz, load, mode):
    shake_steps = round(load["shake_seconds"] * hz)
    if mode == "legacy":
        # Existing code holds its final, nonzero sample throughout settling.
        t = min(step, shake_steps - 1) / hz
    else:
        t = min((step + 1) / hz, load["shake_seconds"])
        if t >= load["shake_seconds"]:
            return 0.0
    return load["amplitude_m"] * math.sin(2 * math.pi * load["hz"] * t)


def growth(age, p):
    return (p["baseline"] + math.exp(-.5 * ((age - p["peak_years"]) / p["sigma_years"])**2)) / (1 + p["baseline"])


def set_material(builder, joint, dual_length, bg, g, mode):
    if tuple(builder.joint_dof_dim[joint]) != (2, 2):
        raise ValueError("Unknown Newton rod DOF layout")
    start = builder.joint_qd_start[joint]
    bend = bg * g["free_mass_kg"] * g["gravity_m_s2"] * g["length_m"]**2 / dual_length
    linear = g["reference_stretch_N_per_m"] * g["fixed_root_length_m"] / dual_length
    ke = [linear, linear, bend, bend]
    kd = [g["linear_damping"], g["linear_damping"], bend * g["angular_relaxation_time_s"], bend * g["angular_relaxation_time_s"]]
    if mode == "legacy":
        ke, kd = [bend] * 4, [bend] * 4
    # Use the installed typed setter so target modes follow gains. Explicit slot
    # assertions prevent an API change silently changing the physical model.
    builder._set_joint_rod_material_gains(joint, stretch_stiffness=ke[0], shear_stiffness=ke[1],
        bend_stiffness=ke[2], twist_stiffness=ke[3], stretch_damping=kd[0], shear_damping=kd[1],
        bend_damping=kd[2], twist_damping=kd[3])
    if not np.allclose(builder.joint_target_ke[start:start+4], ke):
        raise ValueError("Material assignment did not reach expected slots")
    return ke, kd


def rotate(q, v):
    xyz = q[..., :3]
    t = 2 * np.cross(xyz, v)
    return v + q[..., 3:4] * t + np.cross(xyz, t)


def observe(q, kp, n, dual, parents, children, xp, xc):
    w = len(q) // n
    quat = q[:, 3:7]
    tangent = rotate(quat, np.broadcast_to([0., 0., 1.], (len(q), 3)))
    theta = np.unwrap(np.arctan2(tangent[:, 0].reshape(w,n), tangent[:, 2].reshape(w,n)), axis=1)
    dtheta = np.diff(theta, axis=1)
    curv = dtheta / dual
    ap = q[parents, :3] + rotate(quat[parents], xp[:, :3])
    ac = q[children, :3] + rotate(quat[children], xc[:, :3])
    gap = ac - ap
    ax = np.sum(gap * tangent[parents], axis=1)
    shear = np.linalg.norm(gap - ax[:, None] * tangent[parents], axis=1)
    return {"bend_deg": np.degrees(np.abs(dtheta).sum(axis=1)).tolist(),
            "permanent_bend_deg": np.degrees((np.abs(kp) * dual).sum(axis=1)).tolist(),
            "curvature_rad_per_m": curv.tolist(), "permanent_curvature_rad_per_m": kp.tolist(),
            "out_of_plane": np.max(np.abs(tangent[:,1].reshape(w,n)), axis=1).tolist(),
            "quaternion_error": float(np.max(np.abs(np.linalg.norm(quat,axis=1)-1))),
            "axial_anchor_strain": np.max(np.abs(ax.reshape(w,n-1)) / dual,axis=1).tolist(),
            "shear_anchor_strain": np.max(shear.reshape(w,n-1) / dual,axis=1).tolist(),
            "root_x_m": q[np.arange(w)*n,0].tolist()}


def available_window_seconds(now):
    now = now.astimezone(IST)
    if now.hour >= 23 or now.hour < 1:
        return 0.0
    end = now.replace(hour=23, minute=0, second=0, microsecond=0)
    return (end-now).total_seconds()


def compare(a, b, tolerance):
    if a["conditions"] != b["conditions"] or a["ages"] != b["ages"]:
        raise ValueError("Unmatched conditions or observation ages")
    fields = {}
    for key in ("bend_deg", "permanent_bend_deg"):
        x = np.asarray([r[key] for r in a["observations"]]); y = np.asarray([r[key] for r in b["observations"]])
        err = np.max(np.abs(x-y),axis=0)
        allowed = np.maximum(tolerance["absolute_bend_deg"], tolerance["relative_peak"]*np.max(np.abs(y),axis=0))
        fields[key] = {"max_error_deg": err.tolist(), "allowed_error_deg": allowed.tolist(), "pass": bool(np.all(err<=allowed))}
    crossings=[]
    for i in range(len(a["conditions"])):
        times=[]
        for r in (a,b):
            times.append(next((age for age,o in zip(r["ages"],r["observations"]) if o["bend_deg"][i]>10),None))
        crossings.append(times[0] is None and times[1] is None or times[0] is not None and times[1] is not None and abs(times[0]-times[1])<=tolerance["crossing_age_years"]+1e-10)
    return {"fields":fields,"crossing_pass_per_world":crossings,
            "pass": all(x["pass"] for x in fields.values()) and all(crossings) and a["mechanically_valid"] and b["mechanically_valid"]}
