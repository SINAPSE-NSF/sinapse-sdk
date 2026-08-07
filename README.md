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
  - AsyncFlow — asynchronous workflow layer
  - Rootstock — interchangeable containerized AI models
  - [SEEKRFLOW] (https://github.com/seekrcentral/seekrflow) — 
    biomolecular rate-constant estimation
  - [QuAcc](https://github.com/Quantum-Accelerators/quacc) — quantum
    chemistry workflow recipes

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

Packaging is planned for pip, conda, and Spack under a common
namespace. Once released:

```
pip install sinapse-sdk
```

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

### SEEKRFLOW

  - Repo: https://github.com/seekrcentral/seekrflow
  - Docs: https://github.com/seekrcentral/seekrflow/tree/main/docs
  - SEEKR2 Docs: https://seekr2.readthedocs.io/en/latest/citations.html
