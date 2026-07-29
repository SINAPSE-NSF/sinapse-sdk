#!/usr/bin/env python3
"""UMA energy/force inference on all .extxyz under sinapse_sdk/structures."""

from pathlib import Path

import numpy as np
import torch
from ase.io import read
from fairchem.core import FAIRChemCalculator
from fairchem.core.units.mlip_unit import load_predict_unit
from fairchem.core.units.mlip_unit.api.inference import InferenceSettings

STRUCTURES = Path(__file__).resolve().parent.parent / "sinapse_sdk" / "structures"
CHECKPOINT = Path("/mnt/d/workdir/uma-cache/uma-s-1p2.pt")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Portable backend for older GPUs (e.g. Titan V / Volta).
SETTINGS = InferenceSettings(execution_mode="general")


def main() -> None:
    paths = sorted(STRUCTURES.rglob("*.extxyz"))
    print(f"checkpoint : {CHECKPOINT}")
    print(f"device     : {DEVICE}")
    print(f"structures : {len(paths)}\n")

    predictor = load_predict_unit(
        str(CHECKPOINT), inference_settings=SETTINGS, device=DEVICE
    )

    for path in paths:
        atoms = read(str(path))
        # Periodic cells use omat; non-periodic molecules use omol.
        task = "omat" if atoms.pbc.any() else "omol"
        atoms.info.setdefault("charge", 0)
        atoms.info.setdefault("spin", 1)
        atoms.calc = FAIRChemCalculator(predictor, task_name=task)

        energy = atoms.get_potential_energy()
        forces = atoms.get_forces()
        fmax = float(np.max(np.linalg.norm(forces, axis=1)))

        print(f"[{task}] {path.relative_to(STRUCTURES)}")
        print(f"  energy = {energy:.8f} eV")
        print(f"  fmax   = {fmax:.6f} eV/Å")
        print()


if __name__ == "__main__":
    main()
