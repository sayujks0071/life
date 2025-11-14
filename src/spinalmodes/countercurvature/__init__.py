"""Countercurvature modelling layer for spinalmodes.

This subpackage introduces analog models of *biological countercurvature of spacetime*
using Cosserat rod mechanics (PyElastica) coupled to information fields defined along a
rod-like living structure (e.g. spine, plant stem, neural tract).

The modules provide:
- Data containers for information fields on arc-length grids (:mod:`info_fields`).
- Coupling rules that map information content into mechanical parameters and active
  efforts (:mod:`coupling`).
- Bridge code that constructs PyElastica systems equipped with the countercurvature
  couplings (:mod:`pyelastica_bridge`).
- Validation metrics that interpret the information-driven corrections as effective
  metric deviations (:mod:`validation_and_metrics`).

All components support the working hypothesis that biological information processing can
be represented as countercurvature correcting how a body experiences a gravitational
field.
"""

from .info_fields import InfoField1D, InfoFieldTimeSeries, make_uniform_grid
from .coupling import (
    CounterCurvatureParams,
    compute_active_moments,
    compute_effective_stiffness,
    compute_rest_curvature,
)

__all__ = [
    "InfoField1D",
    "InfoFieldTimeSeries",
    "make_uniform_grid",
    "CounterCurvatureParams",
    "compute_active_moments",
    "compute_effective_stiffness",
    "compute_rest_curvature",
]
