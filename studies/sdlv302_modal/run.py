"""Reproduce the prospectively specified first-mode analytical reference."""

import hashlib
import json
from pathlib import Path

from .reference import (axial_control_hz, energy_matrix_hz,
                        euler_bernoulli_limit_hz, source_formula_hz)

ROOT = Path(__file__).resolve().parents[2]
SPEC = Path(__file__).with_name("spec.json")
OUTPUT = ROOT / "reports" / "sdlv302-modal" / "results.json"


def build() -> dict:
    raw = SPEC.read_bytes()
    spec = json.loads(raw)
    p = spec["geometry_and_material"]
    L, h, width = p["L_m"], p["h_m"], p["b_m"]
    E, nu, rho = p["E_Pa"], p["nu"], p["rho_kg_per_m3"]
    A, I, G = width*h, width*h**3/12, E/(2*(1+nu))
    shear_factor = 5/6
    rows = []
    for n in range(1, 5):
        args = (n, L, A, I, E, G, rho, shear_factor)
        source = source_formula_hz(*args)
        energy, residual = energy_matrix_hz(*args)
        rows.append({"flexural_n": n, "source_expression_Hz": source,
                     "independent_energy_matrix_Hz": energy,
                     "route_difference_Hz": abs(source-energy),
                     "eigen_residual_relative": residual})
    first = rows[0]
    lo, hi = spec["claim"]["published_display_interval_Hz"]
    display = spec["source_displays"]
    printed_i = display["second_moment_numeric_if_m4"]
    printed_fourth = display["fourth_flexural_Hz"]
    eb = euler_bernoulli_limit_hz(L, A, I, E, rho)
    checks = {
        "route_agreement_all_modes": all(r["route_difference_Hz"] <= spec["budgets"]["route_absolute_Hz"] for r in rows),
        "eigen_residual_all_modes": all(r["eigen_residual_relative"] <= spec["budgets"]["eigen_residual_relative"] for r in rows),
        "first_display_precision": lo <= first["independent_energy_matrix_Hz"] < hi,
        "positive_ordered_modes": all(rows[i]["independent_energy_matrix_Hz"] > (rows[i-1]["independent_energy_matrix_Hz"] if i else 0) for i in range(4)),
        "shear_and_rotary_lower_than_eb": first["independent_energy_matrix_Hz"] < eb,
    }
    assert all(checks.values()), checks
    return {"status": "executed analytical development reference awaiting scoped Claude technical review",
            "spec_sha256": hashlib.sha256(raw).hexdigest(),
            "derived_section": {"area_m2": A, "second_moment_m4": I, "shear_modulus_Pa": G},
            "source_display_inertia_diagnostic": {
                "printed_numeric_value_m4_if_reinterpreted": printed_i,
                "first_mode_from_printed_numeric_value_Hz": source_formula_hz(1, L, A, printed_i, E, G, rho, shear_factor),
                "printed_value_matches_derived_section": I == printed_i,
            },
            "flexural_modes": rows,
            "axial_control_Hz": axial_control_hz(L, E, rho),
            "euler_bernoulli_first_mode_limit_Hz": eb,
            "published_displays_Hz": {"first_flexural": spec["claim"]["published_display_Hz"],
                                      "second_flexural": display["second_flexural_Hz"],
                                      "first_axial": display["first_axial_Hz"],
                                      "third_flexural": display["third_flexural_Hz"],
                                      "fourth_flexural": printed_fourth},
            "fourth_display_interval_excludes_derived": not (printed_fourth-0.05 <= rows[3]["independent_energy_matrix_Hz"] < printed_fourth+0.05),
            "checks": checks}


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
