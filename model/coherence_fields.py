"""
Coherence field generators I(s) for developmental information.

Implements prototypical spatial patterns representing:
- HOX/PAX expression gradients
- Morphogen gradients (RA, FGF, Wnt)
- Ciliary flow fields
- Segmentation clock coherence

All fields are dimensionless and normalized.
"""

import numpy as np
from numpy.typing import NDArray
from typing import Literal, Tuple

from .core import IECParameters


def generate_coherence_field(
    s: NDArray[np.float64], params: IECParameters
) -> NDArray[np.float64]:
    """
    Generate information/coherence field I(s).

    Args:
        s: Spatial coordinates (m), shape (n_nodes,)
        params: IEC parameters specifying field mode and parameters

    Returns:
        Coherence field I(s), dimensionless, shape (n_nodes,)

    Raises:
        ValueError: If I_mode is not recognized

    Examples:
        >>> params = IECParameters(I_mode="linear", I_gradient=0.5)
        >>> s = params.get_s_array()
        >>> I_field = generate_coherence_field(s, params)
        >>> assert I_field[0] == pytest.approx(1.0)
        >>> assert I_field[-1] > I_field[0]
    """
    if len(s) == 0:
        return np.array([])

    s_norm = s / params.length

    if params.I_mode == "constant":
        return _constant_field(s, params)

    elif params.I_mode == "linear":
        return _linear_gradient_field(s_norm, params)

    elif params.I_mode == "gaussian":
        return _gaussian_bump_field(s_norm, params)

    elif params.I_mode == "step":
        return _step_function_field(s_norm, params)

    else:
        raise ValueError(f"Unknown I_mode: {params.I_mode}")


def _constant_field(s: NDArray[np.float64], params: IECParameters) -> NDArray[np.float64]:
    """
    Constant uniform field.

    I(s) = I_amplitude

    Use case: Uniform expression domain (e.g., thoracic HOX)
    """
    return np.ones_like(s) * params.I_amplitude


def _linear_gradient_field(
    s_norm: NDArray[np.float64], params: IECParameters
) -> NDArray[np.float64]:
    """
    Linear rostro-caudal gradient.

    I(s) = I_amplitude * (1 + I_gradient * s_normalized)

    Use case: RA gradient in presomitic mesoderm
    Biological reference: Dubrulle et al. 2001 (Cell)
    """
    return params.I_amplitude * (1.0 + params.I_gradient * s_norm)


def _gaussian_bump_field(
    s_norm: NDArray[np.float64], params: IECParameters
) -> NDArray[np.float64]:
    """
    Gaussian localized signaling center.

    I(s) = I_amplitude * exp[-(s - s_center)^2 / (2 * width^2)]

    Use case: FGF8 signaling from tail bud
    Biological reference: Delfini et al. 2005 (Dev Cell)
    """
    return params.I_amplitude * np.exp(
        -((s_norm - params.I_center) ** 2) / (2 * params.I_width**2)
    )


def _step_function_field(
    s_norm: NDArray[np.float64], params: IECParameters
) -> NDArray[np.float64]:
    """
    Sharp domain boundary (Heaviside step).

    I(s) = 0 if s < s_center, I_amplitude if s >= s_center

    Use case: HOX domain boundaries (e.g., cervical-thoracic transition)
    Biological reference: Wellik 2007 (Dev Dyn)
    """
    I_field = np.zeros_like(s_norm)
    I_field[s_norm >= params.I_center] = params.I_amplitude
    return I_field


def compute_gradient(
    field: NDArray[np.float64], s: NDArray[np.float64]
) -> NDArray[np.float64]:
    """
    Compute spatial gradient of a field using finite differences.

    Args:
        field: Field values at spatial points, shape (n,)
        s: Spatial coordinates (m), shape (n,)

    Returns:
        Gradient ∂field/∂s, shape (n,)

    Note:
        Uses numpy.gradient with second-order accurate central differences
        (except at boundaries where forward/backward differences are used).
    """
    return np.gradient(field, s)


def compute_gradient_norm(
    field: NDArray[np.float64], s: NDArray[np.float64]
) -> float:
    """
    Compute L2 norm of spatial gradient (magnitude measure).

    Args:
        field: Field values
        s: Spatial coordinates

    Returns:
        ||∇I|| = sqrt(∫ (∂I/∂s)^2 ds) / L
    """
    grad = compute_gradient(field, s)
    return float(np.sqrt(np.trapz(grad**2, s)) / (s[-1] - s[0]))


def compute_gravity_information_field(
    s: NDArray[np.float64], params: IECParameters
) -> NDArray[np.float64]:
    """
    Compute gravity-dependent information field component.

    I_gravity(s) = χ_g · σ_effective(s)
    where σ_effective(s) = (ρ_tissue - ρ_CSF) · g · (L - s)

    This represents mechanotransduction: gravitational stress → gene expression.

    Args:
        s: Spatial coordinates (m), shape (n_nodes,)
        params: IEC parameters with gravity coupling

    Returns:
        Gravity-dependent information field I_gravity(s), dimensionless
    """
    if not params.include_gravity or params.chi_g == 0.0:
        return np.zeros_like(s)

    L = params.length
    rho_effective = params.rho_tissue - params.rho_CSF
    sigma_effective = rho_effective * params.g * (L - s)
    
    # Normalize to dimensionless (scale by typical stress)
    sigma_normalized = sigma_effective / (rho_effective * params.g * L)
    
    return params.chi_g * sigma_normalized


def compute_buoyancy_information_field(
    s: NDArray[np.float64], params: IECParameters
) -> NDArray[np.float64]:
    """
    Compute CSF buoyancy-dependent information field component.

    I_buoyancy(s) = -χ_b · ρ_CSF · g · (L - s) / (ρ_tissue · g · L)

    This represents the counteracting effect of CSF buoyancy on gravitational stress.

    Args:
        s: Spatial coordinates (m), shape (n_nodes,)
        params: IEC parameters with buoyancy coupling

    Returns:
        Buoyancy-dependent information field I_buoyancy(s), dimensionless
    """
    if not params.include_buoyancy or params.chi_b == 0.0:
        return np.zeros_like(s)

    L = params.length
    # Normalized buoyancy contribution (negative, counteracting gravity)
    buoyancy_normalized = -params.rho_CSF * params.g * (L - s) / (params.rho_tissue * params.g * L)
    
    return params.chi_b * buoyancy_normalized


def compute_effective_load(
    params: IECParameters
) -> Tuple[float, NDArray[np.float64]]:
    """
    Compute effective load accounting for CSF buoyancy.

    P_effective = P_load - P_buoyant
    where P_buoyant = ρ_CSF · g · A_cross · L

    Also computes distributed load accounting for effective weight:
    w_effective(s) = (ρ_tissue - ρ_CSF) · g · A_cross

    Args:
        params: IEC parameters

    Returns:
        Tuple of (P_effective, w_effective):
        - P_effective: Effective tip load (N)
        - w_effective: Effective distributed load (N/m), shape (n_nodes,)
    """
    if not params.include_buoyancy:
        s = params.get_s_array()
        return params.P_load, np.full(len(s), params.distributed_load)

    # Buoyant force reduces effective load
    P_buoyant = params.rho_CSF * params.g * params.A_cross * params.length
    P_effective = params.P_load - P_buoyant

    # Effective distributed load (accounting for buoyancy)
    rho_effective = params.rho_tissue - params.rho_CSF
    w_effective = rho_effective * params.g * params.A_cross + params.distributed_load

    s = params.get_s_array()
    w_array = np.full(len(s), w_effective)

    return P_effective, w_array
