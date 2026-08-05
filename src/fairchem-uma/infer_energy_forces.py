#!/usr/bin/env python3
"""UMA energy/force helpers and batch inference over demo structures.

Provides:
  - ``load_uma_calculator`` / ``make_uma_energy_fns`` for the numerical-stability
    evaluator (autograd-safe energy-only forward + batched FD energies)
  - ``main()`` CLI that reports energy/forces for all demo ``.extxyz`` files
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Callable, Iterator

import numpy as np
import torch
from ase import Atoms
from ase.io import read
from fairchem.core import FAIRChemCalculator
from fairchem.core.datasets.atomic_data import AtomicData, atomicdata_list_to_batch
from fairchem.core.units.mlip_unit import load_predict_unit
from fairchem.core.units.mlip_unit.api.inference import InferenceSettings

EnergyFn = Callable[[torch.Tensor], torch.Tensor]
BatchedEnergyFn = Callable[[torch.Tensor], torch.Tensor]

STRUCTURES = (
    Path(__file__).resolve().parent.parent
    / "numerical-stability-test"
    / "structures"
)
CHECKPOINT = Path("/mnt/d/workdir/uma-cache/uma-s-1p2.pt")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Portable backend for older GPUs (e.g. Titan V / Volta).
SETTINGS = InferenceSettings(execution_mode="general")


def load_uma_calculator(
    atoms: Atoms,
    *,
    checkpoint: str | Path = CHECKPOINT,
    device: str = DEVICE,
    task_name: str | None = None,
) -> FAIRChemCalculator:
    """Load UMA predict unit and return a FAIRChemCalculator for ``atoms``."""
    atoms.info.setdefault("charge", 0)
    atoms.info.setdefault("spin", 1)
    if task_name is None:
        task_name = "omat" if atoms.pbc.any() else "omol"

    predictor = load_predict_unit(
        str(checkpoint), inference_settings=SETTINGS, device=device
    )
    calc = FAIRChemCalculator(predictor, task_name=task_name)
    # Warm up lazy init / kernels.
    predictor.predict(calc.a2g(atoms))
    return calc


def make_uma_energy_fns(
    atoms: Atoms,
    calc: FAIRChemCalculator,
) -> tuple[EnergyFn, BatchedEnergyFn]:
    """Build single and batched UMA energy callables bound to ``atoms``/``calc``.

    UMA's full ``predict()`` path runs force autograd internally and frees the
    graph, so these helpers disable force/stress heads and return denormalized
    energy only.
    """
    predictor = calc.predictor
    task_name = calc.task_name
    energy_task = predictor.model.module.tasks[f"{task_name}_energy"]
    efs_head = _efs_head(predictor)
    device = torch.device(predictor.device)
    model_dtype = predictor.inference_settings.base_precision_dtype

    def energy_fn(positions: torch.Tensor) -> torch.Tensor:
        data = _materialize_data(calc, atoms, device=device, dtype=model_dtype)
        data.pos = positions.to(device=device, dtype=model_dtype)
        return _forward_energy(
            predictor, data, energy_task, efs_head, undo_refs=True
        ).reshape(())

    def energy_fn_batched(positions_batch: torch.Tensor) -> torch.Tensor:
        # positions_batch: (B, N, 3)
        pos_b = positions_batch.to(device=device, dtype=model_dtype)
        data_list = [
            _with_positions(
                _materialize_data(calc, atoms, device=device, dtype=model_dtype),
                pos_b[i],
            )
            for i in range(pos_b.shape[0])
        ]
        batch = atomicdata_list_to_batch(data_list)
        return _forward_energy(
            predictor, batch, energy_task, efs_head, undo_refs=True
        ).reshape(-1)

    return energy_fn, energy_fn_batched


def _efs_head(predictor):
    head = predictor.model.module.output_heads["energyandforcehead"]
    return head.head if hasattr(head, "head") else head


@contextmanager
def _energy_only(efs_head) -> Iterator[None]:
    rc = efs_head.regress_config
    old = (rc.forces, rc.stress)
    rc.forces = False
    rc.stress = False
    try:
        yield
    finally:
        rc.forces, rc.stress = old


def _materialize_data(
    calc: FAIRChemCalculator,
    atoms: Atoms,
    *,
    device: torch.device,
    dtype: torch.dtype,
) -> AtomicData:
    data = calc.a2g(atoms).to(device).clone()
    for key, val in data:
        if torch.is_tensor(val) and val.is_floating_point():
            data[key] = val.to(dtype=dtype)
    return data


def _with_positions(data: AtomicData, positions: torch.Tensor) -> AtomicData:
    data.pos = positions
    return data


def _forward_energy(predictor, data: AtomicData, energy_task, efs_head, *, undo_refs: bool):
    if not predictor.lazy_model_intialized:
        predictor._lazy_init(data)

    data_device = data.to(predictor.device)
    predictor.model.module.on_predict_check(data_device)

    with _energy_only(efs_head):
        output = predictor.model(data_device)

    raw = output[energy_task.name][energy_task.property]
    energy = energy_task.normalizer.denorm(raw)
    if undo_refs and energy_task.element_references is not None:
        energy = energy_task.element_references.undo_refs(data_device, energy)
    return energy


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
