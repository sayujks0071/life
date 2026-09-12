"""Tests target physical invariants and campaign acceptance, not biological claims."""
import copy
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import numpy as np
import pytest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.experiments.newton.campaign.core import (BASE_DS, available_window_seconds, compare,
    default_protocol, digest, geometry, observe, validate_protocol, waveform)
from scripts.experiments.newton.campaign.controller import estimate_seconds, run_controller, used_seconds


def test_protocol_preserves_all_nine_matched_conditions():
    p=validate_protocol(default_protocol())
    assert len(p["conditions"])==18
    assert [x["kr"] for x in p["conditions"][:9]]==[.3]*3+[1.]*3+[6.]*3
    for a,b in zip(p["conditions"][:9],p["conditions"][9:]):
        assert a["kr"]==b["kr"] and a["bg"]==b["bg"] and not a["law_on"] and b["law_on"]
    assert p["combined"]["hz"]==120 and p["combined"]["iterations"]==300 and p["combined"]["segments"]==48


@pytest.mark.parametrize("n",[24,48,96])
def test_geometry_preserves_physical_clamp_and_length(n):
    lengths,dual=geometry(n,default_protocol()["geometry"])
    assert math.isclose(lengths.sum(),.5)
    assert lengths[0]==BASE_DS
    assert math.isclose(lengths[1:].sum(),.5-BASE_DS)
    assert np.allclose(dual,(lengths[:-1]+lengths[1:])/2)


@pytest.mark.parametrize("hz",[60,120,240])
def test_exact_loading_at_common_times_and_complete_settling(hz):
    p=default_protocol()["load"]
    for t in (.5,1.,7.5,8.,12.,18.):
        actual=waveform(round(t*hz)-1,hz,p,"exact")
        expected=.004*math.sin(2*math.pi*.25*t) if t<8 else 0.
        assert abs(actual-expected)<1e-14
    assert all(waveform(s,hz,p,"exact")==0 for s in range(8*hz,18*hz))


def test_legacy_waveform_reproduces_the_residual_offset():
    load=default_protocol()["load"]
    expected=.004*math.sin(2*math.pi*.25*(8-1/60))
    assert expected!=0
    assert math.isclose(waveform(1000,60,load,"legacy"),expected)
    assert waveform(1000,60,load,"exact")==0


@pytest.mark.parametrize("n",[24,48,96])
def test_real_builder_materials_and_mass_are_correct_after_replication(n):
    pytest.importorskip("newton")
    from scripts.experiments.newton.campaign.worker import build_builder
    p=default_protocol();j=dict(p["jobs"][2],segments=n)
    builder,m=build_builder(p,j)
    ke=np.array(m["stiffness"]).reshape(18,n-1,4);kd=np.array(m["damping"]).reshape(18,n-1,4)
    dual=np.array(m["joint_spacing_m"])
    for w,c in enumerate(p["conditions"]):
        EI=c["bg"]*p["geometry"]["free_mass_kg"]*9.81*.5**2
        assert np.allclose(ke[w,:,0]*dual,1e7*BASE_DS)
        assert np.allclose(ke[w,:,1],ke[w,:,0])
        assert np.allclose(ke[w,:,2]*dual,EI)
        assert np.allclose(ke[w,:,3],ke[w,:,2])
        assert np.all(kd[w,:,:2]==0)
        assert np.allclose(kd[w,:,2:],ke[w,:,2:])
    mass=np.array(m["body_mass"]).reshape(18,n)
    assert np.all(mass[:,0]==0)
    assert np.allclose(mass[:,1:].sum(axis=1),p["geometry"]["free_mass_kg"])
    single=copy.deepcopy(p);single["conditions"]=[p["conditions"][4]]
    _,ms=build_builder(single,j)
    assert np.allclose(ms["stiffness"],ke[4])
    assert np.allclose(ms["damping"],kd[4])


def test_legacy_material_case_captures_confirmed_overwrite():
    pytest.importorskip("newton")
    from scripts.experiments.newton.campaign.worker import build_builder
    p=default_protocol();_,m=build_builder(p,p["jobs"][0])
    ke=np.array(m["stiffness"])
    assert np.allclose(ke,ke[:,0,None])
    assert ke[0,0]<10


def test_unknown_layout_is_rejected():
    from scripts.experiments.newton.campaign.core import set_material
    with pytest.raises(ValueError,match="DOF"):
        set_material(SimpleNamespace(joint_dof_dim=[(3,3)]),0,BASE_DS,.2,default_protocol()["geometry"],"corrected")


def test_state_diagnostics_measure_anchor_gaps_in_physical_units():
    dual=np.array([.1,.1]);q=np.array([[0,0,z,0,0,0,1] for z in (.05,.15,.25)],float)
    xp=np.array([[0,0,.05,0,0,0,1]]*2);xc=np.array([[0,0,-.05,0,0,0,1]]*2)
    def obs():return observe(q,np.zeros((1,2)),3,dual,np.array([0,1]),np.array([1,2]),xp,xc)
    r=obs();assert r["bend_deg"]==[0.] and r["quaternion_error"]==0
    assert max(r["axial_anchor_strain"])<1e-14
    q[-1,2]+=.001
    assert np.allclose(obs()["axial_anchor_strain"],[.01])
    q[-1,0]+=.002
    assert np.allclose(obs()["shear_anchor_strain"],[.02])


def result(bend):
    return {"conditions":[0,1],"ages":[5.,20.],"observations":[{"bend_deg":[0.,0.],"permanent_bend_deg":[0.,0.]},{"bend_deg":[bend,2.],"permanent_bend_deg":[1.,.2]}],"mechanically_valid":True}


def test_comparison_does_not_allow_missing_crossing_or_failed_mechanics():
    tol=default_protocol()["agreement"]
    assert compare(result(2),result(2.05),tol)["pass"]
    assert not compare(result(9.99),result(10.01),tol)["pass"]
    bad=result(2);bad["mechanically_valid"]=False
    assert not compare(result(2),bad,tol)["pass"]
    assert not compare(result(2),result(3),tol)["pass"]


@pytest.mark.parametrize("hour,minutes",[(23,0),(0,30),(0,59)])
def test_night_window_blocks_launches(hour,minutes):
    assert available_window_seconds(datetime(2026,9,13,hour,minutes,tzinfo=ZoneInfo("Asia/Kolkata")))==0


def test_window_and_runtime_accounting_include_cpu_and_interrupted_runs():
    assert available_window_seconds(datetime(2026,9,13,22,tzinfo=ZoneInfo("Asia/Kolkata")))==3600
    assert used_seconds({"runs":[{"wall_seconds":90,"status":"interrupted"}],"cpu_wall_seconds":10})==100
    job=default_protocol()["jobs"][3]
    calibrated=estimate_seconds(job,[{"status":"completed","config":dict(job,months=12),"wall_seconds":360}])
    assert 180*45<calibrated<180*100


def test_dry_run_does_not_create_output_directory(tmp_path):
    proto=tmp_path/"p.json";proto.write_text(json.dumps(default_protocol()))
    output=tmp_path/"out"
    run_controller(SimpleNamespace(protocol=proto,out_dir=output,max_active_hours=48,dry_run=True,once=False))
    assert not output.exists()


def test_protocol_rejects_budget_expansion_and_condition_deletion():
    p=default_protocol();p["active_hours_cap"]=49
    with pytest.raises(ValueError):validate_protocol(p)
    p=default_protocol();p["conditions"].pop()
    with pytest.raises(ValueError):validate_protocol(p)
    p=default_protocol();before=digest(p);p["load"]["amplitude_m"]*=2;assert digest(p)!=before


def test_frozen_matrix_cannot_silently_drop_a_refinement():
    p=default_protocol();p["jobs"].pop()
    with pytest.raises(ValueError,match="matrix"):validate_protocol(p)
    p=default_protocol();p["night_exclusion_ist"]=[0,0]
    with pytest.raises(ValueError,match="exclusions"):validate_protocol(p)


def test_report_requires_all_refinements_and_ignores_partial_runs(tmp_path):
    from scripts.experiments.newton.campaign.report import make_report,PAIRS
    p=default_protocol();sha=digest(p);ledger={"runs":[],"status":"running","protocol_sha256":sha}
    for name in sorted({n for pair in PAIRS for n in pair}):
        path=tmp_path/name;path.mkdir()
        r=result(2);r.update(status="completed",protocol_sha256=sha,conditions=p["conditions"],shake_diagnostics=[])
        for o in r["observations"]:
            o["bend_deg"]=[2.]*18;o["permanent_bend_deg"]=[0.]*9+[3.,3.,3.,2.,2.,2.,1.,1.,1.]
        (path/"result.json").write_text(json.dumps(r))
        ledger["runs"].append({"job":name,"directory":name,"status":"completed","wall_seconds":1.})
    r=make_report(tmp_path,p,ledger)
    assert r["verdict"]=="NUMERICAL_AGREEMENT_PASSES"
    assert all(x["ordering"] for x in r["ordering_after_numerical_gates"].values())
    ledger["runs"][-1]["status"]="interrupted"
    r=make_report(tmp_path,p,ledger)
    assert r["verdict"]=="NOT_YET_EVALUATED" and not r["ordering_after_numerical_gates"]


def test_restart_refuses_source_change_and_charges_missing_runtime(tmp_path,monkeypatch):
    from scripts.experiments.newton.campaign import controller as C
    monkeypatch.setattr(C,"ROOT",tmp_path)
    monkeypatch.setattr(C,"source_hashes",lambda:{"solver":"current"})
    p=default_protocol();proto=tmp_path/"p.json";proto.write_text(json.dumps(p))
    out=tmp_path/"run";out.mkdir();(out/"comparators").mkdir();(out/"comparators/results.json").write_text('{}')
    ledger={"protocol_sha256":digest(p),"source_hashes":{"solver":"old"},"runs":[],"status":"running"}
    (out/"campaign.json").write_text(json.dumps(ledger))
    args=SimpleNamespace(protocol=proto,out_dir=out,max_active_hours=48,dry_run=False,once=True)
    with pytest.raises(ValueError,match="Frozen"):C.run_controller(args)
    ledger["source_hashes"]={"solver":"current"}
    ledger["runs"]=[{"job":"diag_legacy","directory":"missing","status":"running","wall_seconds":1.,"started_epoch":1.}]
    (out/"campaign.json").write_text(json.dumps(ledger))
    monkeypatch.setattr(C.time,"time",lambda:172801.)
    C.run_controller(args)
    got=json.loads((out/"campaign.json").read_text())
    assert got["status"]=="budget_limited"
    assert got["runs"][0]["wall_seconds"]==172800.
    assert got["runs"][0]["status"]=="interrupted_controller_restart"
