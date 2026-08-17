# Compare how different machine-learned interatomic potentials calculate silicon phonons with QuAcc and Rootstock

This example runs a materials science workflow with two different machine-learned interatomic potentials (MLIPs).
We calculate phonon properties of crystalline silicon with the two MLIPs and see how they compare to each other and to experimental results.

We will use two SINAPSE SDK components:

- **[QuAcc](https://quantum-accelerators.github.io/quacc/)** provides the components of the computational materials science workflow.
- **[Rootstock](https://github.com/Garden-AI/rootstock)** provides the MLIPs that QuAcc will use at calculation time.

## Prerequisites

You need an account on a cluster with a Rootstock installation. Check the [Matter Model Almanac](https://garden-ai.github.io/almanac/) to see which are currently supported. The example will also assume that your allocation includes access to GPU time.

In a virtual environment, install the following packages:

```console
$ pip install "quacc[phonons]" rootstock matplotlib
```

Note that you do not need to install PyTorch or individual MLIP packages because Rootstock manages pre-installed model environments on the cluster.

## The phonon calculation workflow

This workflow takes a few minutes to run on a GPU node. Change `CLUSTER` to be the cluster you are running on, and double-check the [Almanac](https://garden-ai.github.io/almanac/) to confirm the MLIPs you are using are available on your cluster.

```{literalinclude} phonons.py
:language: python
```

## Plot the comparison

With the output in `phonon_summary.json`, we can plot the phonon density of states and constant-volume heat capacity obtained with each MLIP.
We also overlay experimental measurements from the literature for reference.

`````{dropdown} plot_phonons.py — click to expand
````{literalinclude} plot_phonons.py
:language: python
````
`````

## Results

![Phonon density of states and heat capacity of silicon computed with
mace-mh-1 and orb-v3-conservative-inf-omat, with experimental reference
values](phonon_comparison.png)

*Experimental data: TA(X) phonon frequency from inelastic neutron
scattering ([Nilsson & Nelin, Phys. Rev. B 6, 3777
(1972)](https://doi.org/10.1103/PhysRevB.6.3777)); heat capacities of
crystalline Si from the [NIST-JANAF Thermochemical
Tables](https://janaf.nist.gov/tables/Si-002.html) (Chase, 1998).*

Both models reproduce the shape of the measured silicon spectrum, and the heat-capacity curves roughly track the [NIST-JANAF](https://janaf.nist.gov/tables/Si-002.html) measurements.

The models line up very closely on heat capacity, but have some noteworthy disagreement in the density of states. In particular, MACE-MH-1 (with the omat_pbe task head activated) places the transverse-acoustic peak at ~4.6 THz and Orb places it at ~4.2 THz, overshooting and undershooting the neutron-measured 4.5 THz respectively. This demonstrates that even when different MLIPs closely agree on some properties, they can disagree on zero-point vibrational energies in a way that would affect follow-on calculations of free energies.