"""Information field representations for countercurvature analog models.

The :class:`InfoField1D` container stores the discretised information density
:math:`I(s)` and its spatial gradient along the arclength coordinate of a rod or
spinal segment.  In the countercurvature framework, gradients of :math:`I`
provide the source terms that bias mechanical curvature and stiffness, modelling
how biological information processing acts as an effective local
"countercurvature" opposing gravitational sag.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, NamedTuple

import numpy as np
from numpy.typing import NDArray

ArrayLike = NDArray[np.float64]


class InfoField1D(NamedTuple):
    r"""One-dimensional information field sampled on an arclength grid.

    Parameters
    ----------
    s:
        Monotonic arclength coordinates in metres with shape ``(N,)``.
    I:
        Dimensionless information density :math:`I(s)` evaluated at ``s``.
    dIds:
        Spatial derivative :math:`\partial I/\partial s` on the same grid.  Units
        are ``1/m`` provided ``I`` is dimensionless.  This gradient acts as the
        primary source of biological countercurvature in the mechanical
        couplings.
    """

    s: ArrayLike
    I: ArrayLike
    dIds: ArrayLike

    def assert_consistent(self) -> None:
        """Validate array shapes and monotonicity of the arclength grid."""

        if not (self.s.ndim == self.I.ndim == self.dIds.ndim == 1):
            raise ValueError("InfoField1D arrays must be one-dimensional.")
        if not (self.s.shape == self.I.shape == self.dIds.shape):
            raise ValueError("InfoField1D arrays must share the same shape.")
        if not np.all(np.diff(self.s) > 0.0):
            raise ValueError("Arclength grid `s` must be strictly increasing.")


@dataclass(slots=True)
class InfoFieldFactory:
    """Factory utilities for constructing :class:`InfoField1D` instances.

    The factory centralises common discretisations used throughout the
    countercurvature experiments.  Each constructor ensures consistent gradient
    estimation so that downstream couplings receive physically interpretable
    countercurvature source terms.
    """

    gradient_mode: str = "central"

    def _compute_gradient(self, values: ArrayLike, s: ArrayLike) -> ArrayLike:
        """Return ``∂values/∂s`` using the configured finite-difference rule."""

        if self.gradient_mode == "central":
            return np.gradient(values, s, edge_order=2)
        if self.gradient_mode == "forward":
            return np.gradient(values, s, edge_order=1)
        raise ValueError(f"Unknown gradient_mode: {self.gradient_mode}")

    def from_callable(
        self,
        s_grid: ArrayLike,
        I_func: Callable[[ArrayLike], ArrayLike],
    ) -> InfoField1D:
        """Construct an information field by sampling ``I_func`` on ``s_grid``.

        Parameters
        ----------
        s_grid:
            Arclength coordinates (m) with shape ``(N,)``.
        I_func:
            Callable producing the information density at each location.

        Returns
        -------
        InfoField1D
            Populated data structure with consistent gradient estimates.
        """

        s = np.asarray(s_grid, dtype=float)
        I = np.asarray(I_func(s), dtype=float)
        dIds = self._compute_gradient(I, s)
        field = InfoField1D(s=s, I=I, dIds=dIds)
        field.assert_consistent()
        return field

    def from_array(self, s: ArrayLike, I: ArrayLike) -> InfoField1D:
        """Construct an information field from pre-tabulated arrays."""

        s_arr = np.asarray(s, dtype=float)
        I_arr = np.asarray(I, dtype=float)
        dIds = self._compute_gradient(I_arr, s_arr)
        field = InfoField1D(s=s_arr, I=I_arr, dIds=dIds)
        field.assert_consistent()
        return field

    def from_profile(
        self,
        length: float,
        n_points: int,
        profile: Callable[[ArrayLike], ArrayLike],
    ) -> InfoField1D:
        """Create a field on an evenly spaced grid spanning ``[0, length]``.

        The helper is convenient for experiments that prescribe analytical
        information landscapes (e.g., sigmoidal growth programmes or oscillatory
        neural activity).  The resulting gradient provides the countercurvature
        source term :math:`∂I/∂s` used to bias the Cosserat rod mechanics.
        """

        s = np.linspace(0.0, float(length), int(n_points))
        return self.from_callable(s, profile)
