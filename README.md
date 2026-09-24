# SINAPSE SDK

The SINAPSE SDK is a curated collection of software components for
AI-coupled HPC workflows, developed by the [SINAPSE
project](http://project-sinapse.org) (Scalable INfrastructure for
AI-coupled Predictive Simulation Enhancement, NSF award 2514139).

The SDK curates existing components and provides common packaging, testing,
documentation, and deployment across them, with well-defined integration points
between the components.

## Components

The initial SDK release targets the following components:

  - [RHAPSODY](https://github.com/radical-cybertools/rhapsody) —
    unified AI+HPC runtime supporting services alongside tasks
    (extends RADICAL-Pilot)
  - [AsyncFlow](https://github.com/radical-cybertools/radical.asyncflow) —
    asynchronous workflow layer
  - Rootstock — interchangeable containerized AI models
  - [Seekrflow](https://github.com/seekrcentral/seekrflow) — 
    biomolecular rate-constant estimation
  - [QuAcc](https://github.com/Quantum-Accelerators/quacc) — quantum
    chemistry workflow recipes
  - [DeepDriveSim](https://github.com/radical-collaboration/DeepDriveSim) —
    Deep learning-driven Adaptive Simulations

Components are classed as *core*, *associated*, or *external*; the set
of covered integrations will grow over subsequent releases.

## Maturity levels

  - **L0** — technologies individually collected: uniform
    documentation, packaging, testing, and processes
  - **L1** — components interoperate via pointwise, tool-specific
    integrations
  - **L2** — sustainable integration: well-defined APIs and
    integration points, deeply configurable

## Installation

The `sinapse-sdk` meta-package installs a mutually compatible set of the
SDK components. The conda package is the complete set:

```
conda install -c conda-forge sinapse-sdk
```

It pulls every component plus `flux-core` for RHAPSODY's Flux backend.
It installs on Linux (x86_64 and aarch64) with Python 3.11 or newer,
the floor set by its conda-only dependencies. The Dragon backend for
RHAPSODY is PyPI-only: `pip install dragonhpc` into that conda
environment.

The PyPI package covers the components that have PyPI releases:

```
pip install sinapse-sdk
```

Seekrflow (depends on SEEKR and OpenMM) and Flux are conda-only, so the
pip install lacks Seekrflow and RHAPSODY's Flux backend. The pip package
requires Python 3.9 or newer.

Each component can also be installed on its own; see the package links
under [Components](docs/components.md). Spack packaging is planned.

## Documentation

Documentation lives in [`docs/`](docs/) and is built with Sphinx; it
is published to [GitHub Pages](https://sinapse-nsf.github.io/sinapse-sdk/)
and configured for hosting on ReadTheDocs (`.readthedocs.yaml`). See
also the [project website](http://project-sinapse.org).

## License

The SINAPSE SDK is released under the [MIT license](LICENSE).
Individual components retain their own licenses.

## Acknowledgment

This work is supported by the National Science Foundation under award
2514139 (collaborative award; Rutgers University, University of
Chicago, Princeton University, UC San Diego).


## SDK Components

### Rhapsody

  - Repo: https://github.com/radical-cybertools/rhapsody/
  - Docs: https://radical-cybertools.github.io/rhapsody/
  - Pypi: https://pypi.org/project/rhapsody-py/

### Seekrflow

  - Repo: https://github.com/seekrcentral/seekrflow
  - Docs: https://seekrflow.readthedocs.io/en/latest/
  - Seekr Docs: https://seekr.readthedocs.io/en/latest/

### DeepDriveSim

  - Repo: https://github.com/radical-collaboration/DeepDriveSim
  - Docs: https://radical-collaboration.github.io/DeepDriveSim/
