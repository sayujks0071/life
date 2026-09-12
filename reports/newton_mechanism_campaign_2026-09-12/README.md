# Newton mechanism campaign implementation

Authoritative runner: `scripts/experiments/newton/campaign/`. Frozen specification: [PREREG.md](PREREG.md) and [protocol.json](protocol.json). Live results: `../../results/newton_mechanism_campaign_2026-09-12/REPORT.md` and `campaign.json`.

Run from `/home/sayuj/life` with the installed environments; no dependency changes are required:

```sh
/home/sayuj/newton/.venv/bin/python -m scripts.experiments.newton.campaign.controller --protocol reports/newton_mechanism_campaign_2026-09-12/protocol.json --out-dir results/newton_mechanism_campaign_2026-09-12 --max-active-hours 48 --dry-run
```

Omit `--dry-run` to execute the sealed sequence. Add `--kanban-task TASK_ID` only for the manually assigned campaign card. `--once` admits at most one GPU job and returns immediately when admission must wait. The CPU comparator stage uses the existing project `.venv`; the controller and solver use the installed Newton `.venv`.

A file named `STOP` in the result directory requests a stop of the owned worker. Preserve incomplete attempts and review before restarting. Source/protocol changes require a new campaign directory. Completed runs are skipped on a matching restart; partial runs do not enter the assessment. `campaign.json` identifies controller/worker PIDs, active hours and wait reason; worker `progress.json` records months completed.

Validation includes real Newton builder checks at all three meshes, exact load sampling, fixed clamp and free mass, control pairing, units/anchor diagnostics, unchanged matrix, full evidence gating, source-change refusal and interrupted-budget accounting. Existing rod/readout and reduced-model regressions are also run. The 2-step CUDA smoke is implementation evidence only; its transient strain gate failure is recorded in PREREG.md and not reclassified.

No existing runner, historical result, manuscript, release tag, GPU service configuration or unrelated work is modified by this implementation.
