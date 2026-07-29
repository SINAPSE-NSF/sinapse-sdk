#!/usr/bin/env bash
set -euo pipefail
source /home/xyan11/miniforge3/etc/profile.d/conda.sh
conda activate uma312
exec python "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/infer_energy_forces.py"
