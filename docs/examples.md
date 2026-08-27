# Integration examples

Worked examples of combining SDK components.

```{toctree}
:hidden:

Silicon phonons with QuAcc and Rootstock <quacc-rootstock-phonons/index>
Adaptive MD campaign with DeepDriveSim <ddsim-asyncflow-rhapsody/index>
```

**Materials science:** [Calculate silicon phonons with QuAcc and
Rootstock](quacc-rootstock-phonons/index.md) — compute phonon
properties of crystalline silicon with two different machine-learned
interatomic potentials.

**Molecular dynamics:** [AI-steered adaptive MD ensemble with DeepDriveSim,
AsyncFlow, and Rhapsody](ddsim-asyncflow-rhapsody/index.md) — run an ensemble
of simulations, train an ML surrogate on the fly, and cancel low-scoring runs
to free resources for new ones. Implements the full simulate → train → evaluate
→ resample loop with a concurrent backend or on HPC via Dragon.

**Bio (planned):** [Compute the kinetics of a receptor and
a ligand with Seekrflow](seekrflow-asyncflow-trypsin/index.md) - 
a biomolecular rate-constant example combining AsyncFlow and SEEKRFLOW.

