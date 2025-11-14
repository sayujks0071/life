"""Bridge between countercurvature fields and PyElastica Cosserat rods.

This module will host wrappers that assemble Cosserat rod simulations where the
rest curvature, stiffness, and active moments are shaped by biological
information fields.  The implementation will:

* Build rods with spatially varying reference curvature derived from
  :func:`~spinalmodes.countercurvature.coupling.compute_rest_curvature`.
* Inject gravity as the physical baseline forcing and overlay optional active
  information moments.
* Provide utilities to run ensembles of simulations for the countercurvature
  experiments (plant growth, spinal modes, microgravity adaptation, etc.).

The detailed PyElastica integration is staged for subsequent commits; this file
currently defines the scaffolding and documentation to guide that work.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CounterCurvatureRodSystem:  # pragma: no cover - placeholder
    """Placeholder for the PyElastica-aware rod system.

    The full implementation will provide constructors that ingest
    :class:`~spinalmodes.countercurvature.info_fields.InfoField1D` instances and
    :class:`~spinalmodes.countercurvature.coupling.CounterCurvatureParams`
    objects, translating them into PyElastica state.  Simulation runners will
    expose ``run_simulation`` returning time histories for post-processing into
    countercurvature metrics.
    """

    description: Optional[str] = None

    def build(self) -> None:
        """Placeholder hook for the forthcoming PyElastica construction layer."""

        raise NotImplementedError("PyElastica integration pending implementation")
