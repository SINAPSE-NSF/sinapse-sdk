# fairchem-uma

Run UMA energy and force inference on all `.extxyz` files under
`../numerical-stability-test/structures`.

## Tracked files (this demo)

| Path | Role |
|------|------|
| `infer_energy_forces.py` | UMA inference CLI + `load_uma_calculator` / `make_uma_energy_fns` for the numerical-stability evaluator |
| `run_infer.sh` | Activates `uma312` and runs the script |
| `README.md` | This file |
| `../numerical-stability-test/structures/molecules/*.extxyz` | Molecule demo structures (`omol`) |
| `../numerical-stability-test/structures/crystals/*.extxyz` | Crystal demo structures (`omat`) |

## Needed to run (not in this repo)

| Dependency | Notes |
|------------|--------|
| conda env `uma312` | `fairchem-core`, ASE, PyTorch + CUDA |
| `/mnt/d/workdir/uma-cache/uma-s-1p2.pt` | UMA small checkpoint used by the script |
| NVIDIA GPU (optional) | CUDA if available; otherwise CPU |

## Setup

```bash
source /home/xyan11/miniforge3/etc/profile.d/conda.sh
conda activate uma312
```

Task is chosen from PBC: periodic → `omat`, non-periodic → `omol`.

## Run

```bash
python infer_energy_forces.py
# or
./run_infer.sh
```
