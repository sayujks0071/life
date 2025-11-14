"""Countercurvature mechanisms opposing gravitational bending."""

from __future__ import annotations

from typing import Tuple

from numpy.typing import NDArray

from .core import IECParameters


def compute_gravitational_load(params: IECParameters) -> float:
    """Compute distributed gravitational load (N/m)."""
    return params.rho * params.A_cross * params.g_magnitude


def compute_gravitational_moment_profile(
    s: NDArray[np.float64], params: IECParameters
) -> NDArray[np.float64]:
    """Cantilever bending moment induced by uniform gravitational load."""
    q = compute_gravitational_load(params)
    L = params.length
    x = s
    return q * (L * x - 0.5 * x**2)


def compute_gravitational_curvature_profile(
    s: NDArray[np.float64], params: IECParameters
) -> NDArray[np.float64]:
    """Curvature profile induced by gravitational bending."""
    EI = params.E0 * params.I_moment
    if EI <= 0:
        raise ValueError("Product E0 * I_moment must be positive for curvature calculation")
    moments = compute_gravitational_moment_profile(s, params)
    return moments / EI


def apply_countercurvature(
    s: NDArray[np.float64],
    params: IECParameters,
    kappa_target: NDArray[np.float64],
    M_active: NDArray[np.float64],
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Oppose gravitational bending by modulating curvature and active moments."""
    if params.countercurvature_gain == 0.0:
        return kappa_target, M_active

    if params.countercurvature_orientation == "against_gravity":
        sign = -1.0
    elif params.countercurvature_orientation == "with_gravity":
        sign = 1.0
    else:
        raise ValueError(
            "countercurvature_orientation must be 'against_gravity' or 'with_gravity'"
        )

    kappa_gravity = compute_gravitational_curvature_profile(s, params)
    M_gravity = compute_gravitational_moment_profile(s, params)

    kappa_adjusted = kappa_target + sign * params.countercurvature_gain * kappa_gravity
    M_adjusted = M_active + sign * params.countercurvature_gain * M_gravity

    return kappa_adjusted, M_adjusted


__all__ = [
    "compute_gravitational_load",
    "compute_gravitational_moment_profile",
    "compute_gravitational_curvature_profile",
    "apply_countercurvature",
]
