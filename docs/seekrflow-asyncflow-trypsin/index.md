# Protein-ligand binding kinetics setup with Seekrflow and Asyncflow

In this example, we will prepare, run, and analyze calculations to predict
binding and unbinding kinetics for a host-guest system - a common
benchmark system for computational methods to predict biomolecular
interactions.

We will use two SINAPSE SDK components:

- **[Seekrflow](https://github.com/seekrcentral/seekrflow)** performs the calculations that will predict the kinetics.
- **[Asyncflow](https://github.com/radical-cybertools/radical.asyncflow)** an asynchronous workflow layer for Seekrflow pipeline.

## Prerequisites

These calculations will run on your local Linux machine, although additional 
configuration can allow running on remote compute resources.

## Install

The easiest, quickest way to install seekrflow is to use Mamba. If you don't already have
Mamba installed, Download the Miniforge install script and run.

```sh
curl -O https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh
bash Miniforge3-$(uname)-$(uname -m).sh
```

Once this has been done, set up a new environment:

```sh
mamba create -n SEEKR python=3.12 --yes
```

This step installs seekrflow from github.
```sh
mamba activate SEEKR
git clone https://github.com/seekrcentral/seekrflow.git
cd seekrflow
python -m pip install .
```

Next, install seekr:

```sh
mamba install seekr
```

One will also need to install OpenMM:

```sh
mamba install openmm
```

You may wish to specify the cuda version for your pre-installed version.

```
mamba install openmm cuda-nvrtc=##.# cuda-version=##.#
```

Where, of course, you replace the '##.#' with whatever Cuda version you have
installed, found using `nvidia-smi` or other such program.

Next, find the host-guest example directory and run the example:

```sh
seekrflow/seekrflow/examples/host_guest
python ~/seekrflow/seekrflow/flow.py prepare -i seekrflow_1_butanol_local.json
python ~/seekrflow/seekrflow/flow.py run -i seekrflow_1_butanol_local.json
python ~/seekr/seekr/analyze.py work/root/model.json
```

You will see the analysis printed to the screen. If you're curious, the 
experimentally-measured k-off for this compound is 3.8e8 1/s. This calculation 
is artificially truncated for demonstration purposes - a true seekr 
calculation should simulate much longer. The generated images can be 
seen in ~/test_seekr/images_and_plots.


