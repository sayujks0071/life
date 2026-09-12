"""Dimensional and gate checks using explicit synthetic rod observations."""
import copy
import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/experiments/newton"))
from ratchet_rod_readout import CONDS, evaluate


def fixture(version=1, months=180):
    # True angles are 2 -> 3 deg for the experiment and 2 -> 2.1 for control.
    scale = 48 if version == 1 else 1
    age_offset = 0 if version == 1 else 1 / 12
    ages = [5 + age_offset, 5 + (months - 1) / 12 + age_offset]
    rows = {}
    for kr, bg in CONDS:
        kp = {0.3: .3, 1.0: .2, 6.0: .1}[kr]
        rows[f"k{kr}_bg{bg}"] = {"rod_kappa_p_mean": kp, "ode_kappa_p": 2 * scale}
    data = {
        "params": {"L": .5, "n_seg": 24, "months": months},
        "gate_a1": {"pass": True}, "rows": rows,
        "observations": {"age": ages, "cobb": [[2 * scale] * 9, [3 * scale] * 9], "oop": [[0] * 9] * 2},
        "control": {"age": list(ages), "cobb": [[2 * scale] * 9, [2.1 * scale] * 9], "oop": [[0] * 9] * 2},
    }
    if version == 2:
        data.update(measurement_schema_version=2, measurement={"observation_age": "end_of_month"},
                    conditions=[{"k_r": kr, "B_g": bg} for kr, bg in CONDS])
    return data


def test_legacy_units_corrected_once_and_input_preserved():
    old = fixture(); original = copy.deepcopy(old)
    legacy, current = evaluate(old), evaluate(fixture(2))
    assert old == original
    assert legacy["rows"] == current["rows"]
    assert legacy["rows"][0]["bend_last_deg"] == 3
    assert legacy["rows"][0]["rod_over_ode_unit_corrected"] == .15
    assert math.isclose(legacy["rows"][0]["permanent_bend_deg"], math.degrees(.3 * 23 * .5 / 24))
    assert math.isclose(legacy["observed_age_end"], 20)
    assert legacy["status"] == "BASELINE_LIMITATION_REVIEW_REQUIRED"


def test_control_uses_own_baseline_and_keeps_negative_drift():
    data = fixture(2)
    data["observations"]["cobb"][0] = [30] * 9
    data["control"]["cobb"] = [[5] * 9, [2] * 9]
    result = evaluate(data)
    assert all(r["control_abs_drift_deg"] == 3 for r in result["rows"])
    assert result["rows"][-1]["a2_recorded_window_pass"] is False


def test_smoke_never_reports_ordering_or_ratio():
    data = fixture(months=12); data["gate_a1"]["skipped"] = True
    result = evaluate(data)
    assert result["status"] == "SMOKE_ONLY_NO_GATES"
    assert not result["gate_a1_pass"]
    assert all(x["descriptive_final_order"] is None for x in result["by_bg"].values())
    assert all(r["rod_over_ode_unit_corrected"] is None for r in result["rows"])


def test_wrong_frame_old_result_cannot_be_rescued_by_scaling():
    data = fixture(); del data["control"]["oop"]
    with pytest.raises(ValueError, match="Pre-frame-fix"):
        evaluate(data)


def test_amended_bend_bounds_are_the_default_and_the_original_window_is_reproducible():
    """Author adopted 0.05-10 deg (corrected units) on 2026-09-12 before any full-run output existed;
    the pre-amendment 1-40 deg reading stays reproducible through bend_bounds for the record."""
    data = fixture(2); data["observations"]["cobb"][0][0] = .9
    result = evaluate(data)
    assert result["sanity_bounds"]["bend_deg"] == [0.05, 10.0]
    assert "Amendment" in result["sanity_bounds"]["bend_bounds_source"]
    assert result["rows"][0]["angle_sanity_pass"] is True
    old = evaluate(data, bend_bounds=(1, 40))
    assert old["sanity_bounds"]["bend_deg"] == [1.0, 40.0]
    assert old["rows"][0]["angle_sanity_pass"] is False
    assert old["by_bg"]["0.2"]["gate_c_conditional_on_recorded_window"] is None
    assert old["status"] == "PREREQUISITE_FAILURE_NO_MECHANISTIC_VERDICT"
    low = fixture(2); low["observations"]["cobb"][0][0] = .04
    assert evaluate(low)["rows"][0]["angle_sanity_pass"] is False
    with pytest.raises(ValueError, match="bend bounds"):
        evaluate(data, bend_bounds=(5, 1))


def test_large_angle_planarity_and_drift_gates():
    data = fixture(2)
    data["observations"]["cobb"][0][0] = 41
    data["control"]["oop"][0][1] = .001
    data["control"]["cobb"][1][2] = 8
    result = evaluate(data)
    assert not result["rows"][0]["angle_sanity_pass"]
    assert not result["rows"][1]["planarity_pass"]
    assert not result["rows"][2]["control_drift_under_5_deg"]
    assert all(x["gate_c_conditional_on_recorded_window"] is None for x in result["by_bg"].values())


def test_failed_or_skipped_statics_never_promoted():
    for gate in ({"pass": False}, {"pass": True, "skipped": True}):
        data = fixture(2); data["gate_a1"] = gate
        result = evaluate(data)
        assert all(x["gate_c_conditional_on_recorded_window"] is None for x in result["by_bg"].values())


@pytest.mark.parametrize("defect", ["nan", "shape", "age", "condition", "schema"])
def test_malformed_output_is_rejected(defect):
    data = fixture(2)
    if defect == "nan": data["observations"]["cobb"][0][0] = np.nan
    if defect == "shape": data["control"]["oop"] = []
    if defect == "age": data["control"]["age"][0] += 1
    if defect == "condition": data["conditions"].reverse()
    if defect == "schema": data["measurement_schema_version"] = 99
    with pytest.raises(ValueError): evaluate(data)
