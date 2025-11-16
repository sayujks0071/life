# Final Submission Checklist

## 🚀 You're 98% There - Final Steps

This checklist covers the last steps before submission to PRX Life.

---

## ✅ Already Complete

- [x] Code implementation (PyElastica, tests, metrics)
- [x] Reproducible experiments (with CLI arguments)
- [x] Documentation (API reference, guides, checklists)
- [x] PRX Life cover letter (ready to use)
- [x] Key claims bullets (ready to update with numbers)
- [x] Manuscript structure (LaTeX with Code/Data Availability)
- [x] Sine-wave narrative text (added to Results/Discussion)
- [x] Version tagged (v0.1.0 on GitHub)
- [x] All changes pushed to GitHub

---

## ⏳ Final Steps (Before Submission)

### 1. Run Full Parameter Sweeps

**Command:**
```bash
bash RUN_FULL_SWEEPS.sh
```

**Or run individually:**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

python3 -m spinalmodes.experiments.countercurvature.experiment_spine_modes_vs_gravity
python3 -m spinalmodes.experiments.countercurvature.experiment_microgravity_adaptation
python3 -m spinalmodes.experiments.countercurvature.experiment_phase_diagram
python3 -m spinalmodes.experiments.countercurvature.generate_countercurvature_figure
```

**Expected runtime:** 40-70 minutes total

**Outputs to verify:**
- [ ] `outputs/experiments/spine_modes/spine_modes_results.csv`
- [ ] `outputs/experiments/spine_modes/spine_modes_summary.csv`
- [ ] `outputs/experiments/microgravity/microgravity_summary.csv`
- [ ] `outputs/experiments/phase_diagram/phase_diagram_data.csv`
- [ ] `outputs/figs/fig_countercurvature_metrics.png`

---

### 2. Extract Anchor Numbers

**Command:**
```bash
python3 scripts/extract_anchor_numbers.py
```

**What to extract:**
- [ ] Microgravity: Energy collapse %, D_geo persistence ratio
- [ ] Phase diagram: Three regime anchor points (χ_κ, g, D̂_geo, S_lat, Cobb)
- [ ] Spine S-curve: Sign changes, max/RMS ratio, D̂_geo

**Output:** Script prints formatted sentences ready to paste into manuscript

---

### 3. Update Manuscript with Numbers

**Files to update:**
- [ ] `manuscript/main_countercurvature.tex`:
  - [ ] Results Section 3.1: Add D̂_geo, max/RMS ratio, sign change count
  - [ ] Results Section 3.2: Add energy collapse %, D_geo persistence %
  - [ ] Results Section 3.3: Add three regime anchor points
  - [ ] Replace `<your GitHub URL>` with actual URL

**See:** `docs/manuscript_sine_wave_text.md` for TODO locations

---

### 4. Update Cover Letter & Key Claims

**Files to update:**
- [ ] `docs/cover_letter_expansion_template.md`: Replace `<your GitHub URL>`
- [ ] `docs/key_claims_bullets.md`: Update placeholder numbers with real values

**Cover letter placeholders:**
- [ ] Replace `<your GitHub URL>` → `https://github.com/sayujks0071/life`
- [ ] Replace `<Your affiliation>` → Your institution
- [ ] Replace `<Email>` → Your email

---

### 5. Final Manuscript Checks

- [ ] LaTeX compiles: `pdflatex main_countercurvature.tex` (no errors)
- [ ] Bibliography compiles: `bibtex main_countercurvature`
- [ ] All figure paths exist and are correct
- [ ] All citations have entries in `refs.bib`
- [ ] No TODO comments remain in final manuscript
- [ ] All placeholder numbers replaced with actual values

---

### 6. Generate Final PDF

```bash
cd manuscript
pdflatex main_countercurvature.tex
bibtex main_countercurvature
pdflatex main_countercurvature.tex
pdflatex main_countercurvature.tex
```

**Verify:**
- [ ] PDF has all figures
- [ ] Page numbers are correct
- [ ] References are complete
- [ ] No compilation errors or warnings

---

## Submission Package

### What to Submit to PRX Life

1. **Manuscript PDF** (`main_countercurvature.pdf`)
2. **Cover Letter** (from `docs/cover_letter_expansion_template.md`)
3. **Figures** (high-resolution PDFs or PNGs):
   - `outputs/figs/fig_countercurvature_metrics.png` (4-panel figure)
   - `outputs/experiments/phase_diagram/phase_diagram.png` (phase diagram)
4. **Supplementary Materials** (if any)

### PRX Life Submission Form

**Key Claims** (use from `docs/key_claims_bullets.md`, Version 1):
- Copy the 3-4 bullet points
- Update with actual numbers from full sweeps

---

## Timeline

| Task | Time |
|------|------|
| Run full sweeps | 40-70 min |
| Extract numbers | 5 min |
| Update manuscript | 30-60 min |
| Final checks | 15 min |
| Generate PDF | 5 min |

**Total**: ~2-3 hours of focused work

---

## Quick Reference

- **Full sweeps script**: `RUN_FULL_SWEEPS.sh`
- **Extraction script**: `scripts/extract_anchor_numbers.py`
- **Cover letter**: `docs/cover_letter_expansion_template.md` (PRX Life version at top)
- **Key claims**: `docs/key_claims_bullets.md`
- **Manuscript TODOs**: `docs/manuscript_sine_wave_text.md`
- **Extraction guide**: `docs/full_sweeps_extraction_guide.md`

---

## Status

✅ **Code**: Complete and pushed  
✅ **Cover letter**: Ready (just fill in placeholders)  
✅ **Manuscript structure**: Complete with sine-wave narrative  
⏳ **Full sweeps**: Run to get actual numbers  
⏳ **Number extraction**: Update manuscript with real values  
⏳ **Final polish**: Replace placeholders, verify PDF

**You're literally one full-sweep run away from submission!** 🚀

