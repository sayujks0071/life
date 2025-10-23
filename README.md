# Spinal Modes: Counter-Curvature & IEC Model

[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A research codebase for studying biological counter-curvature and Information→Elasticity Coupling (IEC) in spinal biomechanics, integrating developmental genetics (HOX/PAX), ciliary origins, and scoliosis as symmetry-breaking.

## Overview

This package implements:
- **IEC Model**: Three coupling mechanisms linking information fields to mechanical properties
  - IEC-1: Target curvature bias (χ_κ)
  - IEC-2: Constitutive bias (χ_E, χ_C)
  - IEC-3: Active moment (χ_f)
- **Beam/Cosserat Solvers**: For spinal mechanics with coupled oscillators
- **Phase Analysis**: Parameter sweeps, node drift, helical threshold computations
- **Figure Generation**: Publication-ready figures with validation

## Installation

```bash
# Install dependencies
poetry install

# Verify installation
poetry run spinalmodes --help
```

## Quick Start

```bash
# Run IEC demo
poetry run spinalmodes iec demo --out-prefix outputs/csv/iec_demo

# Generate phase diagram
poetry run spinalmodes iec phase \
  --delta-b 0.0:0.2:41 \
  --gradI 0.0:0.1:21 \
  --out-csv outputs/csv/iec_phase_map.csv \
  --out-fig outputs/figs/fig_iec_phase.png

# Node drift analysis
poetry run spinalmodes iec node-drift \
  --I-mode step \
  --chi-kappa 0.04 \
  --out-fig outputs/figs/fig_iec_node_drift.png
```

## Development

```bash
# Run all checks
make green

# Run tests
make test

# Format code
make format

# Validate figures
poetry run python tools/validate_figures.py
```

## Project Structure

```
spinalmodes/
├── src/spinalmodes/       # Core package
│   ├── iec.py            # IEC model utilities
│   ├── iec_cli.py        # CLI commands
│   ├── fig_*.py          # Figure generation
│   └── solvers/          # Beam/Cosserat solvers
├── tests/                # Unit tests
├── docs/                 # Documentation & manuscript
├── outputs/              # Generated outputs
│   ├── figs/            # Figures (PNG + JSON)
│   ├── csv/             # Data tables
│   ├── aor/             # Analysis of record
│   └── reports/         # Reports
└── tools/               # Validation scripts
```

## Documentation

- [CLI Reference](docs/cli.md)
- [Figure Guide](docs/figures.md)
- [Manuscript](docs/manuscript/SpinalCountercurvature_IEC.md)

## Citation

If you use this code, please cite:
```
Krishnan, S. et al. (2025). Biological Counter-Curvature and Information-Elasticity
Coupling in Spinal Development. [Journal TBD].
```

## License

MIT License - see LICENSE file for details.

