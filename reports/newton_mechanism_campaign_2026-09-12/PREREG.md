# Corrected-material Newton mechanism campaign — frozen 2026-09-12

Purpose: challenge implementation and numerical validity without selecting a biological mechanism by synthetic agreement. This is the user-approved “Test the mechanism” campaign, capped at 48 active hours including the CPU comparator grid, failed runs and interrupted attempts. Waiting for the night window is not active runtime.

## Historical evidence

The completed 180-month result remains at `results/newton_ratchet_rod/ratchet_rod.json` (SHA256 `15bd31b5943b4119c3a1d3bc384fc949c50baaa9481e2e67da378a0ec4d450b8`). The prior amended 0.05–10-degree readout and exclusions are preserved. The corrected numerical readout is reproducible but its physical interpretation was withdrawn in AUDIT_LEDGER R-7(iv): the batch builder overwrote stretch/shear as well as bend/twist gains. No old result is silently replaced. The old runner is retained for provenance; new experiments use `scripts.experiments.newton.campaign`.

## Fixed experiment

Every run contains all 18 worlds: law off then law on, each with kr = 0.3, 1, 6 crossed with Bg = 0.2, 0.3, 0.5. Initial age 5 years; full horizon 180 months; initial and every monthly state saved. Law-off worlds have exactly zero permanent-curvature update. No parameter fitting or removal of high-bend worlds.

Diagnostic prefix, 12 months each, hz 60, 150 VBD iterations, 24 segments:

1. `diag_legacy`: historical blanket material gains and historical shake sampling.
2. `diag_material`: corrected material slots, historical shake sampling.
3. `diag_exact`: corrected material slots and exact shake endpoint.

Full-horizon jobs, all with corrected materials and exact waveform:

| ID | Steps/s | VBD iterations | Segments |
|---|---:|---:|---:|
| baseline | 60 | 150 | 24 |
| dt120 | 120 | 150 | 24 |
| iter300 | 60 | 300 | 24 |
| mesh48 | 60 | 150 | 48 |
| dt240 | 240 | 150 | 24 |
| iter600 | 60 | 600 | 24 |
| mesh96 | 60 | 150 | 96 |
| combined | 120 | 300 | 48 |

The first refined values are combined before acceptance. Jobs execute in this fixed order, subject to budget admission. A higher combined refinement or growth-update refinement requires a new, separately named protocol; no tuning follows observed ordering.

## Continuum and load conventions

Total length 0.5 m, radius 0.006 m, free mass 0.07500238442636259 kg, gravity 9.81 m/s², initial tilt 0.5 degrees. The fixed root segment remains 0.5/24 m at every mesh. The remaining length is divided into N−1 free bodies with uniform line mass. Root mass and inertia are zero. Builder capsule inertias are scaled with body mass; capsule discretization dependence is recorded and assessed by the mesh comparisons.

Joint spacing is the average of adjacent segment lengths. EI = Bg × free mass × g × length². Bending and twisting gains are EI/spacing. Stretch and shear gains preserve EA = 10⁷ × (0.5/24); gains are EA/spacing. Linear damping is zero; angular damping is stiffness × 1 second. Newton's typed rod material setter must report DOF layout (2 linear, 2 angular), and every final stiffness/damping array is saved.

Each model month: 8 seconds of 0.004 m, 0.25 Hz root translation followed by 10 seconds of settling. The exact waveform sets the root at sample endpoint (step+1)/hz, reaches exactly zero at 8 seconds and stays zero while settling. The historical waveform holds sin(2π×0.25×(8−dt)) through settling. Root orientation and other coordinates are clamped to their initial values at every step.

Growth envelope: (0.08 + exp(−0.5×((age−12)/1.6)²))/1.08, peak kg 1/year. At shake end, update signed permanent curvature by kg×(measured curvature−permanent curvature)×kg/(kr+kg)×1/12 year. Encode rest bend in parent-local y as 2 tan(permanent curvature × joint spacing / 2). All law-off updates remain zero. The imposed update is a model assumption, not measured biology.

## Recorded evidence and acceptance

Initial and monthly NPZ states save all body transforms and permanent curvature. JSON records signed joint curvature, length-integrated total absolute planar bend, length-integrated absolute permanent bend, joint-anchor axial/shear gap divided by spacing, quaternion norm error, out-of-plane tangent and root position. Shake-end diagnostics precede each growth update. Bend is not clinical Cobb angle.

At recorded states, nonfinite state is a failure; quaternion norm error > 0.001, out-of-plane tangent > 0.001, or axial/shear anchor strain > 0.01 makes that run mechanically invalid. The gate applies to initial, shake-end and monthly observations, not a claimed bound on every internal solver step. The two-step implementation smoke was finite but showed transient axial strain 0.0100418, above the unchanged 0.01 gate; it is labelled `validation_only` and is excluded from scientific comparisons. Initial axial strain was below 7.2e-7. This observation is recorded before the diagnostic/full campaign.

Compare baseline with dt120, iter300 and mesh48; compare dt120 with dt240, iter300 with iter600 and mesh48 with mesh96. Compare combined with baseline and each first refinement. Every world must have maximum trajectory error in both integrated bend measures ≤ max(0.1 degree, 5% of reference peak), and first sampled 10-degree crossing must agree within one model month (or be absent in both). Both runs must pass mechanical gates. All ten comparisons must pass before any law-on rate ordering is reported as numerically supported. Missing, partial or failed runs cannot pass. Numerical disagreement means unresolved simulation, not disproof of biology.

No new angle ceiling is used as a numerical-validity criterion. Historical 10-degree exclusions apply only to that historical reading. Complete convergence and ordering within this imposed law still cannot establish it as the biological mechanism.

## Reduced-model challenge grid

CPU-only, existing equations unchanged: signed scalar extension, two-state kh=0, two-state kh=0.2, stress-growth. Fixed load coefficients; kr 0.3/1/6 and growth multiplier 0.5/1/1.5; stress-growth instead crosses beta 0.92/1.71/2.39 with the same growth multipliers. Seven protocols: sustained positive load, zero load, negative load, unload at 14, reverse at 14, existing smooth growth cessation near 18, no growth. Total 252 cases. Zero-load, sign-mirror and no-growth permanent-set controls must pass at 1e-9. Report recovery times and post-unload structural change; no synthetic winner is selected. No patient data or calibration enters this stage.

## Runtime, reproducibility and stopping

One controller and one Newton worker at a time, guarded by campaign and repository GPU locks. No job is admitted with <6 GiB available RAM or alongside detected Newton/TimesFM work. Stop the owned worker if available RAM falls below 3 GiB. GPU exclusion is 23:00–01:00 IST; no services or existing model processes are stopped. No interaction with Flash-Next configuration or its soak.

A conservative per-month estimate admits a whole job only if it fits the remaining budget and daily window, with a 10-minute window margin. An estimate too large for any daily window produces `window_limited`; one too large for the remaining active budget produces `budget_limited`. A 90-second termination margin protects the 48-hour cap. On controller death, workers request SIGTERM; elapsed missing runtime is conservatively charged through recovery. Interrupted/failed trajectories remain separate attempts and are never accepted as completed evidence.

Protocol JSON, project source hashes and hashes of installed Newton/Warp sources and native libraries are sealed before work. Changed seals refuse continuation. The controller rebuilds REPORT.md and assessment.json from completed results and returns the manually assigned kanban card for review at termination. It never declares biological success.
