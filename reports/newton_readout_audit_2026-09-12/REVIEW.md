# Newton rod reporting continuation — 2026-09-12

Reviewed the Claude session b9063ed6-27ac-4701-896a-b3f1259a76f1, live spine-research board,
~/life at 3188f854, the existing code, and saved smoke data. This continues the measurement
review; it does not rerun the physics or change a scientific hypothesis to make a gate pass.

## Current project state

The submission snapshot is v1.7-consistency at 3188f854, following the final wording changes.
The publication checklist has the current PDF, bundle, and cover_letter.txt paths. Its tag
supersedes the earlier c535860e mentioned in a stale Claude memory note. Manuscript consistency,
DOI resolution, and comparative reduced-model work were already completed by Claude today.
The journal submission and BrAIST data agreement remain human actions on the board.

Newton PID 994575 started at 13:12:19 IST and was still running during this review. The raw
ratchet_rod.json/md at initial inspection were still dated September 3, not the rerun.
The running interpreter has already imported its code. Changes below affect future runs;
use the independent CPU reader to correct the eventual output of the current process.

## Confirmed defects and fixes

1. **48-fold reporting inflation.** Joint curvature is dtheta/ds in rad/m. The observation
   was degrees(sum(abs(curvature))) without ds = 0.5/24 m. Correct total absolute bend is
   degrees(sum(abs(curvature))*ds). A known 20-degree arc reported 960 degrees. The fix is
   independent of mesh in tests on 12, 24 and 48 segments.
2. **Mismatched/clipped control drift.** The prior summary subtracted the law-on experiment's
   first value from the law-off control's last value and clipped negative changes to zero.
   It now uses abs(control_last-control_first) for each matched world. A2 compares this
   angular drift against permanent bend: degrees(mean(abs(kp))*(N-1)*ds).
3. **Observation clock.** The sample is taken after a month but labelled at its start.
   Correct the age by +1/12 year. The recorded window is 5.083333 to 20 years in a full run;
   there is no measured pre-first-month age-5 baseline. The reader distinguishes recorded-
   window A2 from the preregistered full-window check, which cannot be certified from these
   observations alone.
4. **Observable identity.** Total absolute planar rod bend is not clinical Cobb. Opposite
   bends add in this observable; clinical endplate selection is absent. The legacy JSON key
   `cobb` remains for compatibility, with explicit quantity/units metadata for future runs.
5. **Dependent scalar amplitude.** The original ODE amplitude inherited the same factor 48.
   The reader rescales it and the derived rod/ODE ratio. It preserves the original aggregate
   full-L definition rather than changing calibration across Bg or measured joint span.

The new schema marks corrected angles and observation times, preventing double correction.
Old results without both out-of-plane observation arrays are refused. The reader writes
separate SHA256-linked readout.json and READOUT.md files; it never changes the raw input.

## Real smoke check — sanity only

Source SHA256: 12b741f6af66662cd6e06052b4a1c516e502c15bff70699a23f6b0c96838dc13.
See smoke_READOUT.md and smoke_readout.json for all nine worlds. Corrected total bend spans
0.220823 to 1.17102 degrees, not the previously reported 10.6 to 56.2 degrees. Absolute
control drift is 0.364952, 0.0236734, and 0.000470831 degrees at Bg 0.2, 0.3, and 0.5.
The former 17.5-degree drift cited as evidence of large continuing sag was also inflated.
These are the already completed 12-month smoke observations, not a new mechanical run.

The preregistration says O(1–40 degrees); its board card states 1–40 degrees. The reader
retains the board's literal interval and reports the ambiguity rather than silently lowering
the bound. All nine smoke series include values below 1 degree. No Gate C or ratio is read
from the smoke. A changed future sanity bound needs a declared new protocol; a failure of
the old range is not a biological null. The preregistration and raw smoke are preserved.

## Validation and scope

19 focused CPU tests pass: existing frame/curvature tests, mesh-independent analytic arcs,
control drift, schema conversion, smoke gate suppression, stale-output rejection, baseline
limitation, planarity, fixed angle bounds, and malformed-result checks. The original September
3 output is refused with exit 2; the real smoke returns SMOKE_ONLY_NO_GATES.

AST comparisons confirm that growth_velocity, bg_to_k_bend, build_column, column_mass,
batched_model, gate_a1, scalar_ode_final and the ratchet update block are unchanged. No
manuscript sources, source data, preregistration, submitted/tagged artifacts, live services,
or the unrelated untracked src/spine_growth_analysis.py are edited by this patch.
No GPU simulation, Flash-Next benchmark, restart, new worker, submission, or push was run.

## Full-run handoff — t_40524ff0 stays open

When run.log has an exit=0 completion and the JSON has been replaced by the new full output,
run from ~/life:

```bash
.venv/bin/python scripts/experiments/newton/ratchet_rod_readout.py results/newton_ratchet_rod/ratchet_rod.json --out-dir reports/newton_readout_audit_2026-09-12/full
```

The reader automatically corrects the running process's old reporting schema and accepts
future schema-2 outputs without rescaling. Report per-Bg sanity, recorded-window A2, and
conditional ordering together; do not promote a descriptive ordering into evidence when
its prerequisite fails. Keep the age-5 baseline limitation explicit. Append the factual
reading with its source hash; do not overwrite the raw run or change preregistered bounds.
This research result is not cited by the submission manuscript and does not reopen its tag.

Other existing ready cards: AlphaFold parser/provenance follow-ups t_010625f1; DOI-check
scheduling decision t_ff862b49; journal upload t_810e86a2; BrAIST DUA t_3df16fb4.
