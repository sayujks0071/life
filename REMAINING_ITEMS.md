# Remaining items for Spine Deformity

Live manuscript: `manuscript/main.tex`
Live journal: Spine Deformity (Springer). Backup: Spine (LWW).
Portal: https://www.editorialmanager.com/sdef/ (not `/spde/`).
No journal-imposed deadline as of 22 Aug 2026. See `JOURNAL_TRACK.md`.

Mark items done only when the artifact exists in this repo.

## Submission-ready now (computational article)

- [x] Theory + methods + results as a computational/hypothesis-generating paper
- [x] Cover letter aligned to `main.tex` title (not the old “spacetime” title in the May pack)
- [x] Bibliography in `manuscript/references.bib`
- [x] Figure files referenced by `manuscript/sections/figures.tex` (checked by `scripts/check_manuscript_figures.py`)
- [x] Ethics / funding / competing-interest statements for a computational study
- [x] Open SpineWeb/AASCE geometry check (609 cases; 534 usable)
- [x] Literature Cobb anchors CSV wired (`data/clinical_cohort_targets.csv`, n=5 aggregate points)
- [x] PHV / sex-window overlays wired to `data/literature_epidemiology_anchors.csv` (Cheng 2015 windows already cited in-repo)
- [x] Status docs no longer claim 100% ready or a completed submission

## Blocking a *clinical* original article (leave as gaps)

- [ ] Patient-level Cobb series with age, sex, and curve type (not invented; not in this repo)
- [ ] Risser or Sanders staging linked to those curves
- [ ] Serial Cobb / progression labels (12-month or similar)
- [ ] Uncalibrated test of `Bg_eff` on held-out patient records (BrAIST IPD or equivalent DUA)
- [ ] Independent clinician Cobb vs landmark-derived envelope on SpineWeb (pixels + rater)
- [ ] Zenodo DOI minted and pasted into `manuscript/sections/availability.tex`
- [ ] Editorial Manager manuscript ID recorded here after actual submission

## Compile / packaging holes that are now operational

- [x] `make -C manuscript` fails loudly if LaTeX is missing instead of implying a PDF exists
- [x] `final_verification.sh` checks `manuscript/figures/` (not the empty `figures/main/`)
- [x] SpineWeb zips unpack on demand; extracted XML dirs are gitignored
- [x] `results/open_data/` is tracked (was gitignored under `results/`)

## How to compile / submit

```bash
python3 scripts/run_submission_validation.py
make -C manuscript
```

Upload `manuscript/main.pdf` (or Overleaf PDF), `manuscript/cover_letter_spine_deformity.tex` compiled PDF, and individual figures to https://www.editorialmanager.com/sdef/ (not `/spde/`).

Optional: select the journal’s AI / machine-learning collection (Springer Status: Open / deadline Ongoing as of 22 Aug 2026). If selected, omit guest editor Carl-Éric Aubin from suggested reviewers.

If *Spine Deformity* desks the paper for insufficient clinical data, retarget *Spine* or *European Spine Journal* with the same computational framing; do not invent a cohort to keep the original journal.
