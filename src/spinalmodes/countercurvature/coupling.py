"""Map information fields into mechanical countercurvature targets.

The functions in this module implement the IEC-inspired couplings that translate
information gradients into shifts of the mechanical rest-curvature, stiffness,
and active moments experienced by a Cosserat rod.  These mappings provide the
operational meaning of *biological countercurvature*: structured information
flows reshape the effective curvature metric felt by the body in a gravitational
field.
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np
from numpy.typing import ArrayLike

from .info_fields import InfoField1D


class CounterCurvatureParams(NamedTuple):
    """Parameter bundle controlling information-to-mechanics couplings.

    Parameters
    ----------
    chi_kappa:
        Coupling from the information gradient to the rest-curvature bias.  Units
        are metres because ``∂I/∂s`` carries ``1/m`` when ``I`` is
        dimensionless, yielding curvature in ``1/m``.
    chi_E:
        Dimensionless coefficient scaling how the information density stiffens or
        softens the rod.
    chi_M:
        Coupling from ``∂I/∂s`` to an active bending moment density (``N·m``).
    scale_length:
        Characteristic arclength used to non-dimensionalise gradients when
        desired.  Default is ``1`` (no scaling).
    """

    chi_kappa: float = 0.0
    chi_E: float = 0.0
    chi_M: float = 0.0
    scale_length: float = 1.0


def _validate_shapes(info: InfoField1D, array: ArrayLike, name: str) -> np.ndarray:
    """Ensure ``array`` broadcasts to the shape of ``info``'s grid."""

    arr = np.asarray(array, dtype=float)
    if arr.shape not in {(info.s.size,), ()}:
        raise ValueError(f"{name} must be scalar or match info grid length {info.s.size}.")
    return arr


def compute_rest_curvature(
    info: InfoField1D,
    params: CounterCurvatureParams,
    kappa_gen: ArrayLike,
) -> np.ndarray:
    r"""Return the information-biased rest curvature :math:`\bar{\kappa}(s)`.

    The baseline generator ``kappa_gen`` encodes the geometric template (e.g. a
    passive gravitational mode).  Biological countercurvature adds the term
    ``χ_κ Lₛ ∂I/∂s`` which can oppose gravity-driven sag.  ``Lₛ`` is the optional
    ``scale_length`` parameter that renders the correction dimensionally
    consistent when ``∂I/∂s`` is computed on a non-dimensional grid.
    """

    baseline = _validate_shapes(info, kappa_gen, "kappa_gen")
    gradient = info.dIds * params.scale_length
    kappa_rest = baseline + params.chi_kappa * gradient
    return np.asarray(kappa_rest, dtype=float)


def compute_effective_stiffness(
    info: InfoField1D,
    params: CounterCurvatureParams,
    E0: ArrayLike,
    *,
    model: str = "linear",
) -> np.ndarray:
    """Compute an information-modulated bending stiffness field ``E_eff``.

    Parameters
    ----------
    info:
        Information field providing ``I(s)``.
    params:
        Coupling coefficients.
    E0:
        Baseline Young's modulus or bending stiffness (scalar or array).
    model:
        Functional form of the modulation.  ``"linear"`` applies
        ``E_eff = E0 * (1 + χ_E I)``.  ``"exponential"`` yields
        ``E_eff = E0 * exp(χ_E I)`` for strictly positive stiffness.
    """

    baseline = _validate_shapes(info, E0, "E0")
    if model == "linear":
        eff = baseline * (1.0 + params.chi_E * info.I)
    elif model == "exponential":
        eff = baseline * np.exp(params.chi_E * info.I)
    else:
        raise ValueError(f"Unknown stiffness model: {model}")
    return np.asarray(eff, dtype=float)


def compute_active_moments(info: InfoField1D, params: CounterCurvatureParams) -> np.ndarray:
    """Return an active bending moment density driven by information gradients.

    The term ``χ_M Lₛ ∂I/∂s`` is interpreted as the biological effort exerted to
    maintain posture or upward growth against gravity.  The resulting moment
    density has units of ``N·m`` when ``χ_M`` carries ``N·m`` and ``I`` is
    dimensionless.
    """

    gradient = info.dIds * params.scale_length
    M_info = params.chi_M * gradient
    return np.asarray(M_info, dtype=float)
