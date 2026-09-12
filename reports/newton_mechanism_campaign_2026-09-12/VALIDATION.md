# Implementation validation

Recorded 2026-09-12T12:31:09.886087+00:00.

- Installed campaign plus existing rod/readout, recovery-comparator and two-state regressions: **63 passed in 2.74 seconds**. No dependencies installed or upgraded.
- Test targets: `tests/test_newton_campaign.py`, `tests/test_newton_rod_measure.py`, `tests/test_ratchet_rod_readout.py`, `tests/test_recovery_comparators.py`, `tests/test_recovery_two_state.py`.
- Tests ran with the Newton Python environment and existing pytest package from the project environment; third-party pytest auto-loading was disabled. All 24 campaign tests ran, including real builder invariants at three meshes; none skipped.
- Two-step CUDA smoke: exit 0, `validation_only`, finite states, initial geometry axial strain <7.2e-7, transient axial strain 0.0100418. The unchanged 1% mechanical gate fails at that transient sample. Raw smoke artifacts are in `solver_validation/`; no scientific completion is inferred from this smoke.
- Installed controller dry-run: successful; created no campaign output. Protocol SHA256: `0bcc0f3d27b86dd18aaa3e19b6e3dde87718ea6fd612c11e7aa426fa6f99fcb6`. The live ledger separately seals installed Newton/Warp and existing reduced-model sources.
- Post-launch CPU challenge: **252 cases completed**; all zero-load, mirror and no-growth controls passed. This checks equation consequences and does not identify a biological mechanism.
- Controller PID at launch: 1243828. Kanban: `spine-research/t_c0635f19`. GPU diagnostic and refinement outcomes are ongoing in `results/newton_mechanism_campaign_2026-09-12/REPORT.md`; this validation note is not a convergence verdict.
- Historical raw JSON SHA256 remains `15bd31b5943b4119c3a1d3bc384fc949c50baaa9481e2e67da378a0ec4d450b8`.

The historical hash is also checked independently against the source in the implementation handoff; manuscript tag remains `v1.7-consistency` at `3188f854e1504daf0bf2f80d7eadfde9c560e330`. Existing `src/spine_growth_analysis.py` remains outside this change.
