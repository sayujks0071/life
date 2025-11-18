# Countercurvature Growth Response

## Biological Motivation
Living systems routinely exhibit gravitropic responses: shoots grow upward,
roots downward, and vertebrate embryos sculpt their spine against body-weight
loading.  The countercurvature hypothesis posits that this behavior is not
merely passive elastic recoil but an active growth program that senses the
vector of gravity and deposits tissue to oppose the induced bending.

## Mechanical Representation
The implementation keeps the mechanical substrate classical:

- Gravity is modeled as a uniform distributed load ``q = \rho A g`` over a
  cantilevered spinal segment of length ``L``.
- Internal bending moments follow the Euler–Bernoulli solution
  ``M(s) = q (L s - s^2 / 2)``.
- Curvature arises from ``\kappa(s) = M(s) / (E I)`` where ``E`` is the local
  Young's modulus and ``I`` the second moment of area.

These profiles are exported by :mod:`model.countercurvature` and feed directly
into the IEC coupling pipeline.

## Growth-Based Opposition to Gravity
The new :func:`model.countercurvature.apply_countercurvature` function adjusts
the target curvature (IEC-1) and active moment (IEC-3) fields according to two
parameters stored in :class:`model.core.IECParameters`:

1. ``countercurvature_gain`` — a scalar multiplier describing how strongly
growth reacts to gravity.  A value of zero leaves the system unchanged, while
positive values subtract a scaled copy of the gravitational curvature/moment.
2. ``countercurvature_orientation`` — selects whether growth works
``against_gravity`` (default) or ``with_gravity``.  Flipping the orientation
allows experiments that intentionally reinforce gravitational bending.

This controller does not remove gravity from the system.  Instead it overlays a
directed growth signal that adds or subtracts the gravitational profile from the
target fields, reflecting the biological observation that organisms build
structure to counter external loads.

## Usage Walkthrough
```python
from model.core import IECParameters
from model.couplings import apply_iec_coupling

params = IECParameters(
    chi_kappa=0.02,
    chi_f=0.05,
    countercurvature_gain=1.5,
    countercurvature_orientation="against_gravity",
)

s = params.get_s_array()
# Returns curvature, modulus, damping, and active moment fields with
# countercurvature already applied.
kappa_target, E_field, C_field, M_active = apply_iec_coupling(s, params)
```

For hypothesis testing you can sweep ``countercurvature_gain`` from 0 (no
active response) up to the physical limit defined in
:mod:`model.core` and compare equilibrium shapes produced by the BVP solver.
