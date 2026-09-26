"""Pure-NumPy Gupta (RGL) potential as an ASE calculator.

Drop-in replacement for asap3.Internal.BuiltinPotentials.Gupta for
single-element, non-periodic clusters, so it runs in Pyodide/JupyterLite.
Parameters use the same convention as ASAP: {symbol: [p, q, A, xi, r0]}.

E = sum_i [ sum_{j!=i} A exp(-p (r_ij/r0 - 1))
            - sqrt( sum_{j!=i} xi^2 exp(-2 q (r_ij/r0 - 1)) ) ]
"""
import numpy as np
from ase.calculators.calculator import Calculator, all_changes


class Gupta(Calculator):
    implemented_properties = ["energy", "forces"]

    def __init__(self, parameters, cutoff=None, debug=False, **kwargs):
        Calculator.__init__(self, **kwargs)
        if len(parameters) != 1:
            raise NotImplementedError("Only single-element Gupta is implemented.")
        (self.symbol, (self.p, self.q, self.A, self.xi, self.r0)), = parameters.items()
        self.cutoff = cutoff  # None or large value = no cutoff

    def calculate(self, atoms=None, properties=("energy",), system_changes=all_changes):
        Calculator.calculate(self, atoms, properties, system_changes)
        if any(atoms.pbc):
            raise NotImplementedError("Periodic systems are not supported.")
        if set(atoms.get_chemical_symbols()) != {self.symbol}:
            raise ValueError("All atoms must be " + self.symbol)
        p, q, A, xi, r0 = self.p, self.q, self.A, self.xi, self.r0
        pos = atoms.positions
        n = len(pos)
        vec = pos[:, None, :] - pos[None, :, :]          # r_i - r_j
        r = np.linalg.norm(vec, axis=2)
        np.fill_diagonal(r, np.inf)
        mask = np.isfinite(r)
        if self.cutoff is not None:
            mask &= r < self.cutoff
        d = np.where(mask, r / r0 - 1.0, 0.0)
        rep = np.where(mask, A * np.exp(-p * d), 0.0)
        att = np.where(mask, xi**2 * np.exp(-2.0 * q * d), 0.0)
        rho = att.sum(axis=1)
        sqrt_rho = np.sqrt(rho)
        energy = rep.sum() - sqrt_rho.sum()
        # dE/dr_ij for each ordered pair (symmetric matrix)
        inv = np.where(sqrt_rho > 0, 0.5 / sqrt_rho, 0.0)
        dE_dr = 2.0 * (-p / r0) * rep + (inv[:, None] + inv[None, :]) * (2.0 * q / r0) * att
        with np.errstate(invalid="ignore", divide="ignore"):
            unit = np.where(mask[:, :, None], vec / r[:, :, None], 0.0)
        forces = -(dE_dr[:, :, None] * unit).sum(axis=1)
        self.results = {"energy": energy, "forces": forces}
