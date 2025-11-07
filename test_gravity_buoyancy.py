"""
Test script for gravity and buoyancy extensions to IEC model.
"""

import numpy as np
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from model.core import IECParameters
from model.coherence_fields import (
    generate_coherence_field,
    compute_gravity_information_field,
    compute_buoyancy_information_field,
    compute_effective_load,
)
from model.couplings import apply_iec_coupling


def test_gravity_information_field():
    """Test gravity-dependent information field computation."""
    print("Testing gravity information field...")
    
    params = IECParameters(
        include_gravity=True,
        chi_g=0.2,
        length=0.4,
        rho_tissue=1050.0,
        rho_CSF=1000.0,
        g=9.81,
    )
    
    s = params.get_s_array()
    I_gravity = compute_gravity_information_field(s, params)
    
    # Should be non-zero when enabled
    assert np.any(I_gravity != 0), "Gravity field should be non-zero"
    assert np.all(np.isfinite(I_gravity)), "Gravity field should be finite"
    
    # Should increase from base to tip (more stress at base)
    assert I_gravity[0] > I_gravity[-1], "Gravity field should decrease from base to tip"
    
    print("  ✓ Gravity information field test passed")
    return True


def test_buoyancy_information_field():
    """Test buoyancy-dependent information field computation."""
    print("Testing buoyancy information field...")
    
    params = IECParameters(
        include_buoyancy=True,
        chi_b=-0.15,
        length=0.4,
        rho_tissue=1050.0,
        rho_CSF=1000.0,
        g=9.81,
    )
    
    s = params.get_s_array()
    I_buoyancy = compute_buoyancy_information_field(s, params)
    
    # Should be non-zero when enabled
    assert np.any(I_buoyancy != 0), "Buoyancy field should be non-zero"
    assert np.all(np.isfinite(I_buoyancy)), "Buoyancy field should be finite"
    
    # Should be negative (counteracting gravity)
    assert np.all(I_buoyancy <= 0), "Buoyancy field should be negative (counteracting)"
    
    print("  ✓ Buoyancy information field test passed")
    return True


def test_effective_load():
    """Test effective load calculation with buoyancy."""
    print("Testing effective load calculation...")
    
    params = IECParameters(
        include_buoyancy=True,
        P_load=100.0,
        rho_CSF=1000.0,
        rho_tissue=1050.0,
        g=9.81,
        A_cross=1e-4,
        length=0.4,
    )
    
    P_effective, w_effective = compute_effective_load(params)
    
    # Effective load should be less than applied load (buoyancy reduces it)
    assert P_effective < params.P_load, "Effective load should be less than applied load"
    
    # Calculate expected buoyant force
    P_buoyant_expected = params.rho_CSF * params.g * params.A_cross * params.length
    P_effective_expected = params.P_load - P_buoyant_expected
    
    assert np.abs(P_effective - P_effective_expected) < 1e-6, \
        f"Effective load mismatch: {P_effective} vs {P_effective_expected}"
    
    print(f"  ✓ Effective load: {P_effective:.2f} N (reduced from {params.P_load:.2f} N)")
    print(f"    Buoyant force: {P_buoyant_expected:.2f} N")
    print(f"    Reduction: {(P_buoyant_expected/params.P_load*100):.1f}%")
    
    return True


def test_combined_information_field():
    """Test combined information field with gravity and buoyancy."""
    print("Testing combined information field...")
    
    params = IECParameters(
        I_mode="linear",
        I_gradient=0.5,
        include_gravity=True,
        include_buoyancy=True,
        chi_g=0.2,
        chi_b=-0.15,
    )
    
    s = params.get_s_array()
    
    # Generate components
    I_genetic = generate_coherence_field(s, params)
    I_gravity = compute_gravity_information_field(s, params)
    I_buoyancy = compute_buoyancy_information_field(s, params)
    I_total = I_genetic + I_gravity + I_buoyancy
    
    # Total should be sum of components
    assert np.allclose(I_total, I_genetic + I_gravity + I_buoyancy), \
        "Total field should equal sum of components"
    
    # Test IEC coupling with combined field
    kappa_target, E_field, C_field, M_active = apply_iec_coupling(s, params)
    
    assert len(kappa_target) == len(s), "Curvature should match spatial array length"
    assert np.all(np.isfinite(kappa_target)), "Curvature should be finite"
    
    print("  ✓ Combined information field test passed")
    print(f"    Genetic component range: [{np.min(I_genetic):.3f}, {np.max(I_genetic):.3f}]")
    print(f"    Gravity component range: [{np.min(I_gravity):.3f}, {np.max(I_gravity):.3f}]")
    print(f"    Buoyancy component range: [{np.min(I_buoyancy):.3f}, {np.max(I_buoyancy):.3f}]")
    print(f"    Total field range: [{np.min(I_total):.3f}, {np.max(I_total):.3f}]")
    
    return True


def test_parameter_validation():
    """Test parameter validation for new fields."""
    print("Testing parameter validation...")
    
    # Test invalid density (tissue < CSF)
    try:
        params = IECParameters(
            rho_tissue=900.0,
            rho_CSF=1000.0,
        )
        assert False, "Should raise ValueError for invalid density"
    except ValueError:
        print("  ✓ Correctly rejected invalid density")
    
    # Test valid parameters
    params = IECParameters(
        rho_tissue=1050.0,
        rho_CSF=1000.0,
        chi_g=0.2,
        chi_b=-0.15,
        include_gravity=True,
        include_buoyancy=True,
    )
    
    assert params.rho_tissue > params.rho_CSF, "Valid density relationship"
    print("  ✓ Parameter validation test passed")
    
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Testing Gravity and Buoyancy Extensions to IEC Model")
    print("=" * 60)
    print()
    
    tests = [
        test_parameter_validation,
        test_gravity_information_field,
        test_buoyancy_information_field,
        test_effective_load,
        test_combined_information_field,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ✗ Test failed with error: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Tests passed: {passed}/{len(tests)}")
    print(f"Tests failed: {failed}/{len(tests)}")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
