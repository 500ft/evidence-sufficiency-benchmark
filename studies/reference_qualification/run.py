"""Local reference qualification only. Reuses public axial results without rerunning them."""
import copy
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

from . import assembled, reference, radial

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "reports/reference-qualification"


def numeric_agreement(value, exact, tolerance=None):
    rounded = float(exact)
    tolerance = math.ulp(rounded) if tolerance is None else tolerance
    return math.isfinite(value) and abs(value - rounded) <= tolerance


def control_case(case, control):
    changed = copy.deepcopy(case)
    p = changed["parameters"]
    for name, factor in control.get("scale", {}).items():
        p[name] = str(F(p[name]) * F(factor))
    for destination, source in control.get("copy", {}).items():
        p[destination] = p[source]
    if "swap" in control:
        a, b = control["swap"]
        p[a], p[b] = p[b], p[a]
    return changed


def qualify(case, control):
    changed = control_case(case, control)
    truth = reference.solve(changed)
    runs = []
    for partition in case.get("partitions", []):
        computed, diagnostics = assembled.solve(changed, partition)
        runs.append({"partition": partition,
                     "output_exact": {k: str(v) for k, v in computed.items()},
                     "rule": "exact rational equality",
                     "agreement": {k: computed[k] == truth[k] for k in truth},
                     "diagnostics": diagnostics})
    if case.get("model") == "thick_cylinder":
        p = reference.parameters(changed)
        pressure = max(p["internal_pressure_psi"], p["external_pressure_psi"])
        scales = {k: pressure*p["inner_radius_in"]/p["modulus_psi"] if k == "inner_displacement" else pressure for k in truth}
        tolerances = {k: float(v*F(case["qualification"]["relative_scale_budget"])) for k,v in scales.items()}
        for steps in case["qualification"]["steps"]:
            computed, diagnostics = radial.solve(p, steps)
            errors = {k: abs(computed[k]-float(truth[k])) for k in truth}
            runs.append({"steps": steps, "rule": "absolute error within declared numerical budget",
                         "output_binary64": computed, "absolute_error": errors,
                         "cross_method_absolute_tolerance": tolerances,
                         "agreement": {k: numeric_agreement(computed[k], truth[k], tolerances[k]) for k in truth},
                         "diagnostics": diagnostics})
    return {"control": control["id"],
            "claims": [{**c, "reference_exact": str(truth[c["observable"]]),
                        "reference_binary64": float(truth[c["observable"]]),
                        "decision_rule": "characteristic-scale budget" if case.get("model") == "thick_cylinder" else "one binary64 ULP",
                        "absolute_tolerance": tolerances[c["observable"]] if case.get("model") == "thick_cylinder" else math.ulp(float(truth[c["observable"]]))}
                       for c in case["claims"]],
            "cross_checks": runs,
            "qualified_numerically": bool(runs) and all(all(r["agreement"].values()) for r in runs)}


def published_comparison(case):
    evidence = case.get("published_evidence")
    if not evidence:
        return None
    truth = reference.solve(case)
    return {"source": evidence["source"], "rule": evidence["rule"], "comparisons": [
        {**item, "derived_exact": str(truth[item["observable"]]),
         "absolute_difference": float(abs(truth[item["observable"]]-F(item["displayed"]))),
         "within_one_display_unit": abs(truth[item["observable"]]-F(item["displayed"])) <= F(item["display_unit"]),
         "within_half_display_unit": abs(truth[item["observable"]]-F(item["displayed"])) <= F(item["display_unit"])/2}
        for item in evidence["targets"]]}


def build():
    spec = json.loads((HERE / "spec.json").read_text())
    # Axial claims, loading conventions and tolerances stay in their original home.
    axial = json.loads((ROOT / spec["reused_axial"]["result"]).read_text())
    axial_contract = json.loads((ROOT / spec["reused_axial"]["contract"]).read_text())
    results = [{"id": c["id"], "family": c["family"],
                "controls": [qualify(c, control) for control in c["controls"]],
                "published_evidence": published_comparison(c)}
               for c in spec["cases"]]
    sources = [*sorted(HERE.glob("*.py")), HERE / "spec.json", HERE / "sources.json",
               ROOT / spec["reused_axial"]["result"], ROOT / spec["reused_axial"]["contract"]]
    return {"status": spec["status"],
            "coverage": {"development_families": len({spec["reused_axial"]["family"], *[c["family"] for c in spec["cases"]]}),
                         "admitted_problems": 0, "independent_human_reviews": 0},
            "reused_axial": {**spec["reused_axial"],
                             "case_ids": [c["source_case"] for c in axial["cases"]],
                             "claim_ids": [c["id"] for c in axial_contract["claims"]]},
            "qualification_rule": spec["qualification_rule"],
            "numeric_claim_rule": spec["numeric_claim_rule"],
            "cases": results,
            "all_new_controls_qualify": all(c["qualified_numerically"] for r in results for c in r["controls"]),
            "provenance": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}


def table(result):
    lines = ["# Development reference qualification", "",
             "**Pending independent human review. M1.2 remains incomplete.**", "",
             f'{result["coverage"]["development_families"]} distinct development families; '
             f'{result["coverage"]["admitted_problems"]} admitted problems; '
             f'{result["coverage"]["independent_human_reviews"]} independent human reviews.', "",
             "The axial family reuses [M1.1](../claim-sufficiency/matrix.md), including its original",
             "loading conventions, tolerances and stiffness cross-checks. Its configurations",
             "are counted once. No axial outputs or figures were regenerated.", "",
             "Source: [results.json](results.json). [Contract, derivations and limitations](../../studies/reference_qualification/README.md).", "",
             "The controls compare closed-form answers with separate stiffness, heat-balance or",
             "radial boundary-value solutions. Fractions in JSON retain exact references.", ""]
    for case in result["cases"]:
        lines += [f'## {case["id"].replace("_", " ")}', "",
                  "| Control | Observable [unit] | Reference | Claim tolerance | Cross-check passes |",
                  "| :--- | :--- | ---: | ---: | :---: |"]
        for control in case["controls"]:
            for claim in control["claims"]:
                name = claim["observable"]
                passes = sum(r["agreement"][name] for r in control["cross_checks"])
                lines.append(f'| {control["control"].replace("_", " ")} | {name.replace("_", " ")} [{claim["unit"]}] | {claim["reference_binary64"]:.9g} | {claim["absolute_tolerance"]:.3g} | {passes}/{len(control["cross_checks"])} |')
        lines += [""]
        if case["family"] == "thick_cylinder_elasticity":
            lines += ["Cylinder claims and cross-checks use the declared numerical budget; step refinement is shown separately:", "",
                      "| Control | Radial steps | Inner displacement error [in] | Budget [in] | Inner hoop error [psi] | Budget [psi] |",
                      "| :--- | ---: | ---: | ---: | ---: | ---: |"]
            for control in case["controls"]:
                for r in control["cross_checks"]:
                    e,t = r["absolute_error"],r["cross_method_absolute_tolerance"]
                    lines.append(f'| {control["control"]} | {r["steps"]} | {e["inner_displacement"]:.3g} | {t["inner_displacement"]:.3g} | {e["inner_hoop_stress"]:.3g} | {t["inner_hoop_stress"]:.3g} |')
            lines += [""]
        if case["published_evidence"]:
            lines += ["Published targets are coarse source evidence, separate from qualification:", "",
                      "| Observable | Published display | Derived value | Difference | Display unit | Within half unit | Within one unit |",
                      "| :--- | ---: | ---: | ---: | ---: | :---: | :---: |"]
            for c in case["published_evidence"]["comparisons"]:
                lines.append(f'| {c["observable"]} | {c["displayed"]} | {float(F(c["derived_exact"])):.10g} | {c["absolute_difference"]:.3g} | {c["display_unit"]} | {c["within_half_display_unit"]} | {c["within_one_display_unit"]} |')
            lines += ["", "Units match the claim table above. A one-unit comparison does not establish the source's rounding mode.", ""]
    lines += ["Rational stiffness/conduction comparisons require exact equality; the cylinder uses its stated budget.",
              "Claim tolerances are one ULP for exact-route binary64 serialization, and the",
              "declared characteristic-scale budget for the cylinder, in each row's unit.",
              "It is not a physical allowable or a tolerance for an approximate FEA model.",
              "Partition and step refinements test the declared observables and boundary handling;",
              "they do not establish general FEA convergence or statistical independence.", "",
              "The thermal HTML source omits x in its printed solution; the pinned PDF includes",
              "it. The implemented solution satisfies both face temperatures and heat balance.", "",
              "Reproduce: `python -m studies.reference_qualification.run`."]
    return "\n".join(lines) + "\n"


def main():
    result = build()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT / "matrix.md").write_text(table(result))
    if not result["all_new_controls_qualify"]:
        raise SystemExit("reference qualification mismatch; inspect results before admission")


if __name__ == "__main__":
    main()
