"""Development references: exact independent routes and physics boundary controls."""
import copy
from fractions import Fraction as F
import json
import math
from pathlib import Path

import pytest

from studies.reference_qualification import assembled, reference, radial
from studies.reference_qualification.run import build, control_case, numeric_agreement, qualify, table

ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "studies/reference_qualification/spec.json").read_text())
BEAM, SLAB, CYLINDER, WALL = SPEC["cases"]


@pytest.mark.parametrize("case", [BEAM, SLAB, WALL], ids=lambda c: c["id"])
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
    assert all(not r["agreement"]["tip_deflection"] for r in result["cross_checks"])
    assert all(r["agreement"]["root_stress"] for r in result["cross_checks"])


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
    assert result["coverage"] == {"development_families": 4, "admitted_problems": 0, "independent_human_reviews": 0}
    assert result["all_new_controls_qualify"]


@pytest.mark.parametrize("control", CYLINDER["controls"], ids=lambda c:c["id"])
def test_cylinder_cross_method_refinement_and_separate_equilibrium(control):
    changed = control_case(CYLINDER, control)
    p = reference.parameters(changed)
    result = qualify(CYLINDER, control)
    assert result["qualified_numerically"]
    previous = None
    for run in result["cross_checks"]:
        d = run["diagnostics"]
        assert d["finite"]
        traction_budget = float(max(p["internal_pressure_psi"],p["external_pressure_psi"]))*1e-12
        assert abs(d["inner_traction_error_psi"]) <= traction_budget
        assert abs(d["outer_traction_error_psi"]) <= traction_budget
        if p["internal_pressure_psi"]:
            error = run["absolute_error"]["inner_displacement"]
            residual = abs(d["integrated_equilibrium_residual_psi_in"])
            h = float((p["outer_radius_in"]-p["inner_radius_in"])/run["steps"])
            # Separate trapezoid balance is second order, while RK4 is fourth order.
            assert residual < float(p["internal_pressure_psi"]*p["inner_radius_in"])*(h/float(p["inner_radius_in"]))**2
            if previous:
                assert 15 < previous[0]/error < 17
                assert 3.9 < previous[1]/residual < 4.1
            previous = error,residual
        else:
            assert set(run["output_binary64"].values()) == {0}


def test_cylinder_axial_convention_cannot_be_replaced_by_closed_ends_or_plane_strain():
    p = reference.parameters(CYLINDER)
    expected = reference.solve(CYLINDER)
    a,b,nu,E = (p[k] for k in ["inner_radius_in","outer_radius_in","poisson_ratio","modulus_psi"])
    sr,st = expected["inner_radial_stress"],expected["inner_hoop_stress"]
    zero_resultant_u = a*(st-nu*sr)/E
    closed_end_axial = (p["internal_pressure_psi"]*a*a-p["external_pressure_psi"]*b*b)/(b*b-a*a)
    plane_strain_axial = nu*(sr+st)
    assert zero_resultant_u == expected["inner_displacement"]
    for axial_stress in [closed_end_axial,plane_strain_axial]:
        alternative_u = a*(st-nu*(sr+axial_stress))/E
        assert not numeric_agreement(float(alternative_u), zero_resultant_u)
    assert expected["inner_radial_stress"] == -p["internal_pressure_psi"]
    assert expected["outer_radial_stress"] == -p["external_pressure_psi"]
    half = reference.solve(control_case(CYLINDER,CYLINDER["controls"][2]))
    assert half["inner_displacement"] == 2*zero_resultant_u
    assert half["inner_hoop_stress"] == st


def test_vm25_dummy_outer_pressure_is_explicitly_negligible_for_declared_budget():
    altered = copy.deepcopy(CYLINDER)
    altered["parameters"]["external_pressure_psi"] = "1e-10"
    exact, with_dummy = reference.solve(CYLINDER),reference.solve(altered)
    budgets = qualify(CYLINDER,CYLINDER["controls"][0])["cross_checks"][0]["cross_method_absolute_tolerance"]
    for k in exact:
        assert abs(float(exact[k]-with_dummy[k])) < budgets[k]


def test_vm92_precision_is_separate_from_exact_truth_and_numeric_tolerance():
    expected = reference.solve(WALL)
    p = reference.parameters(WALL)
    assert (p["hot_temperature_F"]-p["ambient_temperature_F"])/expected["heat_rate"] == F(91,16)
    assert expected["outer_surface_temperature"] == F(30640,91)
    assert not numeric_agreement(336., expected["outer_surface_temperature"])
    assert round(float(expected["outer_surface_temperature"])) == 337
    from studies.reference_qualification.run import published_comparison
    comparison = published_comparison(WALL)
    outer = next(c for c in comparison["comparisons"] if c["observable"] == "outer_surface_temperature")
    assert not outer["within_half_display_unit"]
    assert outer["within_one_display_unit"]
    assert .5 < outer["absolute_difference"] < 1


def test_wall_interface_conservation_area_and_affine_temperature_units():
    for control in WALL["controls"]:
        changed = control_case(WALL,control)
        for partition in WALL["partitions"]:
            computed,d = assembled.solve(changed,partition)
            assert computed == reference.solve(changed)
            assert len(set(d["edge_heat_rates_Btu_per_hr"])) == 1
    base = reference.solve(WALL)
    larger = reference.solve(control_case(WALL,WALL["controls"][3]))
    assert larger["heat_rate"] == 2*base["heat_rate"]
    shifted = copy.deepcopy(WALL)
    for k in ("hot_temperature_F","ambient_temperature_F"):
        shifted["parameters"][k] = str(F(shifted["parameters"][k])+180)
    solution = reference.solve(shifted)
    assert solution["heat_rate"] == base["heat_rate"]
    for k in base:
        if k != "heat_rate":
            assert larger[k] == base[k]
            assert solution[k] == base[k]+180


@pytest.mark.parametrize("case,key,value", [(CYLINDER,"poisson_ratio","1/2"),
    (CYLINDER,"inner_radius_in","8"), (WALL,"outer_h_Btu_per_hr_ft2_F","0")])
def test_new_reference_domains_are_enforced(case,key,value):
    changed = copy.deepcopy(case)
    changed["parameters"][key] = value
    with pytest.raises(ValueError):
        reference.solve(changed)


def test_radial_claim_budget_and_published_precision_are_distinct():
    result = qualify(CYLINDER,CYLINDER["controls"][0])
    for claim in result["claims"]:
        budget = claim["absolute_tolerance"]
        assert claim["decision_rule"] == "characteristic-scale budget"
        assert budget == result["cross_checks"][0]["cross_method_absolute_tolerance"][claim["observable"]]
        # Boundary test at zero avoids an unrepresentable reference-plus-budget sum.
        assert numeric_agreement(budget, F(0), budget)
        assert numeric_agreement(-budget, F(0), budget)
        assert not numeric_agreement(math.nextafter(budget,math.inf), F(0), budget)
    from studies.reference_qualification.run import published_comparison
    displayed = published_comparison(CYLINDER)["comparisons"][0]
    assert float(displayed["display_unit"]) != result["claims"][0]["absolute_tolerance"]


def test_missing_cross_check_does_not_qualify_a_reference():
    changed = copy.deepcopy(BEAM)
    changed["partitions"] = []
    assert not qualify(changed,{"id":"nominal"})["qualified_numerically"]
