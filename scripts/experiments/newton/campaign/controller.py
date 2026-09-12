"""Sequential controller with immutable inputs, runtime accounting and night exclusion."""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from .core import atomic_json, available_window_seconds, default_protocol, digest, validate_protocol
from .report import make_report

ROOT=Path(__file__).resolve().parents[4]
PYTHON=Path("/home/sayuj/newton/.venv/bin/python")


def source_hashes():
    paths=list(Path(__file__).parent.glob("*.py"))
    for rel in ["scripts/experiments/recovery_comparators/models.py", "src/spinalmodes/recovery_ratchet.py", "src/spinalmodes/recovery_two_state.py"]:
        if (ROOT/rel).exists(): paths.append(ROOT/rel)
    hashes = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    # Seal the installed solver as well as project code. A package update cannot
    # silently mix numerical implementations across a multiday campaign.
    for package in [Path("/home/sayuj/newton/newton"), Path("/home/sayuj/newton/.venv/lib/python3.12/site-packages/warp")]:
        if not package.exists(): raise FileNotFoundError(package)
        h=hashlib.sha256()
        for source in sorted(package.rglob("*")):
            if source.is_file() and source.suffix in (".py", ".so", ".h", ".cpp", ".cu"):
                h.update(str(source.relative_to(package)).encode());h.update(source.read_bytes())
        hashes[str(package)]=h.hexdigest()
    return hashes


def available_gib():
    return next(int(line.split()[1])/1024**2 for line in Path("/proc/meminfo").read_text().splitlines() if line.startswith("MemAvailable:"))


def external_gpu_work():
    hits=[]
    for entry in Path("/proc").glob("[0-9]*/cmdline"):
        try: cmd=entry.read_bytes().replace(b"\0",b" ").decode(errors="replace")
        except (FileNotFoundError,PermissionError,ProcessLookupError): continue
        if int(entry.parent.name)==os.getpid(): continue
        if (cmd.startswith(str(PYTHON)) and "campaign.worker" not in cmd or
            ("timesfm_night_window.sh" in cmd or "timesfm_night_restore.sh" in cmd or "/timesfm-3.0/" in cmd) and ("python" in cmd or "bash" in cmd)):
            hits.append(entry.parent.name)
    return hits


def estimate_seconds(job, runs):
    # Conservative start estimate; use the slowest completed per-month normalized rate.
    reference=0.0
    for r in runs:
        if r["status"]=="completed":
            j=r["config"];scale=j["hz"]/60*j["iterations"]/150*(j["segments"]/24)**.5
            reference=max(reference,r["wall_seconds"]/j["months"]/scale*1.5)
    reference = reference or 100.0
    return 120+reference*job["months"]*job["hz"]/60*job["iterations"]/150*(job["segments"]/24)**.5


def used_seconds(ledger): return sum(r["wall_seconds"] for r in ledger["runs"]) + ledger.get("cpu_wall_seconds",0.)


def run_controller(args):
    protocol=validate_protocol(json.loads(args.protocol.read_text()))
    if args.max_active_hours is not None:
        if args.max_active_hours!=protocol["active_hours_cap"]: raise ValueError("Runtime cap must match the frozen protocol")
    sha=digest(protocol);hashes=source_hashes()
    if args.dry_run:
        print(json.dumps({"protocol_sha256":sha,"source_hashes":hashes,"jobs":protocol["jobs"]+[protocol["combined"]],
            "estimated_seconds":{j["id"]:estimate_seconds(j,[]) for j in protocol["jobs"]+[protocol["combined"]]}},indent=2));return
    args.out_dir.mkdir(parents=True,exist_ok=True);out=args.out_dir
    lock=(out/"controller.lock").open("a")
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    global_lock=(ROOT/"results/.newton_validation_gpu.lock")
    global_lock.parent.mkdir(parents=True,exist_ok=True)
    gpu_lock=global_lock.open("a");fcntl.flock(gpu_lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    ledger_file=out/"campaign.json"
    if ledger_file.exists():
        ledger=json.loads(ledger_file.read_text())
        if ledger["protocol_sha256"]!=sha or ledger["source_hashes"]!=hashes: raise ValueError("Frozen campaign inputs changed; use a new campaign")
        for r in ledger["runs"]:
            if r["status"]=="running":
                # The child requests SIGTERM on parent death. A missing final record
                # is conservatively charged through recovery, never given free runtime.
                r["wall_seconds"]=max(r["wall_seconds"],time.time()-r["started_epoch"])
                r["status"]="interrupted_controller_restart"
        if ledger.get("cpu_started_epoch") is not None:
            ledger["cpu_wall_seconds"]=ledger.get("cpu_wall_seconds",0.)+max(0.,time.time()-ledger.pop("cpu_started_epoch"))
            ledger["cpu_interrupted"]=True
    else:
        ledger={"schema":1,"protocol_sha256":sha,"source_hashes":hashes,"runs":[],"status":"prepared",
                "created_utc":datetime.now(timezone.utc).isoformat()}
        atomic_json(out/"protocol.json",protocol)
    last_board_update=0.
    def save(status,reason=""):
        nonlocal last_board_update
        ledger.update(status=status,reason=reason,heartbeat_utc=datetime.now(timezone.utc).isoformat(),controller_pid=os.getpid())
        atomic_json(ledger_file,ledger);assessment=make_report(out,protocol,ledger)
        task=getattr(args,"kanban_task",None)
        terminal=status in {"completed","stopped","stopped_on_failure","budget_limited","window_limited","source_changed","interrupted"}
        if task and (terminal or time.monotonic()-last_board_update>300):
            command=["hermes","kanban","--board","spine-research"]
            command += (["request-review",task,"--summary",f"Campaign {status}; {assessment['verdict']}; active hours {assessment['active_hours']:.3f}. {reason} Report: {out}/REPORT.md. Missing/failed runs are not evidence."] if terminal else ["heartbeat",task])
            try:
                update=subprocess.run(command,capture_output=True,text=True,timeout=20,env={**os.environ,"HERMES_PROFILE":"gpt-astra"})
                if update.returncode: print("Board update failed:",update.stderr.strip() or update.stdout.strip(),flush=True)
            except (OSError,subprocess.TimeoutExpired) as exc: print("Board update unavailable:",exc,flush=True)
            last_board_update=time.monotonic()
    stop=out/"STOP"
    if stop.exists(): save("stopped","STOP marker exists");return
    if ledger.get("cpu_interrupted"):
        save("stopped_on_failure","Interrupted CPU comparator process; elapsed time charged through recovery, review preserved output");return
    if not (out/"comparators/results.json").exists():
        if (out/"comparators").exists():
            save("stopped_on_failure","Incomplete CPU comparator output; preserve and review");return
        remaining=protocol["active_hours_cap"]*3600-used_seconds(ledger)
        if remaining<=35: save("budget_limited","No CPU runtime remains");return
        cpu_start=time.monotonic();ledger["cpu_started_epoch"]=time.time();save("running_cpu_comparators")
        cpu_error=None
        try:
            with (out/"comparators.log").open("a") as log:
                cp=subprocess.run([str(ROOT/".venv/bin/python"),"-m","scripts.experiments.newton.campaign.comparators",
                    "--out-dir",str(out/"comparators"),"--owner-pid",str(os.getpid())],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
                    env={**os.environ,"OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1"},timeout=min(1800,remaining-35))
            if cp.returncode: cpu_error=f"CPU comparator controls failed, exit {cp.returncode}"
        except (OSError,subprocess.TimeoutExpired) as exc:
            cpu_error=f"CPU comparator process failed: {exc}"
        finally:
            ledger["cpu_wall_seconds"]=ledger.get("cpu_wall_seconds",0.)+time.monotonic()-cpu_start
            ledger.pop("cpu_started_epoch",None)
        if cpu_error: save("stopped_on_failure",cpu_error);return
        save("cpu_comparators_completed")
    for job in protocol["jobs"]+[protocol["combined"]]:
        if any(r["job"]==job["id"] and r["status"]=="completed" for r in ledger["runs"]): continue
        if any(r["job"]==job["id"] and r["status"] in ("failed","interrupted") for r in ledger["runs"]):
            save("stopped_on_failure",f"Review failed job {job['id']} before new simulations");return
        remaining=protocol["active_hours_cap"]*3600-used_seconds(ledger)
        estimate=estimate_seconds(job,ledger["runs"])
        if remaining<=0 or estimate>remaining:
            save("budget_limited",f"Cannot admit {job['id']} within remaining active-runtime budget");return
        if estimate+600>=22*3600:
            save("window_limited",f"Estimated {job['id']} runtime cannot fit the permitted daily window; no automatic protocol changes");return
        while True:
            if source_hashes()!=hashes: save("source_changed","Sealed code changed");return
            if stop.exists(): save("stopped","STOP marker exists");return
            now=datetime.now(timezone.utc)
            window=available_window_seconds(now)
            busy=external_gpu_work()
            enough_memory=available_gib()>=protocol["min_available_gib"]
            if window>estimate+600 and not busy and enough_memory: break
            reason=f"waiting to admit {job['id']}; window_s={window:.0f}, estimate_s={estimate:.0f}, other_gpu_pids={busy}, memory_ok={enough_memory}"
            save("waiting_for_window",reason)
            if args.once: return
            time.sleep(30)
        attempt=sum(r["job"]==job["id"] for r in ledger["runs"])+1
        directory=f"runs/{job['id']}_attempt{attempt:02}"
        dest=out/directory
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists(): raise FileExistsError(dest)
        record={"job":job["id"],"directory":directory,"config":job,"status":"running","wall_seconds":0.,"started_epoch":time.time()}
        ledger["runs"].append(record);save("running")
        logfile=(dest.parent/f"{job['id']}_attempt{attempt:02}.log").open("x")
        env={**os.environ,"PYTHONUNBUFFERED":"1","OPENBLAS_NUM_THREADS":"1","OMP_NUM_THREADS":"1"}
        cmd=[str(PYTHON),"-m","scripts.experiments.newton.campaign.worker","--protocol",str(out/"protocol.json"),
             "--job",job["id"],"--out-dir",str(dest),"--stop-file",str(stop),"--owner-pid",str(os.getpid())]
        child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=logfile,stderr=subprocess.STDOUT,start_new_session=True)
        record["pid"]=child.pid;start=time.monotonic();terminated=False
        try:
            while child.poll() is None:
                record["wall_seconds"]=time.monotonic()-start
                if (used_seconds(ledger)>=protocol["active_hours_cap"]*3600-90 or available_window_seconds(datetime.now(timezone.utc))<=60
                    or available_gib()<protocol["stop_available_gib"] or stop.exists()):
                    child.terminate();terminated=True
                    try:child.wait(timeout=30)
                    except subprocess.TimeoutExpired: child.kill();child.wait()
                    break
                save("running")
                time.sleep(10)
        except BaseException:
            child.terminate()
            try:child.wait(timeout=30)
            except subprocess.TimeoutExpired:child.kill();child.wait()
            record["wall_seconds"]=time.monotonic()-start;record["status"]="interrupted";save("interrupted");raise
        record["wall_seconds"]=time.monotonic()-start
        logfile.close()
        result=dest/"result.json"
        record["status"]="completed" if child.returncode==0 and result.exists() and json.loads(result.read_text())["status"]=="completed" else "interrupted" if terminated else "failed"
        record["returncode"]=child.returncode
        save("running")
        if record["status"]!="completed": save("stopped_on_failure",f"{job['id']} is {record['status']}; no partial evidence promoted");return
        if args.once: save("between_jobs");return
    save("completed")


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--protocol",type=Path,required=True);ap.add_argument("--out-dir",type=Path,required=True)
    ap.add_argument("--max-active-hours",type=float);ap.add_argument("--dry-run",action="store_true")
    ap.add_argument("--once",action="store_true")
    ap.add_argument("--kanban-task",help="Existing manually assigned card to heartbeat and return for review")
    a=ap.parse_args();a.protocol=a.protocol.resolve();a.out_dir=a.out_dir.resolve();run_controller(a)


if __name__=="__main__":main()
