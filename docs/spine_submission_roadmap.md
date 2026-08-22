# Spine Deformity remaining-work roadmap

**Target:** *Spine Deformity* (Springer / SRS). *Spine* (LWW) is backup only.
**Canonical status:** `PUBLICATION_STATUS.md`, `REMAINING_ITEMS.md`, `JOURNAL_TRACK.md`
**Start Date:** 2026-02-23
**Journal-imposed deadline:** none as of 2026-08-22

This file is what `scripts/spine_daily_update.py` reads. Checkbox progress is **not** a journal clock.

Do **not** put a `Target Submission Date` here. Historical dates that are **not** journal deadlines:

- **2026-04-06** — stale self-imposed 6-week target for Wolters Kluwer *Spine* (IF 3.30) from this file’s original start 2026-02-23.
- **2026-09-15** — invented internal date; removed.

## Phase 1: Computational Framework (Weeks 1-2)

- [x] **Core Model:** Energy-deficit / IEC / Cosserat work in-repo (`scripts/experiment_energy_deficit_window.py`, `manuscript/`).
- [x] **Open geometry:** SpineWeb/AASCE landmark package under `data/open/` with validation scripts.
- [x] **Status reconciliation:** May "100% ready" docs aligned to the actual computational package.
- [ ] **Robustness:** Broader published sensitivity tables beyond existing sweeps.

## Phase 2: Clinical Validation (Weeks 3-4)

- [x] **Literature anchors:** Weinstein 1983 / Lonstein 1984 aggregate points in `data/clinical_cohort_targets.csv` (n=5; not patient-level).
- [x] **PHV overlay:** Model window vs Cheng 2015 ages in `data/literature_epidemiology_anchors.csv`.
- [x] **SpineWeb geometry:** 609 public AP landmark cases; not progression validation.
- [ ] **Patient-level cohort:** Serial Cobb + Risser/Sanders + treatment (requires DUA; not in this repo).
- [ ] **Lenke types:** Multi-segment prediction against labelled curve types (not in this repo).

## Phase 3: Manuscript Preparation (Weeks 5-6)

- [x] **Live manuscript:** `manuscript/main.tex` is the Spine Deformity IMRaD computational paper.
- [x] **Honest claims:** Abstract/results no longer call synthetic N=1000 "clinical validation".
- [x] **Compile path:** `make -C manuscript` + figure checker.
- [ ] **Zenodo DOI** in availability.tex after a GitHub release.
- [ ] **Portal submit** by the author (credentials required; https://www.editorialmanager.com/sdef/ not /spde/).
