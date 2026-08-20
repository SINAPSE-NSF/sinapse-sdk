# SINAPSE SDK

The SINAPSE SDK is a curated collection of software components for
AI-coupled HPC workflows (Scalable INfrastructure for
AI-coupled Predictive Simulation Enhancement, NSF award 2514139).

The SDK curates existing components and provides common packaging,
testing, documentation, and deployment across them, with well-defined
integration points between the components.

## Aims

Modern scientific computing increasingly couples AI models with
physics-based simulation — surrogate models steering ensembles,
simulations generating training data, inference services running
alongside HPC tasks. The tools that make this possible exist, but they
are developed independently, packaged differently, and integrated
ad hoc.

The SINAPSE SDK addresses this by:

- **Curating** a set of proven components for AI-coupled HPC workflows rather than building a monolithic framework.
- **Standardizing** packaging, testing, documentation, and release
  processes across the components.
- **Defining integration points** so components interoperate through
  well-specified APIs.

Components mature through three levels:

- **L0** — technologies individually collected: uniform documentation,
  packaging, testing, and processes
- **L1** — components interoperate via pointwise, tool-specific
  integrations
- **L2** — sustainable integration: well-defined APIs and integration
  points, deeply configurable

## Installation

Packaging is planned for pip and conda under a common namespace. Once released:

```console
$ conda install sinapse-sdk
```

```{note}
The SDK is under active development and the `sinapse-sdk` package is
currently a placeholder. Until the first release, install individual
components from their own repositories — see
[Components](components.md).
```

## Component documentation

Documentation for the released components:

- RHAPSODY: <https://rhapsody-py.readthedocs.io/>
- AsyncFlow: <https://radicalasyncflow.readthedocs.io/>
- ORBIT (remote access to RHAPSODY services): <https://radicalorbit.readthedocs.io/>

The full component list, including repositories and package links,
is on the [Components](components.md) page.

## Acknowledgment

This work is supported by the National Science Foundation under award
2514139 (collaborative award; Rutgers University, University of
Chicago, Princeton University, UC San Diego).

```{toctree}
:hidden:
:maxdepth: 2

components
examples
```
