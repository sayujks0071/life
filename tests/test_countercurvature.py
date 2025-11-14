import numpy as np

from spinalmodes.countercurvature import (
    CounterCurvatureParams,
    InfoFieldFactory,
    compute_active_moments,
    compute_effective_stiffness,
    compute_rest_curvature,
)


def test_info_field_factory_from_callable_linear_profile() -> None:
    s = np.linspace(0.0, 1.0, 5)
    factory = InfoFieldFactory()
    info = factory.from_callable(s, lambda x: x)
    np.testing.assert_allclose(info.s, s)
    np.testing.assert_allclose(info.I, s)
    np.testing.assert_allclose(info.dIds, np.ones_like(s))


def test_compute_rest_curvature_linear_gradient() -> None:
    factory = InfoFieldFactory()
    info = factory.from_array(np.linspace(0.0, 1.0, 3), [0.0, 0.5, 1.0])
    params = CounterCurvatureParams(chi_kappa=2.0, scale_length=1.0)
    baseline = np.zeros_like(info.s)
    kappa = compute_rest_curvature(info, params, baseline)
    np.testing.assert_allclose(kappa, 2.0 * info.dIds)


def test_compute_effective_stiffness_models() -> None:
    factory = InfoFieldFactory()
    info = factory.from_array(np.linspace(0.0, 1.0, 5), np.linspace(0.0, 0.4, 5))
    params = CounterCurvatureParams(chi_E=0.5)
    baseline = np.full(info.s.shape, 10.0)

    linear = compute_effective_stiffness(info, params, baseline, model="linear")
    np.testing.assert_allclose(linear, baseline * (1.0 + params.chi_E * info.I))

    exponential = compute_effective_stiffness(info, params, baseline, model="exponential")
    np.testing.assert_allclose(exponential, baseline * np.exp(params.chi_E * info.I))


def test_compute_active_moments() -> None:
    factory = InfoFieldFactory()
    info = factory.from_array(np.linspace(0.0, 1.0, 4), [0.0, 0.25, 0.5, 0.75])
    params = CounterCurvatureParams(chi_M=0.1, scale_length=2.0)
    moments = compute_active_moments(info, params)
    np.testing.assert_allclose(moments, params.chi_M * params.scale_length * info.dIds)
