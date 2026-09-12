# Newton rod readout

Status: **PREREQUISITE_FAILURE_NO_MECHANISTIC_VERDICT**

Input SHA256: `15bd31b5943b4119c3a1d3bc384fc949c50baaa9481e2e67da378a0ec4d450b8`.
Quantity: total absolute planar rod bend; not clinical Cobb. Angle conversion factor: 0.0208333333333.
Recorded ages: 5.083333 to 20.000000 years.
Full-window A2: not adjudicated: baseline absent.

| Bg | kr | bend min/max deg | control drift deg | permanent bend deg | bend sanity | A2 recorded window |
|---|---|---|---|---|---|---|
| 0.2 | 0.3 | 0.763152/86.5102 | 0.365053 | 45.7587 | False | True |
| 0.3 | 0.3 | 0.452355/9.33106 | 0.0236876 | 5.15187 | True | True |
| 0.5 | 0.3 | 0.220823/1.81296 | 0.000475964 | 1.18496 | True | True |
| 0.2 | 1.0 | 0.763152/27.8918 | 0.365053 | 10.5019 | False | True |
| 0.3 | 1.0 | 0.452355/3.47873 | 0.0236876 | 1.73704 | True | True |
| 0.5 | 1.0 | 0.220823/0.953754 | 0.000475964 | 0.5445 | True | True |
| 0.2 | 6.0 | 0.763152/3.3392 | 0.365053 | 0.81712 | True | True |
| 0.3 | 6.0 | 0.452355/0.945461 | 0.0236876 | 0.270008 | True | True |
| 0.5 | 6.0 | 0.220823/0.372536 | 0.000475964 | 0.112223 | True | True |

Per-Bg checks:

```json
{
  "0.2": {
    "sanity_pass": false,
    "a2_recorded_window_pass": true,
    "descriptive_final_order": true,
    "gate_c_conditional_on_recorded_window": null
  },
  "0.3": {
    "sanity_pass": true,
    "a2_recorded_window_pass": true,
    "descriptive_final_order": true,
    "gate_c_conditional_on_recorded_window": true
  },
  "0.5": {
    "sanity_pass": true,
    "a2_recorded_window_pass": true,
    "descriptive_final_order": true,
    "gate_c_conditional_on_recorded_window": true
  }
}
```

- Bend sanity bounds applied: 0.05-10.0 deg. The original 1-40 deg was written on the 48x-inflated scale; the amended bounds were adopted before any full-run output existed (PREREG_2026-09-12.md, Amendment).
- A failed measurement/sanity prerequisite is not a biological null.
- Scalar amplitude retains the original mean-across-worlds/full-L definition; it is not a Bg-matched joint-mean calibration.
- No statement here validates AIS, vertebral growth, or a clinical Cobb measurement.
