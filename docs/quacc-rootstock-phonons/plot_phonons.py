"""Plot the phonon comparison in phonon_summary.json against experiment."""

import json

import matplotlib.pyplot as plt

with open("phonon_summary.json") as f:
    summary = json.load(f)

# Experimental reference points. Frequency: the transverse-acoustic
# zone-boundary phonon from inelastic neutron scattering (Nilsson & Nelin,
# Phys. Rev. B 6, 3777 (1972), https://doi.org/10.1103/PhysRevB.6.3777).
# Heat capacity: NIST-JANAF values for crystalline Si
# (https://janaf.nist.gov/tables/Si-002.html), tabulated per mole of
# atoms (C_p, near-identical to C_V except at high temperature, where
# thermal expansion pushes it up).
EXP_FREQS_THZ = {"TA(X)": 4.49}
JANAF_T_K = [100, 200, 298.15, 400, 500, 600, 800, 1000]
JANAF_CP_PER_MOL_ATOMS = [7.268, 15.636, 20.000, 22.142, 23.330, 24.154,
                          25.359, 26.338]

COLORS = ["#2a78d6", "#eb6834", "#1baf7a"]  # colorblind-safe triple
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e1e0d9"

fig, (ax_dos, ax_cv) = plt.subplots(1, 2, figsize=(9.5, 3.8), dpi=200)

for color, (name, data) in zip(COLORS, summary.items()):
    ax_dos.plot(data["dos_frequency_THz"], data["dos"],
                color=color, lw=2, label=name)
    ax_cv.plot(data["temperature_K"], data["heat_capacity_J_per_molK"],
               color=color, lw=2, label=name)

# At high temperature every simple solid stores ~25 J/mol/K of heat per
# mole of atoms (the Dulong-Petit law): 3 vibration directions x the gas
# constant. phonopy reports per mole of cells, and our cell has 2 atoms.
GAS_CONSTANT = 8.314  # J/(mol K)
ATOMS_PER_CELL = 2    # bulk("Si") in the workflow script
dulong_petit = 3 * ATOMS_PER_CELL * GAS_CONSTANT
ax_cv.axhline(dulong_petit, color=MUTED, lw=1, ls=(0, (4, 4)))
ax_cv.text(0.98, dulong_petit, "Dulong–Petit  ", color=MUTED,
           fontsize=8, ha="right", va="bottom",
           transform=ax_cv.get_yaxis_transform())

# Experimental markers: dotted lines on the DOS, open circles on C_V.
for label, freq in EXP_FREQS_THZ.items():
    ax_dos.axvline(freq, color=MUTED, lw=1, ls=(0, (2, 3)))
    ax_dos.text(freq, 0.97, f"{label} ", color=MUTED, fontsize=8,
                ha="right", va="top", rotation=90,
                transform=ax_dos.get_xaxis_transform())
ax_cv.scatter(JANAF_T_K,
              [ATOMS_PER_CELL * cp for cp in JANAF_CP_PER_MOL_ATOMS],
              s=18, facecolors="none", edgecolors=INK, lw=1,
              zorder=3, label="experimental values")

ax_dos.set_xlabel("Frequency (THz)", color=MUTED)
ax_dos.set_ylabel("Phonon DOS (states/THz)", color=MUTED)
ax_dos.set_title("Si phonon density of states", color=INK, fontsize=10)
ax_cv.set_xlabel("Temperature (K)", color=MUTED)
ax_cv.set_ylabel("$C_V$ (J mol$^{-1}$ K$^{-1}$)", color=MUTED)
ax_cv.set_title("Heat capacity", color=INK, fontsize=10)
# One legend for both panels, in the heat-capacity panel's empty corner.
ax_cv.legend(frameon=False, fontsize=8, loc="lower right")

for ax in (ax_dos, ax_cv):
    ax.grid(color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=MUTED, labelsize=8)

fig.tight_layout()
fig.savefig("phonon_comparison.png", bbox_inches="tight")
print("Wrote phonon_comparison.png")
