"""CPU-only extension of the existing reduced-model comparisons; no fitting."""
import argparse
import json
import time
from pathlib import Path
import numpy as np
from scripts.experiments.recovery_comparators import models as M
from .core import atomic_json


def clean(x):
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple,np.ndarray)):return [clean(v) for v in x]
    if isinstance(x,(float,np.floating)):return float(x) if np.isfinite(x) else None
    if isinstance(x,np.bool_):return bool(x)
    if isinstance(x,np.integer):return int(x)
    return x


def run(out):
    started=time.monotonic();t=M.grid();ref=M.REFERENCE
    protocols={"sustained":(M.constant(1),M.growth),"zero_load":(M.constant(0),M.growth),
        "negative_load":(M.constant(-1),M.growth),"unload14":(M.step(1,0,14),M.growth),
        "reverse14":(M.step(1,-1,14),M.growth),"growth_cessation18":(M.constant(1),M.growth_ceasing),
        "no_growth":(M.constant(1),M.no_growth)}
    cases=[];trajectories={};control_errors=[]
    for model in ("scalar_signed_extension","two_state_kh0","two_state_kh0.2","stress_growth"):
        params=[(kr,mult,None) for kr in (.3,1.,6.) for mult in (.5,1.,1.5)] if model!="stress_growth" else [(None,mult,beta) for mult in (.5,1.,1.5) for beta in (.92,1.71,2.39)]
        for param_index,(kr,mult,beta) in enumerate(params):
            full={}
            for name,(segments,g) in protocols.items():
                if model=="scalar_signed_extension":
                    r=M.ratchet_law(t,kr=kr,kg_peak=mult,kappa_e0=ref["kappa_e0"],growth=g,segments=segments)
                elif model.startswith("two_state"):
                    r=M.two_state(t,kr=kr,kg_peak=mult,kh=.2 if model.endswith("0.2") else 0.,c_load=ref["c_load"],growth=g,segments=segments)
                else:
                    lam=M.lam_peak(beta,ref["G_m_peak"]*mult,ref["c_sigma"],ref["w"],ref["h"])
                    r=M.stress_growth(t,lam_peak=lam,kappa_e0=ref["kappa_e0"],growth=g,segments=segments)
                if not all(np.isfinite(r[k]).all() for k in ("time","total","structural","recoverable")):
                    raise FloatingPointError(f"Nonfinite comparator {model}/{name}")
                full[name]=r
                key=f"{model}_{param_index}_{name}"
                summary=M.summarize(r,t_mark=14 if name in ("unload14","reverse14") else None)
                if name=="unload14":
                    i=np.searchsorted(t,14);e=abs(r["recoverable"][i])
                    ids=np.flatnonzero(np.abs(r["recoverable"][i:])<=e/np.e) if e>1e-14 else [0]
                    summary["recoverable_efold_years"]=float(t[i+ids[0]]-14) if len(ids) else None
                i18=np.searchsorted(t,18)
                summary["structural_change_18_to_20"]=float(r["structural"][-1]-r["structural"][i18])
                cases.append({"model":model,"kr":kr,"growth_multiplier":mult,"beta":beta,"protocol":name,"summary":summary})
                for k in ("time","total","structural","recoverable"):
                    trajectories[f"{key}_{k}"]=r[k]
            zero=float(np.max(np.abs(full["zero_load"]["total"])))
            mirror=float(np.max(np.abs(full["sustained"]["total"]+full["negative_load"]["total"])))
            nogrowth=float(np.max(np.abs(full["no_growth"]["structural"])))
            control_errors.append({"model":model,"params":[kr,mult,beta],"zero":zero,"mirror":mirror,"no_growth_set":nogrowth})
            if max(zero,mirror,nogrowth)>1e-9: raise AssertionError(control_errors[-1])
    out.mkdir(parents=True,exist_ok=False)
    np.savez_compressed(out/"trajectories.npz",**trajectories)
    signatures={}
    for model in sorted({x["model"] for x in cases}):
        unload=[x["summary"] for x in cases if x["model"]==model and x["protocol"]=="unload14"]
        ef=[x["recoverable_efold_years"] for x in unload if x["recoverable_efold_years"] is not None]
        change=[x["structural_change_after_mark"] for x in unload]
        signatures[model]={"recoverable_efold_years_range":[min(ef),max(ef)] if ef else None,
                           "post_unload_structural_change_range":[min(change),max(change)]}
    payload=clean({"cases":cases,"control_errors":control_errors,"signatures":signatures,
        "wall_seconds":time.monotonic()-started,"status":"completed",
        "limitations":["No fitting or patient data; differences are predictions imposed by the equations.",
          "Load coefficients held fixed; amplitude and force are not interchangeable across these reduced models.",
          "Growth cessation retains the existing smooth 18-year cutoff, not an instantaneous zero.",
          "Scalar comparator uses the existing signed extension; the published unsigned API is unchanged.",
          "kr and growth-rate sensitivity are not an identified physiological parameter range."]})
    atomic_json(out/"results.json",payload)
    lines=["# Reduced-model challenge grid","",f"Completed {len(cases)} model/protocol cases. All zero-load, mirror and no-growth controls pass at 1e-9.","",
           "| Model | Recovery e-fold range (years) | Structural change after unloading range (1/m) |","|---|---|---|"]
    for name,s in signatures.items():lines.append(f"| {name} | {s['recoverable_efold_years_range']} | {s['post_unload_structural_change_range']} |")
    lines += ["","The recovery e-fold difference tests model identifiability under a prescribed intervention; it is built into the model classes. Shared decline in flexibility or a permanent-set ordering cannot select a biological mechanism.","",
        "Empirical discrimination requires independently measured loading, serial recovery over the relevant timescale, growth and regional wedging. No model is selected as biologically correct by this synthetic grid.",""]
    lines += [f"- {s}" for s in payload["limitations"]]
    (out/"REPORT.md").write_text("\n".join(lines)+"\n")
    print(f"{len(cases)} cases; controls passed; {payload['wall_seconds']:.1f}s")


def main():
    a=argparse.ArgumentParser();a.add_argument("--out-dir",type=Path,required=True)
    a.add_argument("--owner-pid",type=int);args=a.parse_args()
    if args.owner_pid:
        import ctypes, os, signal
        if ctypes.CDLL(None).prctl(1,signal.SIGTERM)!=0: raise OSError("Cannot register parent-death signal")
        if os.getppid()!=args.owner_pid: raise InterruptedError("Controller already exited")
    run(args.out_dir)
if __name__=="__main__":main()
