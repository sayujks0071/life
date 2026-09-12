"""Rebuild a campaign report from completed evidence; never promote partial runs."""
import json
from pathlib import Path
from .core import atomic_json, compare

PAIRS = [("baseline","dt120"),("dt120","dt240"),("baseline","iter300"),
         ("iter300","iter600"),("baseline","mesh48"),("mesh48","mesh96"),
         ("baseline","combined"),("dt120","combined"),("iter300","combined"),("mesh48","combined")]


def make_report(out, protocol, ledger):
    complete={}
    for item in ledger["runs"]:
        path=out/item["directory"]/"result.json"
        if item["status"]=="completed" and path.exists():
            r=json.loads(path.read_text())
            if r["status"]=="completed" and r["protocol_sha256"]==ledger["protocol_sha256"]:
                complete[item["job"]]=r
    diagnostics={}
    for a,b in [("diag_legacy","diag_material"),("diag_material","diag_exact")]:
        if a in complete and b in complete:
            ra,rb=complete[a],complete[b]
            diagnostics[f"{a}_vs_{b}"]={
                "final_bend_delta_deg":[y-x for x,y in zip(ra["observations"][-1]["bend_deg"],rb["observations"][-1]["bend_deg"])],
                "mechanically_valid":[ra["mechanically_valid"],rb["mechanically_valid"]],
                "max_anchor_strain":[max(max(o["axial_anchor_strain"]+o["shear_anchor_strain"]) for o in r["observations"]+r["shake_diagnostics"]) for r in (ra,rb)]}
    comparisons={}
    for a,b in PAIRS:
        comparisons[f"{a}_vs_{b}"]=compare(complete[a],complete[b],protocol["agreement"]) if a in complete and b in complete else {"pass":None,"status":"not evaluated"}
    all_done=all(v["pass"] is not None for v in comparisons.values())
    verdict=("NUMERICAL_AGREEMENT_PASSES" if all_done and all(v["pass"] for v in comparisons.values()) else
             "NUMERICALLY_UNRESOLVED" if any(v["pass"] is False for v in comparisons.values()) else "NOT_YET_EVALUATED")
    groups={}
    if "combined" in complete and verdict=="NUMERICAL_AGREEMENT_PASSES":
        r=complete["combined"];last=r["observations"][-1]
        for bg in (.2,.3,.5):
            vals=[last["permanent_bend_deg"][i] for i,c in enumerate(r["conditions"]) if c["law_on"] and c["bg"]==bg]
            groups[str(bg)]={"permanent_bend_deg_slow_to_fast":vals,"ordering":vals[0]>vals[1]>vals[2]}
    summary={"verdict":verdict,"campaign_status":ledger["status"],"comparisons":comparisons,
             "implementation_diagnostics":diagnostics,"ordering_after_numerical_gates":groups,"active_hours":(sum(x["wall_seconds"] for x in ledger["runs"])+ledger.get("cpu_wall_seconds",0.))/3600,
             "completed_jobs":list(complete),"source_sha256":ledger.get("source_hashes",{}),
             "scope":"Computational validity only. Old material assignment invalidates interpretation as the intended rod. No clinical inference."}
    atomic_json(out/"assessment.json",summary)
    lines=["# Spine mechanism validation campaign", "",f"Status: **{ledger['status']}**. Numerical assessment: **{verdict}**.",
        f"Active simulation hours: {summary['active_hours']:.3f} / {protocol['active_hours_cap']:.1f}.","",
        "The historical run overwrote stretch/shear stiffness with angular stiffness. Its numerical table remains reproducible; its intended-mechanics interpretation is unsupported.","",
        "| Job | Status | Active hours |","|---|---|---|"]
    for run in ledger["runs"]: lines.append(f"| {run['job']} | {run['status']} | {run['wall_seconds']/3600:.3f} |")
    lines += ["", "## Implementation diagnostics", "", "Twelve-month matched comparisons isolate material assignment, then shake endpoint timing. These are implementation effects, not convergence or biological tests.", ""]
    for name,d in diagnostics.items():
        delta=d["final_bend_delta_deg"]
        lines.append(f"- {name}: final bend change across the 18 matched worlds ranges from {min(delta):.6g} to {max(delta):.6g} degrees; maximum anchor strain {d['max_anchor_strain']}; mechanical gates {d['mechanically_valid']}.")
    if not diagnostics: lines.append("Not evaluated: completed matched diagnostics are required.")
    lines += ["","## Numerical comparisons","","| Comparison | Pass |","|---|---|"]
    lines += [f"| {name} | {r['pass'] if r['pass'] is not None else 'not evaluated'} |" for name,r in comparisons.items()]
    lines += ["","## Interpretation","",
        "Numerical disagreement is an unresolved simulation, not evidence against a biological mechanism. Successful ordering within an imposed rate law alone does not distinguish mechanisms.",
        "The campaign saves initial and monthly states and shake-phase diagnostics. Axial/shear anchor strain over 1%, quaternion error over 0.001, or loss of planarity blocks numerical acceptance.",
        "Large bend is recorded without imposing a new angle-validity ceiling. Historical 10-degree exclusions remain attached to the historical experiment.",
        "Missing runs, budget exhaustion, failures and incomplete trajectories remain explicit. No partial run is used for convergence or ordering.","",
        "The complementary CPU comparator grid, when present, is in comparators/REPORT.md. It evaluates model-specific predictions and parameter sensitivity, not patient validation."]
    (out/"REPORT.md").write_text("\n".join(lines)+"\n")
    return summary
