"""Small independent checks for the reconciled VM92 and cylinder findings.

Uses specification inputs and retained results as data, but imports no study
reference or solver. Run from the repository root:
python3 reports/reference-admission/review_repro.py
"""

import json
import math
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
spec = json.loads((ROOT / "studies/reference_qualification/spec.json").read_text())
results = json.loads((ROOT / "reports/reference-qualification/results.json").read_text())


def case(items, identifier):
    return next(item for item in items if item["id"] == identifier)


wall = case(spec["cases"], "vm92_layered_wall")
w = {key: F(value) for key, value in wall["parameters"].items()}
resistance = (
    1 / w["inner_h_Btu_per_hr_ft2_F"]
    + w["layer1_ft"] / w["k1_Btu_per_hr_ft_F"]
    + w["layer2_ft"] / w["k2_Btu_per_hr_ft_F"]
    + 1 / w["outer_h_Btu_per_hr_ft2_F"]
) / w["area_ft2"]
heat_rate = (w["hot_temperature_F"] - w["ambient_temperature_F"]) / resistance
outer = w["ambient_temperature_F"] + heat_rate / (
    w["outer_h_Btu_per_hr_ft2_F"] * w["area_ft2"]
)
display = next(
    F(target["displayed"])
    for target in wall["published_evidence"]["targets"]
    if target["observable"] == "outer_surface_temperature"
)
display_unit = next(
    F(target["display_unit"])
    for target in wall["published_evidence"]["targets"]
    if target["observable"] == "outer_surface_temperature"
)

cylinder = case(spec["cases"], "vm25_pressure_only")
p = {key: F(value) for key, value in cylinder["parameters"].items()}
a, b = p["inner_radius_in"], p["outer_radius_in"]
pi, po = p["internal_pressure_psi"], p["external_pressure_psi"]
A = (pi * a * a - po * b * b) / (b * b - a * a)
B = (pi - po) * a * a * b * b / (b * b - a * a)
steps = cylinder["qualification"]["steps"][0]
h = (b - a) / steps
hoop = [float(A + B / (a + j * h) ** 2) for j in range(steps + 1)]
trapezoid = float(h) * (
    math.fsum(hoop) - (hoop[0] + hoop[-1]) / 2
)
analytic_integral = A * (b - a) + B * (1 / a - 1 / b)
exact_field_residual = float(analytic_integral) - trapezoid
retained = case(results["cases"], "vm25_pressure_only")
nominal = next(c for c in retained["controls"] if c["control"] == "nominal")
rk4_residual = nominal["cross_checks"][0]["diagnostics"][
    "integrated_equilibrium_residual_psi_in"
]

print(json.dumps({
    "vm92_outer": {
        "exact_fraction_degF": str(outer),
        "displayed_degF": str(display),
        "outside_nearest_display_interval": abs(outer - display) > display_unit / 2,
    },
    "vm25_nominal_trapezoid": {
        "steps": steps,
        "exact_field_residual_psi_in": exact_field_residual,
        "retained_rk4_residual_psi_in": rk4_residual,
    },
}, indent=2))
