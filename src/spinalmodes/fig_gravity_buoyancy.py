"""
Visualization of gravity, buoyancy, and spacetime curvature effects in IEC model.

Generates figures showing:
1. Information field components (genetic, gravity, buoyancy, total)
2. Effective load reduction from buoyancy
3. Spacetime curvature analogy visualization
4. Comparison of curvature with/without gravity/buoyancy
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from pathlib import Path
import json
from typing import Dict, Any

import sys
from pathlib import Path as PathLib
sys.path.insert(0, str(PathLib(__file__).parents[2]))

from model.core import IECParameters
from model.coherence_fields import (
    generate_coherence_field,
    compute_gravity_information_field,
    compute_buoyancy_information_field,
    compute_effective_load,
)
from model.couplings import apply_iec_coupling
from model.solvers.bvp_scipy import BVPSolver


def plot_information_field_components(
    params: IECParameters, ax: plt.Axes, title: str = "Information Field Components"
) -> None:
    """
    Plot breakdown of information field into components.
    
    Args:
        params: IEC parameters
        ax: Matplotlib axes
        title: Plot title
    """
    s = params.get_s_array()
    
    # Generate components
    I_genetic = generate_coherence_field(s, params)
    I_gravity = compute_gravity_information_field(s, params)
    I_buoyancy = compute_buoyancy_information_field(s, params)
    I_total = I_genetic + I_gravity + I_buoyancy
    
    # Plot
    ax.plot(s * 1000, I_genetic, 'b-', label='Genetic (HOX/PAX)', linewidth=2)
    if params.include_gravity:
        ax.plot(s * 1000, I_gravity, 'r--', label='Gravity', linewidth=2, alpha=0.7)
    if params.include_buoyancy:
        ax.plot(s * 1000, I_buoyancy, 'g--', label='Buoyancy', linewidth=2, alpha=0.7)
    ax.plot(s * 1000, I_total, 'k-', label='Total I(s)', linewidth=3, alpha=0.8)
    
    ax.set_xlabel('Position along spine (mm)', fontsize=11)
    ax.set_ylabel('Information field I(s)', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, params.length * 1000)


def plot_buoyancy_effect(
    params: IECParameters, ax: plt.Axes
) -> None:
    """
    Plot effective load reduction from CSF buoyancy.
    
    Args:
        params: IEC parameters
        ax: Matplotlib axes
    """
    P_effective, w_effective = compute_effective_load(params)
    
    # Calculate buoyant force
    P_buoyant = params.rho_CSF * params.g * params.A_cross * params.length
    
    # Create bar plot
    categories = ['Applied Load', 'Buoyant Force', 'Effective Load']
    values = [params.P_load, -P_buoyant, P_effective]
    colors = ['blue', 'green', 'red']
    
    bars = ax.bar(categories, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f} N',
                ha='center', va='bottom' if height > 0 else 'top', fontsize=10)
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_ylabel('Force (N)', fontsize=11)
    ax.set_title('CSF Buoyancy Effect on Load', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add reduction percentage
    reduction_pct = (P_buoyant / params.P_load * 100) if params.P_load > 0 else 0
    ax.text(0.5, 0.95, f'Load reduction: {reduction_pct:.1f}%',
            transform=ax.transAxes, ha='center', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            fontsize=10)


def plot_spacetime_curvature_analogy(
    params: IECParameters, ax: plt.Axes
) -> None:
    """
    Visualize spacetime curvature analogy: information field → mechanical curvature.
    
    Args:
        params: IEC parameters
        ax: Matplotlib axes
    """
    s = params.get_s_array()
    
    # Generate information field (analogous to mass-energy distribution)
    I_genetic = generate_coherence_field(s, params)
    I_gravity = compute_gravity_information_field(s, params)
    I_buoyancy = compute_buoyancy_information_field(s, params)
    I_total = I_genetic + I_gravity + I_buoyancy
    
    # Compute curvature (analogous to spacetime curvature)
    kappa_target, E_field, C_field, M_active = apply_iec_coupling(s, params)
    
    # Normalize for visualization
    I_norm = I_total / (np.max(np.abs(I_total)) + 1e-10)
    kappa_norm = kappa_target / (np.max(np.abs(kappa_target)) + 1e-10)
    
    # Plot analogy
    ax2 = ax.twinx()
    
    line1 = ax.plot(s * 1000, I_norm, 'b-', label='Information Field I(s)\n(mass-energy)', 
                    linewidth=2.5, alpha=0.8)
    line2 = ax2.plot(s * 1000, kappa_norm, 'r--', label='Curvature κ(s)\n(spacetime)', 
                     linewidth=2.5, alpha=0.8)
    
    # Combine legends
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax.legend(lines, labels, loc='best', fontsize=9)
    
    ax.set_xlabel('Position along spine (mm)', fontsize=11)
    ax.set_ylabel('Information Field I(s)\n(normalized)', fontsize=11, color='b')
    ax2.set_ylabel('Curvature κ(s)\n(normalized)', fontsize=11, color='r')
    ax.tick_params(axis='y', labelcolor='b')
    ax2.tick_params(axis='y', labelcolor='r')
    ax.set_title('Spacetime Curvature Analogy:\nI(s) → κ(s)', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)


def plot_curvature_comparison(
    params_base: IECParameters,
    params_gravity: IECParameters,
    params_buoyancy: IECParameters,
    ax: plt.Axes
) -> None:
    """
    Compare curvature with/without gravity and buoyancy effects.
    
    Args:
        params_base: Base parameters (no gravity/buoyancy)
        params_gravity: With gravity only
        params_buoyancy: With gravity + buoyancy
        ax: Matplotlib axes
    """
    s = params_base.get_s_array()
    
    # Solve for each case
    solver_base = BVPSolver(params_base, bc_type="cantilever")
    solver_gravity = BVPSolver(params_gravity, bc_type="cantilever")
    solver_buoyancy = BVPSolver(params_buoyancy, bc_type="cantilever")
    
    try:
        state_base = solver_base.solve()
        state_gravity = solver_gravity.solve()
        state_buoyancy = solver_buoyancy.solve()
        
        ax.plot(s * 1000, np.rad2deg(state_base.theta), 'k-', 
                label='Base (no gravity/buoyancy)', linewidth=2)
        ax.plot(s * 1000, np.rad2deg(state_gravity.theta), 'r--', 
                label='With gravity', linewidth=2, alpha=0.8)
        ax.plot(s * 1000, np.rad2deg(state_buoyancy.theta), 'g:', 
                label='With gravity + buoyancy', linewidth=2, alpha=0.8)
        
    except Exception as e:
        # Fallback: plot target curvature instead
        kappa_base, _, _, _ = apply_iec_coupling(s, params_base)
        kappa_gravity, _, _, _ = apply_iec_coupling(s, params_gravity)
        kappa_buoyancy, _, _, _ = apply_iec_coupling(s, params_buoyancy)
        
        ax.plot(s * 1000, kappa_base * 1000, 'k-', 
                label='Base (no gravity/buoyancy)', linewidth=2)
        ax.plot(s * 1000, kappa_gravity * 1000, 'r--', 
                label='With gravity', linewidth=2, alpha=0.8)
        ax.plot(s * 1000, kappa_buoyancy * 1000, 'g:', 
                label='With gravity + buoyancy', linewidth=2, alpha=0.8)
    
    ax.set_xlabel('Position along spine (mm)', fontsize=11)
    ax.set_ylabel('Deflection angle (deg) or Curvature (1/m × 1000)', fontsize=11)
    ax.set_title('Effect of Gravity and Buoyancy on Curvature', fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(True, alpha=0.3)


def generate_gravity_buoyancy_figure(
    output_path: str = "outputs/figs/fig_gravity_buoyancy.png",
    params: IECParameters = None
) -> Dict[str, Any]:
    """
    Generate comprehensive figure showing gravity, buoyancy, and spacetime curvature effects.
    
    Args:
        output_path: Output file path
        params: IEC parameters (if None, uses defaults with gravity/buoyancy enabled)
    
    Returns:
        Metadata dictionary
    """
    # Create output directory
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Default parameters with gravity/buoyancy enabled
    if params is None:
        params = IECParameters(
            chi_kappa=0.04,
            chi_E=0.1,
            chi_f=0.05,
            I_mode="linear",
            I_gradient=0.5,
            include_gravity=True,
            include_buoyancy=True,
            chi_g=0.2,
            chi_b=-0.15,
            P_load=100.0,
        )
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # Panel A: Information field components
    ax_a = fig.add_subplot(gs[0, 0])
    plot_information_field_components(params, ax_a, "(A) Information Field Components")
    
    # Panel B: Buoyancy effect on load
    ax_b = fig.add_subplot(gs[0, 1])
    plot_buoyancy_effect(params, ax_b)
    
    # Panel C: Spacetime curvature analogy
    ax_c = fig.add_subplot(gs[1, :])
    plot_spacetime_curvature_analogy(params, ax_c)
    
    # Panel D: Curvature comparison
    ax_d = fig.add_subplot(gs[2, :])
    params_base = IECParameters(
        chi_kappa=params.chi_kappa,
        chi_E=params.chi_E,
        chi_f=params.chi_f,
        I_mode=params.I_mode,
        I_gradient=params.I_gradient,
        include_gravity=False,
        include_buoyancy=False,
        P_load=params.P_load,
    )
    params_gravity = IECParameters(
        chi_kappa=params.chi_kappa,
        chi_E=params.chi_E,
        chi_f=params.chi_f,
        I_mode=params.I_mode,
        I_gradient=params.I_gradient,
        include_gravity=True,
        include_buoyancy=False,
        chi_g=params.chi_g,
        P_load=params.P_load,
    )
    plot_curvature_comparison(params_base, params_gravity, params, ax_d)
    
    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    # Generate metadata
    P_effective, _ = compute_effective_load(params)
    P_buoyant = params.rho_CSF * params.g * params.A_cross * params.length
    
    metadata = {
        "figure_type": "gravity_buoyancy_spacetime",
        "output_path": output_path,
        "parameters": {
            "chi_kappa": params.chi_kappa,
            "chi_E": params.chi_E,
            "chi_f": params.chi_f,
            "chi_g": params.chi_g,
            "chi_b": params.chi_b,
            "include_gravity": params.include_gravity,
            "include_buoyancy": params.include_buoyancy,
            "P_load_N": params.P_load,
            "P_effective_N": float(P_effective),
            "P_buoyant_N": float(P_buoyant),
            "buoyancy_reduction_pct": float(P_buoyant / params.P_load * 100) if params.P_load > 0 else 0,
        },
        "description": "Comprehensive visualization of gravity, CSF buoyancy, and spacetime curvature effects in IEC model",
    }
    
    # Save metadata
    metadata_path = output_path.replace('.png', '.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return metadata


if __name__ == "__main__":
    # Generate figure
    metadata = generate_gravity_buoyancy_figure()
    print(f"Figure generated: {metadata['output_path']}")
    print(f"Buoyancy reduces load by {metadata['parameters']['buoyancy_reduction_pct']:.1f}%")
