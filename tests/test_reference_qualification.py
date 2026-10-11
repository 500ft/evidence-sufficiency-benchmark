"""Development references: exact independent routes and physics boundary controls."""
import copy
from fractions import Fraction as F
import json
import math
from pathlib import Path

import pytest

from studies.reference_qualification import assembled, reference
from studies.reference_qualification.run import build, control_case, numeric_agreement, qualify, table

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "studies/reference_qualification/spec.json").read_text())
BEAM, SLAB = SPEC["cases"]


@pytest.mark.parametrize("case", SPEC["cases"], ids=lambda c: c["id"])
def test_all_declared_controls_and_partitions_agree_exactly(case):
    for control in case["controls"]:
        result = qualify(case, control)
        assert result["qualified_numerically"]
        for claim in result["claims"]:
            for run in result["cross_checks"]:
                assert F(run["output_exact"][claim["observable"]]) == F(claim["reference_exact"])


def test_beam_nodal_fields_constraints_and_global_equilibrium():
    p = reference.parameters(BEAM)
    length, q = p["length_m"], p["line_load_N_per_m"]
    rigidity = p["modulus_Pa"] * p["width_m"] * p["height_m"]**3 / 12
    for partition in BEAM["partitions"]:
        out, d = assembled.solve(BEAM, partition)
        for ratio, w, theta in zip(partition, d["nodal_deflections_m"], d["nodal_slopes"]):
            x = F(ratio) * length
            assert F(w) == q * x*x * (6*length*length - 4*length*x + x*x) / (24*rigidity)
            assert F(theta) == q * x * (3*length*length - 3*length*x + x*x) / (6*rigidity)
        assert F(d["nodal_deflections_m"][0]) == F(d["nodal_slopes"][0]) == 0
        assert out["support_force"] + q * length == 0
        assert out["support_moment"] + q * length**2 / 2 == 0


def test_beam_zero_load_reversal_and_stiffness_limit():
    nominal, zero, reverse, stiff = [reference.solve(control_case(BEAM, c)) for c in BEAM["controls"]]
    assert set(zero.values()) == {0}
    assert reverse["tip_deflection"] == -nominal["tip_deflection"]
    assert reverse["root_stress"] == nominal["root_stress"]
    assert stiff["tip_deflection"] == nominal["tip_deflection"] / 2
    assert stiff["root_stress"] == nominal["root_stress"]
    # The selected control stays within the declared small-slope development regime.
    p = reference.parameters(BEAM)
    assert abs(nominal["tip_deflection"] / p["length_m"]) < F(1, 1000)


def test_slab_face_values_local_balance_and_direction():
    p = reference.parameters(SLAB)
    for partition in SLAB["partitions"]:
        out, d = assembled.solve(SLAB, partition)
        temperatures = list(map(F, d["nodal_temperatures_K"]))
        assert temperatures[0] == p["left_temperature_K"]
        assert temperatures[-1] == p["right_temperature_K"]
        for position, temperature in zip(partition, temperatures):
            assert temperature == temperatures[0] + F(position) * (temperatures[-1] - temperatures[0])
        assert len(set(d["segment_fluxes_W_per_m2"])) == 1
        assert out["heat_flux"] > 0
        assert all(temperatures[-1] <= t <= temperatures[0] for t in temperatures)


def test_slab_equal_temperatures_reversal_and_conductivity_scaling():
    nominal, equal, reverse, conductive = [reference.solve(control_case(SLAB, c)) for c in SLAB["controls"]]
    assert equal["heat_flux"] == 0
    assert equal["midpoint_temperature"] == F(SLAB["parameters"]["left_temperature_K"])
    assert reverse["heat_flux"] == -nominal["heat_flux"]
    assert conductive["heat_flux"] == 2*nominal["heat_flux"]
    assert reverse["midpoint_temperature"] == conductive["midpoint_temperature"] == nominal["midpoint_temperature"]


def test_html_missing_position_factor_fails_the_boundary_value_problem():
    p = reference.parameters(SLAB)
    # Literal HTML Eq. (3.4) is constant in x. The PDF includes the missing x.
    erroneous = p["left_temperature_K"] + (p["right_temperature_K"] - p["left_temperature_K"]) / p["length_m"]
    assert erroneous != p["left_temperature_K"]
    assert erroneous != reference.solve(SLAB)["midpoint_temperature"]


def test_numeric_tolerance_is_inclusive_but_not_unbounded():
    for case in SPEC["cases"]:
        for exact in reference.solve(case).values():
            value = float(exact)
            direction = math.inf if value > 0 else -math.inf
            edge = math.nextafter(value, direction)
            assert numeric_agreement(value, exact)
            assert numeric_agreement(edge, exact)
            assert not numeric_agreement(math.nextafter(edge, direction), exact)
    assert numeric_agreement(0.0, F(0))
    assert numeric_agreement(math.ulp(0.0), F(0))
    assert not numeric_agreement(2*math.ulp(0.0), F(0))
    assert not numeric_agreement(float("nan"), F(1))
    assert not numeric_agreement(float("inf"), F(1))


def test_qualification_uses_computed_values_not_control_names(monkeypatch):
    c = copy.deepcopy(BEAM)
    c["id"] = "opaque"
    control = {"id": "looks_correct"}
    original = assembled.solve
    def faulty(case, partition):
        values, diagnostics = original(case, partition)
        values["tip_deflection"] *= 2
        return values, diagnostics
    monkeypatch.setattr(assembled, "solve", faulty)
    result = qualify(c, control)
    assert not result["qualified_numerically"]
    assert all(not r["exact_agreement"]["tip_deflection"] for r in result["cross_checks"])
    assert all(r["exact_agreement"]["root_stress"] for r in result["cross_checks"])


@pytest.mark.parametrize("case,key,value", [(BEAM,"height_m","0"), (BEAM,"modulus_Pa","-1"),
                                            (SLAB,"conductivity_W_per_m_K","0"), (SLAB,"left_temperature_K","-1")])
def test_invalid_physical_domain_is_rejected(case, key, value):
    changed = copy.deepcopy(case)
    changed["parameters"][key] = value
    with pytest.raises(ValueError):
        reference.solve(changed)


def test_small_exact_linear_solver_and_singular_boundary_system():
    # Coupled system with nontrivial rational solution, independent of either physics route.
    assert assembled.linear_solve([[F(2), F(1)], [F(1), F(3)]], [F(1), F(1)]) == [F(2,5), F(1,5)]
    with pytest.raises(ValueError, match="singular"):
        assembled.linear_solve([[F(1), F(1)], [F(1), F(1)]], [F(1), F(1)])


def test_committed_result_and_table_reproduce_without_admission():
    result = build()
    assert result == json.loads((ROOT / "reports/reference-qualification/results.json").read_text())
    assert table(result) == (ROOT / "reports/reference-qualification/matrix.md").read_text()
    assert result["coverage"] == {"development_families": 3, "admitted_problems": 0, "independent_human_reviews": 0}
    assert result["all_new_controls_agree_exactly"]
