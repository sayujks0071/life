# Newton rod readout

Status: **SMOKE_ONLY_NO_GATES**

Input SHA256: `12b741f6af66662cd6e06052b4a1c516e502c15bff70699a23f6b0c96838dc13`.
Quantity: total absolute planar rod bend; not clinical Cobb. Angle conversion factor: 0.0208333333333.
Recorded ages: 5.083333 to 6.000000 years.
Full-window A2: not adjudicated: baseline absent.

| Bg | kr | bend min/max deg | control drift deg | permanent bend deg | angle sanity | A2 recorded window |
|---|---|---|---|---|---|---|
| 0.2 | 0.3 | 0.763152/1.17102 | 0.364952 | not read (smoke) | False | None |
| 0.3 | 0.3 | 0.452355/0.488607 | 0.0236734 | not read (smoke) | False | None |
| 0.5 | 0.3 | 0.220823/0.225842 | 0.000470831 | not read (smoke) | False | None |
| 0.2 | 1.0 | 0.763152/1.14296 | 0.364952 | not read (smoke) | False | None |
| 0.3 | 1.0 | 0.452355/0.480491 | 0.0236734 | not read (smoke) | False | None |
| 0.5 | 1.0 | 0.220823/0.222944 | 0.000470831 | not read (smoke) | False | None |
| 0.2 | 6.0 | 0.763152/1.13068 | 0.364952 | not read (smoke) | False | None |
| 0.3 | 6.0 | 0.452355/0.476819 | 0.0236734 | not read (smoke) | False | None |
| 0.5 | 6.0 | 0.220823/0.221606 | 0.000470831 | not read (smoke) | False | None |

Per-Bg checks:

```json
{
  "0.2": {
    "sanity_pass": false,
    "a2_recorded_window_pass": null,
    "descriptive_final_order": null,
    "gate_c_conditional_on_recorded_window": null
  },
  "0.3": {
    "sanity_pass": false,
    "a2_recorded_window_pass": null,
    "descriptive_final_order": null,
    "gate_c_conditional_on_recorded_window": null
  },
  "0.5": {
    "sanity_pass": false,
    "a2_recorded_window_pass": null,
    "descriptive_final_order": null,
    "gate_c_conditional_on_recorded_window": null
  }
}
```

- 1-40 degree range is retained from the board reading of the preregistration, not retuned after correction.
- The preregistration's smoke magnitudes were computed before the 48-fold reporting error was found.
- A failed measurement/sanity prerequisite is not a biological null.
- Scalar amplitude retains the original mean-across-worlds/full-L definition; it is not a Bg-matched joint-mean calibration.
- No statement here validates AIS, vertebral growth, or a clinical Cobb measurement.
