"""Exact closed forms from continuum equilibrium and constitutive laws.

This route never imports the assembled solver or a selection policy.
Inputs are rational SI quantities; return values are rational SI quantities.
"""
from fractions import Fraction as F


def parameters(case):
    p = {key: F(value) for key, value in case["parameters"].items()}
    positive = [k for k in p if not k.endswith("temperature_K") and k != "line_load_N_per_m"]
    if any(p[k] <= 0 for k in positive):
        raise ValueError("geometry and material coefficients must be positive")
    if any(v < 0 for k, v in p.items() if k.endswith("temperature_K")):
        raise ValueError("absolute temperatures must be nonnegative")
    return p


def beam(p):
    length, width, height = p["length_m"], p["width_m"], p["height_m"]
    inertia = width * height**3 / 12
    q, rigidity = p["line_load_N_per_m"], p["modulus_Pa"] * inertia
    return {"tip_deflection": q * length**4 / (8 * rigidity),
            "root_stress": abs(q) * length**2 * height / (4 * inertia),
            "support_force": -q * length,
            "support_moment": -q * length**2 / 2}


def slab(p):
    left, right = p["left_temperature_K"], p["right_temperature_K"]
    return {"midpoint_temperature": (left + right) / 2,
            "heat_flux": p["conductivity_W_per_m_K"] * (left - right) / p["length_m"]}


def solve(case):
    return {"beam_bending": beam, "steady_heat_conduction": slab}[case["family"]](parameters(case))
