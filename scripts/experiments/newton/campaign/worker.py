"""One isolated Newton process. No service lifecycle operations; no raw-file overwrite."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import signal
import sys
import time
from pathlib import Path
import numpy as np
from .core import atomic_json, digest, geometry, growth, observe, set_material, waveform


def build_builder(protocol, job):
    import newton
    import warp as wp
    g = protocol["geometry"]
    n = job["segments"]
    lengths, dual = geometry(n, g)
    tilt = np.radians(g["seed_tilt_deg"])
    locations = np.concatenate([[0.], np.cumsum(lengths)])
    points = [wp.vec3(float(x*np.sin(tilt)),0.,float(x*np.cos(tilt))) for x in locations]
    sub = newton.ModelBuilder()
    bodies, joints = sub.add_rod(positions=points, quaternions=newton.utils.rod_parallel_transport_quaternions(points),
        radius=g["radius_m"], stretch_stiffness=g["reference_stretch_N_per_m"],
        bend_stiffness=1., bend_damping=1., twist_stiffness=1., twist_damping=1., body_frame_origin="com")
    for i, body in enumerate(bodies):
        if i == 0:
            sub.body_mass[body]=0.;sub.body_inv_mass[body]=0.
            sub.body_inertia[body]=wp.mat33(0.);sub.body_inv_inertia[body]=wp.mat33(0.)
        else:
            mass = g["free_mass_kg"] * lengths[i] / lengths[1:].sum()
            ratio = mass / sub.body_mass[body]
            sub.body_mass[body]=float(mass); sub.body_inv_mass[body]=float(1/mass)
            sub.body_inertia[body] = wp.mat33(np.asarray(sub.body_inertia[body])*ratio)
            sub.body_inv_inertia[body] = wp.mat33(np.asarray(sub.body_inv_inertia[body])/ratio)
    builder = newton.ModelBuilder(gravity=(0.,0.,-g["gravity_m_s2"]))
    builder.replicate(sub, world_count=len(protocol["conditions"]), spacing=(0.,.5,0.))
    if len(builder.joint_type) != (n-1)*len(protocol["conditions"]):
        raise ValueError("Unexpected replicated topology")
    for w, cond in enumerate(protocol["conditions"]):
        for j, distance in enumerate(dual):
            set_material(builder,w*(n-1)+j,distance,cond["bg"],g,job["material"])
    material = {"stiffness":np.asarray(builder.joint_target_ke).reshape(-1,4).tolist(),
                "damping":np.asarray(builder.joint_target_kd).reshape(-1,4).tolist(),
                "body_mass":list(builder.body_mass), "body_inertia":np.asarray(builder.body_inertia).tolist(),
                "segment_lengths_m":lengths.tolist(),"joint_spacing_m":dual.tolist(),
                "root_length_m":float(lengths[0]),"free_length_m":float(lengths[1:].sum()),
                "inertia_convention":"builder capsule inertia scaled by mass; discretization dependence explicitly checked by mesh refinement"}
    return builder, material


def run(protocol, job, out, stop_file=None, validation_steps=None):
    import newton
    import warp as wp
    started=time.monotonic()
    stopped=[False]
    signal.signal(signal.SIGTERM,lambda *_:stopped.__setitem__(0,True))
    signal.signal(signal.SIGINT,lambda *_:stopped.__setitem__(0,True))
    builder, material=build_builder(protocol,job)
    builder.color()
    model=builder.finalize()
    solver=newton.solvers.SolverVBD(model,iterations=job["iterations"],rigid_compliant_alm=True)
    s0,s1,c=model.state(),model.state(),model.control()
    n=job["segments"];w=len(protocol["conditions"])
    roots=np.arange(w)*n; qinitial=s0.body_q.numpy().copy()
    kp=np.zeros((w,n-1));dual=np.asarray(material["joint_spacing_m"])
    parents=model.joint_parent.numpy();children=model.joint_child.numpy()
    xp=model.joint_X_p.numpy();xc=model.joint_X_c.numpy()
    load=protocol["load"];hz=job["hz"];dt=1/hz
    shake_steps=round(load["shake_seconds"]*hz)
    steps=round((load["shake_seconds"]+load["settle_seconds"])*hz)
    kr=np.array([x["kr"] for x in protocol["conditions"]])
    mask=np.array([x["law_on"] for x in protocol["conditions"]],bool)
    result={"schema":3,"job":job,"protocol_sha256":digest(protocol),"conditions":protocol["conditions"],
            "material":material,"ages":[5.],"observations":[],"shake_diagnostics":[],
            "mechanically_valid":True,"status":"running",
            "environment":{"newton":str(newton.__version__),"warp":wp.__version__,"python":sys.version,
                "newton_builder_sha256":hashlib.sha256(Path(newton.__file__).parent.joinpath("_src/sim/builder.py").read_bytes()).hexdigest()},
            "units":{"bend":"degrees total absolute planar bend, not clinical Cobb","curvature":"rad/m","age":"model years"}}
    def read_state():
        q=s0.body_q.numpy()
        if not np.isfinite(q).all() or not np.isfinite(kp).all():
            raise FloatingPointError("Nonfinite rod state")
        obs=observe(q,kp,n,dual,parents,children,xp,xc)
        tol=protocol["agreement"]
        if (obs["quaternion_error"]>tol["quaternion_norm_error"] or max(obs["out_of_plane"])>tol["planarity"]
            or max(obs["axial_anchor_strain"]+obs["shear_anchor_strain"])>tol["anchor_strain"]):
            result["mechanically_valid"]=False
        return q,obs
    def flush():
        result["wall_seconds"]=time.monotonic()-started
        atomic_json(out/"progress.json",{"job":job["id"],"months_completed":len(result["ages"])-1,
            "wall_seconds":result["wall_seconds"],"status":result["status"],"mechanically_valid":result["mechanically_valid"]})
    q,obs=read_state();result["observations"].append(obs)
    np.savez_compressed(out/"state_000.npz",body_q=q,permanent_curvature=kp)
    flush()
    total_steps=0
    try:
        for month in range(job["months"]):
            kg=protocol["growth"]["kg_peak"]*growth(5+month/12,protocol["growth"])
            fraction=kg/(kr+kg)
            for step in range(steps):
                if stopped[0] or stop_file and stop_file.exists():
                    raise InterruptedError("Controller deadline, stop request, or process signal")
                q=s0.body_q.numpy().copy()
                q[roots]=qinitial[roots]
                q[roots,0]+=waveform(step,hz,load,job["waveform"])
                s0.body_q.assign(q)
                s0.clear_forces();solver.step(s0,s1,c,None,dt);s0,s1=s1,s0
                total_steps+=1
                if validation_steps and total_steps>=validation_steps:
                    q,obs=read_state();result["validation_observation"]=obs
                    result["status"]="validation_only";flush();atomic_json(out/"result.json",result);return
                if step == shake_steps-1:
                    q,shake=read_state()
                    curv=np.asarray(shake["curvature_rad_per_m"])
                    kp += mask[:,None]*kg*(curv-kp)*fraction[:,None]/12
                    kb=np.zeros((w*(n-1),3))
                    kb[:,1]=(2*np.tan(.5*kp*dual)).reshape(-1)
                    solver.joint_rod_rest_kb_local.assign(kb)
                    result["shake_diagnostics"].append(shake)
            q,obs=read_state()
            result["ages"].append(5+(month+1)/12)
            result["observations"].append(obs)
            np.savez_compressed(out/f"state_{month+1:03}.npz",body_q=q,permanent_curvature=kp)
            flush()
            print(f"{job['id']} month={month+1}/{job['months']} wall_s={result['wall_seconds']:.1f} max_bend_deg={max(obs['bend_deg']):.6g} valid={result['mechanically_valid']}",flush=True)
        wp.synchronize();result["status"]="completed"
        flush();atomic_json(out/"result.json",result)
    except BaseException as exc:
        result["status"]="interrupted" if isinstance(exc,InterruptedError) else "failed"
        result["error"]=f"{type(exc).__name__}: {exc}"
        flush();atomic_json(out/"incomplete.json",result)
        raise


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--protocol",type=Path,required=True);ap.add_argument("--job",required=True)
    ap.add_argument("--out-dir",type=Path,required=True);ap.add_argument("--stop-file",type=Path)
    ap.add_argument("--validation-steps",type=int)
    ap.add_argument("--owner-pid",type=int)
    a=ap.parse_args()
    if a.owner_pid:
        import ctypes
        if ctypes.CDLL(None).prctl(1, signal.SIGTERM) != 0:
            raise OSError("Cannot register parent-death signal")
        if os.getppid() != a.owner_pid: raise InterruptedError("Controller already exited")
    p=json.loads(a.protocol.read_text())
    job=next(x for x in p["jobs"]+[p["combined"]] if x["id"]==a.job)
    a.out_dir.mkdir(parents=True,exist_ok=False)
    run(p,job,a.out_dir,a.stop_file,a.validation_steps)


if __name__=="__main__": main()
