# Independent confirmation of the full Newton run



Raw SHA256: `15bd31b5943b4119c3a1d3bc384fc949c50baaa9481e2e67da378a0ec4d450b8`. Independently recomputed 66 numeric/gate fields; all match Claude's saved readout.

The run completed at 16:09 IST, exit=0. It used 180 model months and has 31 observations.

The author-approved amendment at 15:05 IST precedes the output. This confirmation uses its 0.05–10 degree range; the original range is not substituted.



| Bg | kr | final total bend (deg) | permanent bend (deg) | rod/ODE | amended angle sanity |
|---|---|---|---|---|---|
| 0.5 | 0.3 | 1.813 | 1.185 | 0.681 | True |
| 0.5 | 1.0 | 0.954 | 0.545 | 0.538 | True |
| 0.5 | 6.0 | 0.373 | 0.112 | 0.427 | True |
| 0.3 | 0.3 | 9.331 | 5.152 | 2.962 | True |
| 0.3 | 1.0 | 3.479 | 1.737 | 1.715 | True |
| 0.3 | 6.0 | 0.945 | 0.270 | 1.026 | True |
| 0.2 | 0.3 | 86.510 | 45.759 | 26.307 | False |
| 0.2 | 1.0 | 27.892 | 10.502 | 10.367 | False |
| 0.2 | 6.0 | 3.339 | 0.817 | 3.106 | True |



## Interpretation



At Bg 0.3 and 0.5, sanity and recorded-window A2 pass and permanent set decreases with increasing restoration rate. This establishes the expected ordering within this imposed rod law and protocol. It is not clinical validation or evidence distinguishing the ratchet from all competing growth laws.

At Bg 0.2, kr 0.3 and 1.0 reach 86.510 and 27.892 degrees, exceeding the adopted 10-degree ceiling. That group remains excluded from Gate C; descriptive ordering there is not promoted to a pass. The whole-run status remains PREREQUISITE_FAILURE_NO_MECHANISTIC_VERDICT.

The first sampled exceedances are bracketed by ages 11.583–12.083 and 12.083–12.583 years, respectively. These are sampling intervals, not precise crossing times. By ages 17.583–20, the largest trajectory rises slowly from 84.728 to 86.510 degrees. These finite data do not establish mathematical divergence.

A stable law-off control and zero out-of-plane tangent narrow the explanation but do not prove the high-bend law-on solution is numerically converged. The existing description of runaway cementing should be read as a mechanistic hypothesis until timestep, solver-iteration, and mesh checks are available. Large deformation alone cannot classify a solution as either solver failure or physical instability.

The rod/ODE ratio uses a pooled full-rod-length calibration; Bg-matched calibration has not been applied. The quantity measured is total absolute planar rod bend, not clinical Cobb. A2 uses the recorded 5.083–20-year window; no pretreatment age-5 sample exists.



## Next numerical check (proposed, not an adopted preregistration)



1. Preserve this run and its amendment. Use a separate output directory and freeze the follow-up protocol before generating new results.

2. Start with the informative Bg 0.2/kr 0.3 condition and a Bg 0.3/kr 0.3 reference, each with matched law-off controls. Retain all original nine conditions for any subsequent confirmatory ordering claim.

3. Check mechanical timestep, VBD iterations, and segment count separately. Preserve forcing frequency, amplitude, total physical shake/settling duration, mass, length, and EI when refining. Changing only DT while leaving step counts fixed would change the experiment. Calibrate mesh-dependent statics rather than treating the discrete buckling threshold as fixed.

4. Check the monthly remodeling update separately while preserving the forcing exposure per modeled year. Save an age-5 state, per-joint signed curvature and permanent set, quaternions, and stretch/constraint diagnostics so high-bend solutions can be inspected directly.

5. Predeclare numerical-agreement criteria before those runs. Evaluate finite-trajectory agreement and threshold-crossing intervals; do not infer divergence from a terminal magnitude or simply raise the existing angle ceiling. Only after this should load-dependent amplification become a separate mechanistic hypothesis test.



No new simulation, service change, manuscript edit, tag change, or hypothesis amendment was performed for this confirmation.
