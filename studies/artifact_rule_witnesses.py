"""Public development witnesses for claim, artifact and explanation boundaries.

All constructed alternatives are analytic, not policy/checker labels or observed
failures. Fractions keep exact controls distinct from numerical output bounds.
"""
import json
from fractions import Fraction as F
from pathlib import Path

from studies.artifact_evidence import bounded, claim_decision, displayed, exact
from studies.kirsch_reference.reference import airy_cartesian, polar
from studies.reference_qualification import assembled, reference
from studies.vm92_artifact_evidence import build as vm92_build

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/artifact-rule-witnesses"


def explanation_decision(reference_value, tolerance, alternatives, observed, observation_tolerance):
    """Decide only from analytic outputs compatible with the declared evidence."""
    compatible = {name: values for name, values in alternatives.items()
                  if abs(values[0] - observed) <= observation_tolerance}
    decisions = {name: claim_decision(exact(values[1]), exact(reference_value), tolerance)
                 for name, values in compatible.items()}
    return {"compatible": list(compatible), "decisions": decisions,
            "status": ("inconsistent" if not decisions else
                       next(iter(set(decisions.values()))) if len(set(decisions.values())) == 1
                       else "ambiguous")}


def registered_resolution(parameters, retained_cases):
    """Return a qualified resolution only for an exactly recorded input."""
    matches = [case for case in retained_cases
               if case["parameters"] == parameters and case["new_resolution_qualified"]]
    if len(matches) != 1:
        return None
    return matches[0]["selected_steps"]


def build():
    bar = json.loads((ROOT / "studies/evidence_sufficiency/spec.json").read_text())
    claims = json.loads((ROOT / "studies/evidence_sufficiency/claims/spec.json").read_text())
    refspec = json.loads((ROOT / "studies/reference_qualification/spec.json").read_text())
    cases = {c["id"]: c for c in refspec["cases"]}
    tol = F(str(claims["claims"][0]["absolute_tolerance"]))
    obs_tol = F(str(claims["observations"][0]["absolute_tolerance"]))
    force = next(c for c in bar["cases"] if c["loading"] == "force")
    displacement = next(c for c in bar["cases"] if c["loading"] == "displacement")
    def axial(c, load, modulus=None):
        L, A, E = F(c["length"]), F(c["area"]), F(modulus or c["modulus"])
        if c["loading"] == "force":
            return (F(load)/A, F(load)*L/(E*A))
        return (E*F(load)/L, F(load))
    nominal = axial(force, force["force"])
    soft = axial(force, force["force"], force["modulus"]//2)
    half_area_stress = nominal[0] * 2
    # If only force is observed and area is allowed to vary, the same exact
    # force supports opposite stress decisions. This is outside M1.1 scope.
    axial_rows = {
        "force_stress_known_load": explanation_decision(nominal[0], tol,
            {"nominal": (nominal[0], nominal[0]), "soft_E": (soft[0], soft[0])},
            nominal[0], obs_tol),
        "force_deflection_known_load": explanation_decision(nominal[1], tol,
            {"nominal": (nominal[0], nominal[1]), "soft_E": (soft[0], soft[1])},
            nominal[0], obs_tol),
        "force_stress_unknown_area_with_force_only": explanation_decision(nominal[0], tol,
            {"nominal": (F(force["force"]), nominal[0]),
             "half_area": (F(force["force"]), half_area_stress)},
            F(force["force"]), 0),
    }
    dnom = axial(displacement, F(str(displacement["displacement"])))
    dsoft = axial(displacement, F(str(displacement["displacement"])), displacement["modulus"]//2)
    axial_rows["displacement_stress"] = explanation_decision(dnom[0], tol,
        {"nominal": (dnom[1], dnom[0]), "soft_E": (dsoft[1], dsoft[0])},
        dnom[1], obs_tol)
    axial_rows["displacement_deflection"] = explanation_decision(dnom[1], tol,
        {"nominal": (dnom[1], dnom[1]), "soft_E": (dsoft[1], dsoft[1])},
        dnom[1], obs_tol)

    beam = cases["cantilever_uniform_load"]
    bp = reference.parameters(beam)
    bnom = reference.beam(bp)
    bsoft = reference.beam({**bp, "modulus_Pa": bp["modulus_Pa"]/2})
    assembled_beam, _ = assembled.solve(beam, beam["partitions"][0])
    assert assembled_beam == bnom  # exact for the declared nodal outputs
    beam_rows = {
        "root_stress_given_nominal_stress": explanation_decision(bnom["root_stress"], 0,
            {"nominal": (bnom["root_stress"], bnom["root_stress"]),
             "soft_E": (bsoft["root_stress"], bsoft["root_stress"])}, bnom["root_stress"], 0),
        "tip_deflection_given_nominal_stress": explanation_decision(bnom["tip_deflection"], 0,
            {"nominal": (bnom["root_stress"], bnom["tip_deflection"]),
             "soft_E": (bsoft["root_stress"], bsoft["tip_deflection"])}, bnom["root_stress"], 0),
    }
    slab = cases["slab_dirichlet"]
    sp = reference.parameters(slab)
    snom = reference.slab(sp)
    ssoft = reference.slab({**sp, "conductivity_W_per_m_K": sp["conductivity_W_per_m_K"]/2})
    slab_rows = {
        "midpoint_temperature_from_same_boundaries": explanation_decision(snom["midpoint_temperature"], 0,
            {"nominal": (snom["midpoint_temperature"], snom["midpoint_temperature"]),
             "half_k": (ssoft["midpoint_temperature"], ssoft["midpoint_temperature"])}, snom["midpoint_temperature"], 0),
        "heat_flux_from_same_temperature": explanation_decision(snom["heat_flux"], 0,
            {"nominal": (snom["midpoint_temperature"], snom["heat_flux"]),
             "half_k": (ssoft["midpoint_temperature"], ssoft["heat_flux"])}, snom["midpoint_temperature"], 0),
    }
    cylinder = cases["vm25_pressure_only"]
    cp = reference.parameters(cylinder)
    cz = reference.cylinder({**cp, "internal_pressure_psi": F(0), "external_pressure_psi": F(0)})
    assert all(value == 0 for value in cz.values())
    zero = {"exact_control": claim_decision(exact(0), exact(0), 0),
            "exact_nonzero": claim_decision(exact(F(1, 10**12)), exact(0), 0),
            "conditional_roundoff": claim_decision(bounded(0, F(1, 10**12)), exact(0), 0)}
    convergence = json.loads((ROOT / "reports/cylinder-convergence/results.json").read_text())
    selected = {c["id"]: c["selected_steps"] for c in convergence["cases"] if c["new_resolution_qualified"]}
    assert len(selected) == len(convergence["cases"])
    assert registered_resolution(convergence["cases"][0]["parameters"], convergence["cases"]) == selected[convergence["cases"][0]["id"]]
    assert registered_resolution({**convergence["cases"][0]["parameters"], "outer_radius_in": "5"}, convergence["cases"]) is None
    vm92 = vm92_build()
    assert vm92["unknown_convention_source_compatibility"] == "ambiguous"
    outer = F(vm92["reference_exact_F"])
    wall_tol = F(vm92["claim_acceptance_error_F"])
    wall = {"exact": claim_decision(exact(outer), exact(outer), wall_tol),
            "constructed_negative": claim_decision(exact(outer+2*wall_tol), exact(outer), wall_tol),
            "unknown_display": vm92["unknown_convention_source_compatibility"],
            "nearest_display": claim_decision(displayed(336, 1, "nearest_half_away_from_zero"), exact(outer), wall_tol),
            "truncate_display": claim_decision(displayed(336, 1, "truncate_toward_zero"), exact(outer), wall_tol)}
    kspec = json.loads((ROOT / "studies/kirsch_reference/spec.json").read_text())
    kresult = json.loads((ROOT / "reports/kirsch-reference/results.json").read_text())
    assert kspec["claim"]["exact_reference"] == "3*sigma"
    kcases = {c["id"]: c for c in kspec["cases"]}
    admitted = {c["id"]: c for c in kresult["cases"]}
    knom, kadm = kcases["nominal"], admitted["nominal"]
    sigma = F(knom["remote_sigma_MPa"])
    hoop = F(kadm["claim_sigma_theta_MPa"])
    airy = F(kadm["independent_claim_sigma_yy_MPa"])
    # spec budgets.stress_route_abs_MPa, as applied by studies/kirsch_reference/run.py.
    route_budget = F("1e-9") * max(1, abs(sigma))
    assert hoop == 3 * sigma and abs(airy - hoop) <= route_budget

    def kirsch_hoop(case):
        # The admitted routes take E and nu only as domain assertions: the
        # prescribed-traction stress field does not depend on them.
        assert float(case["E_MPa"]) > 0 and -1 < float(case["nu"]) < 0.5
        a, s = float(case["a_m"]), float(case["remote_sigma_MPa"])
        p, q = polar(a, 0, a, s)[1], airy_cartesian(a, 0, a, s)[1]
        assert abs(p - q) <= route_budget
        return F(p)

    kalts = {"nominal": knom, "half_E": {**knom, "E_MPa": knom["E_MPa"] / 2}, "nu_0": {**knom, "nu": 0}}
    kirsch = {
        "exact_reference_by_case": {
            cid: claim_decision(exact(F(admitted[cid]["claim_sigma_theta_MPa"])),
                                exact(3 * F(c["remote_sigma_MPa"])), 0)
            for cid, c in kcases.items()},
        "constructed_outside_route_budget": claim_decision(exact(hoop + 2 * route_budget), exact(3 * sigma), route_budget),
        "airy_route_bounded": claim_decision(bounded(airy, route_budget), exact(3 * sigma), 0),
        "hoop_given_hoop_modulus_and_poisson_vary": explanation_decision(3 * sigma, 0,
            {name: (kirsch_hoop(c), kirsch_hoop(c)) for name, c in kalts.items()}, hoop, 0),
    }
    return {"status": "development witnesses only; no new case, frozen label or solver run",
            "axial": axial_rows, "beam": beam_rows, "slab": slab_rows,
            "cylinder_zero": zero, "cylinder_registered_inputs": len(selected),
            "cylinder_selected_steps_example": {"id": "prior_153", "steps": selected["prior_153"]},
            "vm92_regression": wall, "kirsch": kirsch}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(build(), indent=2) + "\n")


if __name__ == "__main__":
    main()
