"""
Information-Elasticity Coupling (IEC) model core.

Implements three coupling mechanisms:
- IEC-1: Target curvature bias (χ_κ)
- IEC-2: Constitutive bias (χ_E, χ_C)
- IEC-3: Active moment (χ_f)
"""

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import numpy as np
from numpy.typing import NDArray


@dataclass
class IECParameters:
    """Parameters for Information-Elasticity Coupling model."""

    # Coupling strengths
    chi_kappa: float = 0.0  # Target curvature bias coupling
    chi_E: float = 0.0  # Young's modulus coupling
    chi_C: float = 0.0  # Damping/viscosity coupling
    chi_f: float = 0.0  # Active force/moment coupling

    # Baseline material properties
    E0: float = 1e9  # Baseline Young's modulus (Pa)
    C0: float = 1e6  # Baseline damping coefficient
    kappa_gen_baseline: float = 0.0  # Baseline target curvature (1/m)

    # Coherence field parameters
    I_mode: str = "constant"  # constant, linear, gaussian, step, file
    I_amplitude: float = 1.0  # Coherence field amplitude
    I_gradient: float = 0.0  # Linear gradient strength
    I_center: float = 0.5  # Center for gaussian/step (normalized)
    I_width: float = 0.1  # Width for gaussian (normalized)

    # Geometry
    length: float = 0.4  # Spine length (m)
    n_nodes: int = 100  # Number of spatial nodes

    def get_s_array(self) -> NDArray[np.float64]:
        """Generate spatial coordinate array."""
        return np.linspace(0, self.length, self.n_nodes)


def generate_coherence_field(
    s: NDArray[np.float64], params: IECParameters
) -> NDArray[np.float64]:
    """
    Generate information/coherence field I(s).

    Args:
        s: Spatial coordinates (m)
        params: IEC parameters

    Returns:
        Coherence field I(s), dimensionless
    """
    s_norm = s / params.length

    if params.I_mode == "constant":
        return np.ones_like(s) * params.I_amplitude

    elif params.I_mode == "linear":
        # Linear gradient: I(s) = I_amplitude * (1 + I_gradient * s_norm)
        return params.I_amplitude * (1.0 + params.I_gradient * s_norm)

    elif params.I_mode == "gaussian":
        # Gaussian bump centered at I_center
        return params.I_amplitude * np.exp(
            -((s_norm - params.I_center) ** 2) / (2 * params.I_width**2)
        )

    elif params.I_mode == "step":
        # Piecewise step function
        I_field = np.zeros_like(s)
        I_field[s_norm >= params.I_center] = params.I_amplitude
        return I_field

    else:
        raise ValueError(f"Unknown I_mode: {params.I_mode}")


def compute_gradient(
    field: NDArray[np.float64], s: NDArray[np.float64]
) -> NDArray[np.float64]:
    """
    Compute spatial gradient of a field using finite differences.

    Args:
        field: Field values at spatial points
        s: Spatial coordinates

    Returns:
        Gradient ∂field/∂s
    """
    return np.gradient(field, s)


def apply_iec_coupling(
    s: NDArray[np.float64], params: IECParameters
) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """
    Apply IEC couplings to modify mechanical properties.

    Args:
        s: Spatial coordinates
        params: IEC parameters

    Returns:
        Tuple of (kappa_target, E_field, C_field, M_active)
        - kappa_target: Target curvature profile (1/m)
        - E_field: Effective Young's modulus (Pa)
        - C_field: Effective damping coefficient
        - M_active: Active moment field (N·m)
    """
    # Generate coherence field
    I_field = generate_coherence_field(s, params)
    grad_I = compute_gradient(I_field, s)

    # IEC-1: Target curvature bias
    # \bar\kappa(s) = \bar\kappa_gen + χ_κ ∂_s I(s)
    kappa_target = params.kappa_gen_baseline + params.chi_kappa * grad_I

    # IEC-2: Constitutive bias
    # E = E_0 (1 + χ_E I)
    # C = C_0 (1 + χ_C I)
    E_field = params.E0 * (1.0 + params.chi_E * I_field)
    C_field = params.C0 * (1.0 + params.chi_C * I_field)

    # IEC-3: Active moment
    # M_act ∝ χ_f ∇I
    M_active = params.chi_f * grad_I

    return kappa_target, E_field, C_field, M_active


def compute_wavelength(
    s: NDArray[np.float64], theta: NDArray[np.float64]
) -> Optional[float]:
    """
    Compute dominant wavelength from angle profile using zero-crossings.

    Args:
        s: Spatial coordinates (m)
        theta: Angle/curvature profile

    Returns:
        Wavelength in mm, or None if cannot determine
    """
    # Find zero crossings
    theta_centered = theta - np.mean(theta)
    sign_changes = np.diff(np.sign(theta_centered))
    zero_crossings = np.where(sign_changes != 0)[0]

    if len(zero_crossings) < 2:
        return None

    # Estimate wavelength from mean distance between zero crossings
    # Full wavelength = 2 * mean distance
    distances = np.diff(s[zero_crossings])
    wavelength_m = 2.0 * np.mean(distances)
    return wavelength_m * 1000.0  # Convert to mm


def compute_node_positions(
    s: NDArray[np.float64], theta: NDArray[np.float64], threshold: float = 0.01
) -> NDArray[np.float64]:
    """
    Find node positions (points of minimal displacement/angle).

    Args:
        s: Spatial coordinates (m)
        theta: Angle profile
        threshold: Threshold for node detection

    Returns:
        Array of node positions (m)
    """
    theta_centered = theta - np.mean(theta)
    theta_abs = np.abs(theta_centered)

    # Find local minima below threshold
    local_min_idx = []
    for i in range(1, len(theta_abs) - 1):
        if theta_abs[i] < theta_abs[i - 1] and theta_abs[i] < theta_abs[i + 1]:
            if theta_abs[i] < threshold * np.max(theta_abs):
                local_min_idx.append(i)

    return s[local_min_idx]


def compute_amplitude(theta: NDArray[np.float64]) -> float:
    """
    Compute amplitude (peak-to-peak) of angle profile.

    Args:
        theta: Angle profile (radians)

    Returns:
        Amplitude in degrees
    """
    amplitude_rad = np.max(theta) - np.min(theta)
    return np.rad2deg(amplitude_rad)


def compute_torsion_stats(
    tau: NDArray[np.float64],
) -> dict:
    """
    Compute statistics of torsion field.

    Args:
        tau: Torsion profile (1/m)

    Returns:
        Dictionary with torsion statistics
    """
    return {
        "mean": float(np.mean(tau)),
        "std": float(np.std(tau)),
        "max": float(np.max(np.abs(tau))),
        "rms": float(np.sqrt(np.mean(tau**2))),
    }


def compute_helical_threshold(
    delta_b: float, grad_I_norm: float, chi_f: float = 0.0
) -> float:
    """
    Estimate helical instability threshold.

    Simplified model: threshold reduces with information gradient.

    Args:
        delta_b: Asymmetry parameter
        grad_I_norm: Normalized gradient magnitude ||∇I||
        chi_f: Active coupling strength

    Returns:
        Threshold value (dimensionless)
    """
    # Baseline threshold from symmetry-breaking
    baseline_threshold = 0.1 + delta_b

    # Reduction due to information gradient
    reduction = chi_f * grad_I_norm * 0.5

    return max(0.01, baseline_threshold - reduction)


def solve_beam_static(
    s: NDArray[np.float64],
    kappa_target: NDArray[np.float64],
    E_field: NDArray[np.float64],
    M_active: NDArray[np.float64],
    I_moment: float = 1e-8,
    P_load: float = 100.0,
) -> Tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Solve static beam equation with IEC couplings.

    Simplified solver: EI d²θ/ds² + M_active = P·e_load + (κ_target - κ)·k_restore

    Args:
        s: Spatial coordinates
        kappa_target: Target curvature profile
        E_field: Effective Young's modulus
        M_active: Active moment
        I_moment: Second moment of area (m^4)
        P_load: Applied load (N)

    Returns:
        Tuple of (theta, kappa) - angle and curvature profiles
    """
    n = len(s)
    ds = s[1] - s[0]

    # Effective stiffness
    EI = E_field * I_moment

    # Initialize
    theta = np.zeros(n)
    kappa = np.zeros(n)

    # Simple forward integration with restoring force
    k_restore = 1e3  # Restoring stiffness

    for i in range(1, n - 1):
        # Discrete second derivative: d²θ/ds² ≈ (θ[i+1] - 2θ[i] + θ[i-1])/ds²
        # EI·d²θ + M_active = P + k(κ_target - κ)
        # Simplified: accumulate curvature bias
        curvature_error = kappa_target[i] - kappa[i]
        theta[i] = theta[i - 1] + ds * (kappa[i - 1] + 0.1 * curvature_error)
        kappa[i] = (theta[i] - theta[i - 1]) / ds

    return theta, kappa


def solve_dynamic_modes(
    s: NDArray[np.float64],
    E_field: NDArray[np.float64],
    C_field: NDArray[np.float64],
    I_moment: float = 1e-8,
    rho: float = 1000.0,
    A_cross: float = 1e-4,
) -> dict:
    """
    Solve for dynamic mode properties (eigenfrequencies, damping ratios).

    Args:
        s: Spatial coordinates
        E_field: Effective Young's modulus
        C_field: Effective damping
        I_moment: Second moment of area
        rho: Density (kg/m³)
        A_cross: Cross-sectional area (m²)

    Returns:
        Dictionary with mode properties
    """
    L = s[-1]
    # Average properties
    E_avg = np.mean(E_field)
    C_avg = np.mean(C_field)

    # Fundamental frequency (pinned-pinned beam)
    omega_1 = (np.pi / L) ** 2 * np.sqrt((E_avg * I_moment) / (rho * A_cross))

    # Damping ratio
    zeta = C_avg / (2 * np.sqrt(rho * A_cross * E_avg * I_moment))

    return {
        "frequency_hz": omega_1 / (2 * np.pi),
        "damping_ratio": zeta,
        "wavelength_mm": 2 * L * 1000,  # Fundamental mode wavelength
    }

