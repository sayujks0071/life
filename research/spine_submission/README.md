# Spine Submission Workflow (aligned to live track)

The live journal is **Spine Deformity** (Springer). *Spine* (LWW) is backup only.

Canonical files (repo root):

* `PUBLICATION_STATUS.md`
* `REMAINING_ITEMS.md`
* `docs/spine_submission_roadmap.md` (feeds `scripts/spine_daily_update.py`)
* `data/clinical_cohort_targets.csv` (5 literature anchors, not a cohort)
* `data/literature_epidemiology_anchors.csv`
* `data/open/` (SpineWeb/AASCE)

```bash
python3 scripts/run_submission_validation.py
python3 scripts/spine_daily_update.py
make -C manuscript
```
