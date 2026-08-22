# Publication Status (honest, 2026-08-22)

**Live journal:** *Spine Deformity* (Springer; official journal of the Scoliosis Research Society)
**Backup journal:** *Spine* (LWW) — only if *Spine Deformity* desks the paper
**Manuscript:** `manuscript/main.tex` — *Active Geometric Maintenance of the Spinal S-Curve Against Gravity: An Information--Mechanical Coupling Model for Adolescent Idiopathic Scoliosis Onset*
**Status:** Computational/theory package can be compiled and submitted as a **hypothesis-generating computational article**. It is **not** 100% clinically validated and **has not** been shown in this repo to be already submitted.

---

## Why this supersedes the May 2026 pack and the August daily tracker

| Source | Claim | Verdict |
|---|---|---|
| `START_HERE.txt` / `PUBLICATION_STATUS.md` (2026-05-05) | 100% ready; 30 minutes to submit; sometimes implied already submitted | **Stale.** No manuscript ID, no `v1.0.0-submission` tag, `final_verification.sh` looked in the wrong figure directory (`figures/main`). |
| `CITATION.cff` (2026-05-11) | `status: submitted` to Spine Deformity | **Overstated.** Treat as in preparation until an Editorial Manager ID exists. |
| `reports/daily_update_latest.md` (auto, Aug 2026) | Target *Spine*; 23% complete; clinical validation 0% | **Partly honest on the gap, wrong on the journal.** The generator hardcoded *Spine* and read `docs/spine_submission_roadmap.md`, a parallel 6-week checklist. Live track is *Spine Deformity*. |
| `submission_package/SUBMISSION_CHECKLIST.md` | Different title (“Derivative Gain Gap”); says no patient data yet | Parallel draft, not the live `main.tex`. |

**Live track = Spine Deformity + `manuscript/main.tex`.** The May pack is the right *journal*, not the right *readiness*. The daily tracker is the right *clinical-gap warning*, not the right *journal*.

---

## What is actually in the repo (do not inflate)

### Ready as computational evidence
- IEC / Cosserat / postural-control theory and simulations in `manuscript/` and `scripts/`
- Cross-species `Bg` table: **12** vertebrates in `data/species_parameters.csv` (docs that say 18 are wrong)
- AlphaFold structural metrics on the in-repo gene panel
- Energy-deficit / PHV / sex-window **model overlays** against published epidemiology ages already cited in `scripts/validate_tau_clinical.py`
- **Open SpineWeb/AASCE landmark geometry** (Zenodo 4413665): 609 AP cases, 534 usable complete T1–L5. Derived Cobb-like envelope vs centerline metrics. This is public 2D geometry, not progression validation.

### Synthetic, not patient data
- Lonstein/BrAIST “N=1,000” comparison is a **synthetic demographic draw** calibrated to **published trial percentages**. Discussion already says this; Results/abstract now match that wording.
- `r = 0.983` is a **model-internal** growth-window correlation, not a fit to clinical Cobb measurements.

### Gaps (do not fill with invented numbers)
- `data/clinical_cohort_targets.csv` has **five** literature-digitized aggregate points, not a cohort
- No Risser/Sanders, no serial Cobb, no hospital extracts
- Prospective validation design is in Discussion §`sec:prospective` and still requires data-use agreements (BrAIST IPD / Harms Study Group)

---

## Compile and submit

```bash
python3 scripts/run_submission_validation.py
make -C manuscript          # requires pdflatex/latexmk
```

If LaTeX is not installed, upload `manuscript/` to Overleaf and compile `main.tex`. Cover letter: `manuscript/cover_letter_spine_deformity.tex`.

**Author-only portal step:** https://www.editorialmanager.com/spde/  
Do not treat this file as proof of submission.

Checklist that matches this status: `REMAINING_ITEMS.md`.
