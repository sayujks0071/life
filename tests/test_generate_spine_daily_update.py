import os
import unittest

from scripts.generate_spine_daily_update import generate_report, parse_roadmap

TEMP_ROADMAP = "tests/temp_roadmap.md"
ROADMAP_CONTENT = """# Spine Deformity remaining-work roadmap

**Target:** *Spine Deformity* (Springer / SRS). *Spine* (LWW) is backup only.
**Start Date:** 2026-02-23
**Journal-imposed deadline:** none as of 2026-08-22

## Phase 1: Computational Framework (Weeks 1-2)

- [x] **Core Model:** Establish "Energy Deficit" model (`experiment_energy_deficit_window.py`).
- [x] **Rescue Cliff:** Validate "Rescue Cliff" at Anisotropy ~2.4 (Simulated in `outputs/sim/2026-02-22/`).
- [ ] **Spinal Jetlag:** Run "Spinal Jetlag" simulation to demonstrate circadian modulation of curvature.
- [ ] **Robustness:** Ensure model stability across parameter sweeps (Sensitivity Analysis).

## Phase 2: Clinical Validation (Weeks 3-4)

- [ ] **Cohort Data Extraction:** Extract clinical cohort data (Cobb angle distributions, progression rates) from published literature.
"""

STALE_CLOCK_ROADMAP = """# Spine Submission Roadmap

**Target:** *Spine* (IF: 3.30, Q1, H-index: 300)
**Start Date:** 2026-02-23
**Target Submission Date:** 2026-04-06 (6 Weeks)

## Phase 1: Computational Framework (Weeks 1-2)

- [x] **Core Model:** placeholder
- [ ] **Rescue Cliff:** placeholder
"""


class TestSpineUpdateScript(unittest.TestCase):

    def setUp(self):
        with open(TEMP_ROADMAP, "w") as f:
            f.write(ROADMAP_CONTENT)

    def tearDown(self):
        if os.path.exists(TEMP_ROADMAP):
            os.remove(TEMP_ROADMAP)

    def test_parse_roadmap(self):
        data, error = parse_roadmap(TEMP_ROADMAP)
        self.assertIsNone(error)
        self.assertEqual(data['total_tasks'], 5)
        self.assertEqual(data['completed_tasks'], 2)
        self.assertAlmostEqual(data['percent_complete'], 40.0)
        self.assertEqual(data['phases']['Phase 1: Computational Framework (Weeks 1-2)']['total'], 4)
        self.assertEqual(data['phases']['Phase 1: Computational Framework (Weeks 1-2)']['completed'], 2)
        self.assertIsNone(data['target_date'])

    def test_generate_report(self):
        data, error = parse_roadmap(TEMP_ROADMAP)
        report = generate_report(data)
        self.assertIn("**Target Journal:** Spine Deformity", report)
        self.assertIn("**Percent Complete:** 40.0%", report)
        self.assertIn("Phase 1: Computational Framework (Weeks 1-2)", report)
        self.assertIn("https://www.editorialmanager.com/sdef/", report)
        self.assertIn("Journal-imposed deadline:** none", report)
        self.assertIn("**Editorial Manager:** https://www.editorialmanager.com/sdef/", report)
        self.assertIn("Wrong portal:** https://www.editorialmanager.com/spde/", report)
        self.assertNotIn("**Target Deadline:**", report)
        self.assertNotIn("**Target Journal:** Spine (IF", report)
        self.assertNotIn("**Target Journal:** Spine\n", report)

    def test_stale_target_date_is_not_a_journal_clock(self):
        with open(TEMP_ROADMAP, "w") as f:
            f.write(STALE_CLOCK_ROADMAP)
        data, error = parse_roadmap(TEMP_ROADMAP)
        self.assertIsNone(error)
        self.assertIsNone(data['target_date'])
        report = generate_report(data)
        self.assertIn("Journal-imposed deadline:** none", report)
        self.assertNotIn("**Target Deadline:** 2026-04-06", report)
        self.assertIn("2026-04-06 was a self-imposed", report)


if __name__ == '__main__':
    unittest.main()
