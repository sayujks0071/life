"""Tests for the countercurvature extension opposing gravitational bending."""

import numpy as np

from model.core import IECParameters
from model.countercurvature import (
    apply_countercurvature,
    compute_gravitational_curvature_profile,
    compute_gravitational_moment_profile,
)


def test_no_countercurvature_returns_inputs():
    """When gain is zero the original fields should be unchanged."""
    params = IECParameters(countercurvature_gain=0.0, n_nodes=10)
    s = params.get_s_array()
    kappa = np.linspace(0.0, 1e-3, params.n_nodes)
    moments = np.linspace(0.0, 1e-2, params.n_nodes)

    kappa_out, moments_out = apply_countercurvature(s, params, kappa, moments)

    assert np.allclose(kappa_out, kappa)
    assert np.allclose(moments_out, moments)


def test_countercurvature_opposes_gravity_by_default():
    """Positive gain should oppose gravitational curvature by default orientation."""
    params = IECParameters(countercurvature_gain=1.0, n_nodes=25)
    s = params.get_s_array()
    baseline_kappa = np.zeros_like(s)
    baseline_moment = np.zeros_like(s)

    kappa_out, moment_out = apply_countercurvature(
        s, params, baseline_kappa, baseline_moment
    )

    gravitational_kappa = compute_gravitational_curvature_profile(s, params)
    gravitational_moment = compute_gravitational_moment_profile(s, params)

    # Growth against gravity should flip the sign of gravitational contributions
    assert np.allclose(kappa_out, -gravitational_kappa)
    assert np.allclose(moment_out, -gravitational_moment)


def test_orientation_with_gravity_reinforces_curvature():
    """Switching orientation should align with gravitational bending."""
    params = IECParameters(
        countercurvature_gain=0.5,
        countercurvature_orientation="with_gravity",
        n_nodes=30,
    )
    s = params.get_s_array()
    kappa_out, moment_out = apply_countercurvature(
        s, params, np.zeros_like(s), np.zeros_like(s)
    )

    gravitational_kappa = compute_gravitational_curvature_profile(s, params)
    gravitational_moment = compute_gravitational_moment_profile(s, params)

    assert np.allclose(kappa_out, 0.5 * gravitational_kappa)
    assert np.allclose(moment_out, 0.5 * gravitational_moment)
