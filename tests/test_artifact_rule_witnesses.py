"""Scope and boundary regressions for public development witnesses."""
import json
from fractions import Fraction as F
from pathlib import Path

from studies.artifact_rule_witnesses import build, explanation_decision, registered_resolution

ROOT = Path(__file__).resolve().parents[1]


def test_construction_is_independent_of_explanation_names_and_inclusive():
    row = explanation_decision(F(1), F(0), {"good": (0, 1), "bad": (0, 2)}, 0, 0)
    assert row["status"] == "ambiguous"
    assert explanation_decision(1, 0, {"renamed": (0, 1)}, 0, 0)["status"] == "accept"
    assert explanation_decision(1, 0, {"bad": (1, 2)}, 0, 0)["status"] == "inconsistent"
    assert explanation_decision(1, F(1, 10), {"edge": (0, F(11, 10))}, 0, 0)["status"] == "accept"


def test_admitted_family_witnesses_and_committed_result():
    result = build()
    assert result == json.loads((ROOT / "reports/artifact-rule-witnesses/results.json").read_text())
    axial = result["axial"]
    assert axial["force_stress_known_load"]["status"] == "accept"
    assert axial["force_deflection_known_load"]["status"] == "ambiguous"
    assert axial["force_stress_unknown_area_with_force_only"]["status"] == "ambiguous"
    assert axial["displacement_stress"]["status"] == "ambiguous"
    assert axial["displacement_deflection"]["status"] == "accept"
    assert result["beam"]["tip_deflection_given_nominal_stress"]["status"] == "ambiguous"
    assert result["slab"]["heat_flux_from_same_temperature"]["status"] == "ambiguous"
    assert result["cylinder_zero"] == {"exact_control": "accept", "exact_nonzero": "reject", "conditional_roundoff": "ambiguous"}
    assert result["vm92_regression"]["unknown_display"] == "ambiguous"
    assert result["vm92_regression"]["exact"] == "accept"
    assert result["vm92_regression"]["constructed_negative"] == "reject"


def test_cylinder_qualification_does_not_extrapolate():
    cases = json.loads((ROOT / "reports/cylinder-convergence/results.json").read_text())["cases"]
    source = cases[0]
    assert registered_resolution(source["parameters"], cases) == source["selected_steps"]
    changed = {**source["parameters"], "outer_radius_in": "5"}
    assert registered_resolution(changed, cases) is None
    assert registered_resolution(source["parameters"], []) is None
