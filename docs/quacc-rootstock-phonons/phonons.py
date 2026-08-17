"""Comparing how two MLIPs compute phonons of silicon using QuAcc + Rootstock."""

import json

from ase.build import bulk

from quacc.recipes.mlip.core import relax_job
from quacc.recipes.mlip.phonons import phonon_flow

# -- 1. Specify the cluster you're running on and the models to compare --
CLUSTER = "perlmutter"
CHECKPOINTS = {
    "mace-mh-1": {"head": "omat_pbe"},
    "orb-v3-conservative-inf-omat": {"precision": "float64"},
}

# -- 2. Build the structure ----------------------------------------------
atoms = bulk("Si")  # crystalline silicon

summary = {}
for checkpoint, setup_kwargs in CHECKPOINTS.items():
    # The "library" parameter tells QuAcc to use Rootstock.
    # The other parameters are passed to the Rootstock ASE calculator
    #   to load the right MLIP.
    common = {
        "library": "rootstock",
        "cluster": CLUSTER,
        "checkpoint": checkpoint,
        "device": "cuda",
        "setup_kwargs": setup_kwargs,
    }

    # -- 3. Make sure the structure is tightly relaxed before running phonons ----
    relaxed = relax_job(
        atoms, relax_cell=True, opt_params={"fmax": 1e-3}, **common
    )

    # -- 4. Use QuAcc's phonon flow, which calls phonopy -------
    phonons = phonon_flow(
        relaxed["atoms"],
        job_params={"static_job": common},
    )

    # -- 5. Prepare data for visualization -----------
    dos = phonons["results"]["total_dos"]
    thermal = phonons["results"]["thermal_properties"]
    summary[checkpoint] = {
        "dos_frequency_THz": dos["frequency_points"].tolist(),
        "dos": dos["total_dos"].tolist(),
        "temperature_K": thermal["temperatures"].tolist(),
        "heat_capacity_J_per_molK": thermal["heat_capacity"].tolist(),
        "free_energy_kJ_per_mol": thermal["free_energy"].tolist(),
    }
    print(f"{checkpoint}: done")

with open("phonon_summary.json", "w") as f:
    json.dump(summary, f)
print("Wrote phonon_summary.json")