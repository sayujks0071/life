"""Countercurvature analog models coupling information and Cosserat rod mechanics.

This subpackage implements the modelling layer for the working hypothesis
"consciousness as biological countercurvature of spacetime".  It provides:

* :mod:`info_fields` – data structures for one-dimensional information fields along
  a rod/spine, with utilities to generate ∂I/∂s profiles on a discretised arclength
  grid.
* :mod:`coupling` – mappings from information fields to mechanical targets
  (rest-curvature, stiffness, active moments) that embody biological
  countercurvature corrections.
* :mod:`pyelastica_bridge` – wrappers that inject these targets into PyElastica
  Cosserat rod simulations.

All modules emphasise dimensional clarity and document the interpretation of the
couplings as information-driven modifications to the effective curvature metric of
living structures in a gravitational field.
"""

from .info_fields import InfoField1D, InfoFieldFactory
from .coupling import (
    CounterCurvatureParams,
    compute_active_moments,
    compute_effective_stiffness,
    compute_rest_curvature,
)

__all__ = [
    "InfoField1D",
    "InfoFieldFactory",
    "CounterCurvatureParams",
    "compute_rest_curvature",
    "compute_effective_stiffness",
    "compute_active_moments",
]
