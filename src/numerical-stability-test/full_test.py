#!/usr/bin/env python3
"""FP64 UMA numerical-stability sweep over all demo structures.

For each structure under ``structures/``, run the energy-agnostic evaluator
with the FairChem UMA calculator and report energy plus AG/FD per-atom forces.
"""

from __future__ import annotations

import sys
from pathlib import Path

from ase.io import read
from fairchem.core import FAIRChemCalculator
from fairchem.core.units.mlip_unit import load_predict_unit

from evaluator import PrecisionMode, evaluate

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fairchem-uma"))
from infer_energy_forces import (  # noqa: E402
    CHECKPOINT,
    DEVICE,
    SETTINGS,
    make_uma_energy_fns,
)

STRUCTURES = Path(__file__).resolve().parent / "structures"
PRECISION = PrecisionMode.FP64

# UMA task name per structure (path relative to STRUCTURES).
# molecules → omol; crystals → omat.
TASK_BY_STRUCTURE: dict[str, str] = {
    # molecules
    "molecules/CH4.extxyz": "omol",
    "molecules/CO.extxyz": "omol",
    "molecules/H2.extxyz": "omol",
    "molecules/H2O.extxyz": "omol",
    "molecules/HF.extxyz": "omol",
    "molecules/LiH.extxyz": "omol",
    "molecules/NH3.extxyz": "omol",
    "molecules/SiH4.extxyz": "omol",
    # crystals
    "crystals/Al2O3_corundum.extxyz": "omat",
    "crystals/AlN_wurtzite.extxyz": "omat",
    "crystals/AlP.extxyz": "omat",
    "crystals/Al_fcc.extxyz": "omat",
    "crystals/BN_zincblende.extxyz": "omat",
    "crystals/C_diamond.extxyz": "omat",
    "crystals/CaF2_fluorite.extxyz": "omat",
    "crystals/Cu2O_cuprite.extxyz": "omat",
    "crystals/CuCl_zincblende.extxyz": "omat",
    "crystals/Cu_fcc.extxyz": "omat",
    "crystals/FeS2_pyrite.extxyz": "omat",
    "crystals/Fe_bcc.extxyz": "omat",
    "crystals/GaAs.extxyz": "omat",
    "crystals/Ge.extxyz": "omat",
    "crystals/LiF.extxyz": "omat",
    "crystals/LiFePO4_olivine.extxyz": "omat",
    "crystals/LiMn2O4_spinel.extxyz": "omat",
    "crystals/LiPF6.extxyz": "omat",
    "crystals/MgO.extxyz": "omat",
    "crystals/MoS2_2H.extxyz": "omat",
    "crystals/NaCl.extxyz": "omat",
    "crystals/NiO_rocksalt.extxyz": "omat",
    "crystals/Ni_fcc.extxyz": "omat",
    "crystals/ScN.extxyz": "omat",
    "crystals/Si.extxyz": "omat",
    "crystals/SiC.extxyz": "omat",
    "crystals/TiO2_rutile.extxyz": "omat",
    "crystals/Ti_hcp.extxyz": "omat",
    "crystals/ZnO_wurtzite.extxyz": "omat",
    "crystals/ZnS_zincblende.extxyz": "omat",
    "crystals/Zn_hcp.extxyz": "omat",
    "crystals/graphite.extxyz": "omat",
    "crystals/hBN.extxyz": "omat",
}


def _task_for(rel: str) -> str:
    if rel in TASK_BY_STRUCTURE:
        return TASK_BY_STRUCTURE[rel]
    # Fallback if a new file appears before the dict is updated.
    return "omat" if rel.startswith("crystals/") else "omol"


def main() -> None:
    paths = sorted(STRUCTURES.rglob("*.extxyz"))
    print(f"checkpoint : {CHECKPOINT}")
    print(f"device     : {DEVICE}")
    print(f"precision  : {PRECISION.value}")
    print(f"structures : {len(paths)}\n")

    predictor = load_predict_unit(
        str(CHECKPOINT), inference_settings=SETTINGS, device=DEVICE
    )

    for path in paths:
        rel = path.relative_to(STRUCTURES).as_posix()
        task = _task_for(rel)
        atoms = read(str(path))
        atoms.info.setdefault("charge", 0)
        atoms.info.setdefault("spin", 1)

        calc = FAIRChemCalculator(predictor, task_name=task)
        energy_fn, energy_fn_batched = make_uma_energy_fns(atoms, calc)

        result = evaluate(
            atoms,
            energy_fn,
            energy_fn_batched=energy_fn_batched,
            precision=PRECISION,
        )
        out = result.as_dict()

        print(f"[{task}] {rel}")
        print(f"  natoms     = {len(atoms)}")
        print(f"  energy     = {out['energy'].item():.10f} eV")
        print(f"  forces_ag  =\n{out['forces_ag']}")
        print(f"  forces_fd  =\n{out['forces_fd']}")
        print(f"  max |ΔF|   = {result.force_max_abs_diff.item():.6e}")
        print(f"  RMSE(F)    = {result.force_rmse.item():.6e}")
        print()


if __name__ == "__main__":
    main()
