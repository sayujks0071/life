"""Spinal modes: Counter-curvature and IEC model."""

__version__ = "0.1.0"

from spinalmodes.iec import (
    IECParameters,
    apply_iec_coupling,
    generate_coherence_field,
    solve_beam_static,
)

__all__ = [
    "IECParameters",
    "apply_iec_coupling",
    "generate_coherence_field",
    "solve_beam_static",
]
