"""Energy-agnostic force evaluator for ASE Atoms.

Given any differentiable energy function E(R), report:
  - total energy
  - per-atom forces from autograd: F = -dE/dR
  - per-atom forces from central finite differences
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterator, Union

import numpy as np
import torch
from ase import Atoms

# positions (N, 3) -> scalar energy (same device/dtype as positions)
EnergyFn = Callable[[torch.Tensor], torch.Tensor]
# positions (B, N, 3) -> energies (B,) for vectorized FD when vmap is unsuitable
BatchedEnergyFn = Callable[[torch.Tensor], torch.Tensor]


class PrecisionMode(str, Enum):
    """Compute precision for position tensors / matmul backends."""

    BF16 = "BF16"
    TF32 = "TF32"
    FP32 = "FP32"
    FP64 = "FP64"


PrecisionLike = Union[PrecisionMode, str]


def _resolve_precision(precision: PrecisionLike) -> PrecisionMode:
    if isinstance(precision, PrecisionMode):
        return precision
    return PrecisionMode(str(precision).upper())


def _dtype_for_precision(precision: PrecisionMode) -> torch.dtype:
    if precision is PrecisionMode.FP64:
        return torch.float64
    if precision is PrecisionMode.BF16:
        return torch.bfloat16
    # TF32 uses FP32 tensors with TF32 Tensor-Core matmuls on CUDA.
    return torch.float32


@contextmanager
def _precision_context(precision: PrecisionMode) -> Iterator[torch.dtype]:
    """Apply dtype + CUDA TF32 flags for the chosen precision mode."""
    dtype = _dtype_for_precision(precision)
    cuda_ok = torch.cuda.is_available()
    if not cuda_ok:
        yield dtype
        return

    old_matmul = torch.backends.cuda.matmul.allow_tf32
    old_cudnn = torch.backends.cudnn.allow_tf32
    # FP32: force true FP32 matmuls; TF32: enable TF32 for FP32 ops.
    allow_tf32 = precision is PrecisionMode.TF32
    torch.backends.cuda.matmul.allow_tf32 = allow_tf32
    torch.backends.cudnn.allow_tf32 = allow_tf32
    try:
        yield dtype
    finally:
        torch.backends.cuda.matmul.allow_tf32 = old_matmul
        torch.backends.cudnn.allow_tf32 = old_cudnn


@dataclass(frozen=True)
class EvalResult:
    """Outputs of :func:`evaluate`.

    ``energy``, ``forces_ag``, and ``forces_fd`` use the selected precision
    dtype (BF16/TF32/FP32/FP64 → bfloat16/float32/float32/float64).
    """

    energy: torch.Tensor  # scalar
    forces_ag: torch.Tensor  # (N, 3)
    forces_fd: torch.Tensor  # (N, 3)
    precision: PrecisionMode

    def as_dict(self) -> dict[str, torch.Tensor | str]:
        """Flat output dict with energy and both AG/FD forces."""
        return {
            "energy": self.energy,
            "forces_ag": self.forces_ag,
            "forces_fd": self.forces_fd,
            "precision": self.precision.value,
        }

    @property
    def force_max_abs_diff(self) -> torch.Tensor:
        """Max |F_ag - F_fd| over all components (same dtype as forces)."""
        return torch.max(torch.abs(self.forces_ag - self.forces_fd))

    @property
    def force_rmse(self) -> torch.Tensor:
        """RMSE between autograd and finite-difference forces."""
        d = self.forces_ag - self.forces_fd
        return torch.sqrt(torch.mean(d * d))


def evaluate(
    atoms: Atoms,
    energy_fn: EnergyFn,
    *,
    energy_fn_batched: BatchedEnergyFn | None = None,
    device: torch.device = torch.device("cuda"),
    precision: PrecisionLike = PrecisionMode.FP64,
) -> EvalResult:
    """Evaluate energy and forces on an ASE ``Atoms`` structure.

    Parameters
    ----------
    atoms
        Structure whose Cartesian positions are evaluated. Cell / PBC / species
        are not modified here; fold any such dependence into ``energy_fn``.
    energy_fn
        Callable ``positions -> energy`` where ``positions`` is an ``(N, 3)``
        tensor (requires grad for the autograd path) and the return value is a
        scalar tensor. Must be differentiable w.r.t. ``positions``.
    energy_fn_batched
        Optional ``(B, N, 3) -> (B,)`` energy for vectorized FD. Use this when
        ``energy_fn`` is not ``torch.vmap``-compatible (e.g. FairChem UMA).
    device
        Device used to build the position tensor passed to ``energy_fn``.
    precision
        One of ``BF16``, ``TF32``, ``FP32``, ``FP64``. Sets dtype for positions,
        energy, and forces; on CUDA also sets TF32 matmul flags (on for TF32,
        off for FP32).

    Returns
    -------
    EvalResult
        ``energy``, ``forces_ag``, and ``forces_fd`` in the selected dtype.
    """
    mode = _resolve_precision(precision)
    pos_np = np.asarray(atoms.get_positions(), dtype=np.float64)

    with _precision_context(mode) as dtype:
        energy, forces_ag = _autograd_energy_forces(
            pos_np, energy_fn, device=device, dtype=dtype
        )
        forces_fd = _finite_diff_forces(
            pos_np,
            energy_fn,
            energy_fn_batched=energy_fn_batched,
            device=device,
            dtype=dtype,
        )

    return EvalResult(
        energy=energy,
        forces_ag=forces_ag,
        forces_fd=forces_fd,
        precision=mode,
    )


def _as_scalar_energy(energy: torch.Tensor) -> torch.Tensor:
    if energy.ndim != 0:
        energy = energy.squeeze()
    if energy.ndim != 0:
        raise ValueError(
            f"energy_fn must return a scalar tensor, got shape {tuple(energy.shape)}"
        )
    return energy


def _autograd_energy_forces(
    positions: np.ndarray,
    energy_fn: EnergyFn,
    *,
    device: torch.device,
    dtype: torch.dtype,
) -> tuple[torch.Tensor, torch.Tensor]:
    pos = torch.tensor(positions, device=device, dtype=dtype, requires_grad=True)
    energy = _as_scalar_energy(energy_fn(pos))
    # Keep output energy in the selected precision dtype.
    energy = energy.to(dtype=dtype)

    (grad,) = torch.autograd.grad(energy, pos, create_graph=False)
    forces = (-grad).detach().to(dtype=dtype)
    return energy.detach(), forces


def _finite_diff_forces(
    positions: np.ndarray,
    energy_fn: EnergyFn,
    *,
    energy_fn_batched: BatchedEnergyFn | None = None,
    device: torch.device,
    dtype: torch.dtype,
) -> torch.Tensor:
    """Central difference: F_iα = -(E(R+h e_iα) - E(R-h e_iα)) / (2h).

    Displacements are built with on-device broadcast (no atom/coord Python
    loops). Energies use ``energy_fn_batched`` when provided, otherwise
    ``torch.vmap(energy_fn)``.
    """
    # Step size in the same length units as positions (typically Å).
    _delta = 1e-4

    pos0 = torch.tensor(positions, device=device, dtype=dtype)  # (N, 3)
    n_atoms = pos0.shape[0]
    h = torch.as_tensor(_delta, device=device, dtype=dtype)

    # offsets[i, a, j, b] = h * δ_ij * δ_ab  →  shape (N, 3, N, 3)
    eye_n = torch.eye(n_atoms, device=device, dtype=dtype)
    eye_3 = torch.eye(3, device=device, dtype=dtype)
    offsets = h * eye_n[:, None, :, None] * eye_3[None, :, None, :]

    base = pos0[None, None, :, :]
    pos_plus = (base + offsets).reshape(n_atoms * 3, n_atoms, 3)
    pos_minus = (base - offsets).reshape(n_atoms * 3, n_atoms, 3)

    with torch.no_grad():
        if energy_fn_batched is not None:
            e_plus = energy_fn_batched(pos_plus).to(dtype=dtype)
            e_minus = energy_fn_batched(pos_minus).to(dtype=dtype)
        else:

            def _e(pos: torch.Tensor) -> torch.Tensor:
                return _as_scalar_energy(energy_fn(pos)).to(dtype=dtype)

            e_plus = torch.vmap(_e)(pos_plus)
            e_minus = torch.vmap(_e)(pos_minus)

        forces = -(e_plus - e_minus).reshape(n_atoms, 3) / (h + h)

    return forces


def wrap_ase_calculator(atoms_template: Atoms) -> EnergyFn:
    """Build an ``energy_fn`` from ``atoms_template.calc`` (no autograd).

    Useful only for the finite-difference path, or as a reference energy.
    Autograd through this wrapper will fail unless the calculator itself is
    torch-differentiable and wired into the graph.
    """
    if atoms_template.calc is None:
        raise ValueError("atoms_template.calc is None")

    def energy_fn(positions: torch.Tensor) -> torch.Tensor:
        work = atoms_template.copy()
        work.calc = atoms_template.calc
        work.set_positions(positions.detach().cpu().numpy())
        e = work.get_potential_energy()
        return positions.new_tensor(float(e))

    return energy_fn


if __name__ == "__main__":
    import sys
    from pathlib import Path

    from ase.io import read

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fairchem-uma"))
    from infer_energy_forces import load_uma_calculator, make_uma_energy_fns

    structure = (
        Path(__file__).resolve().parent
        / "structures"
        / "molecules"
        / "H2O.extxyz"
    )
    atoms = read(str(structure))
    calc = load_uma_calculator(atoms)
    energy_fn, energy_fn_batched = make_uma_energy_fns(atoms, calc)

    for mode in PrecisionMode:
        result = evaluate(
            atoms,
            energy_fn,
            energy_fn_batched=energy_fn_batched,
            precision=mode,
        )
        out = result.as_dict()
        print(f"=== UMA {out['precision']} ({out['energy'].dtype}) ===")
        print(f"energy    = {out['energy'].item()}")
        print(f"forces_ag =\n{out['forces_ag']}")
        print(f"forces_fd =\n{out['forces_fd']}")
        print(f"max |ΔF|  = {result.force_max_abs_diff.item():.3e}")
        print(f"RMSE(F)   = {result.force_rmse.item():.3e}")
        print()
