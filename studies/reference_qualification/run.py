"""Local reference qualification only. Reuses public axial results without rerunning them."""
import copy
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

from . import assembled, reference

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "reports/reference-qualification"


def numeric_agreement(value, exact):
    rounded = float(exact)
    tolerance = math.ulp(rounded)
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
    for partition in case["partitions"]:
        computed, diagnostics = assembled.solve(changed, partition)
        runs.append({"partition": partition,
                     "output_exact": {k: str(v) for k, v in computed.items()},
                     "exact_agreement": {k: computed[k] == truth[k] for k in truth},
                     "diagnostics": diagnostics})
    return {"control": control["id"],
            "claims": [{**c, "reference_exact": str(truth[c["observable"]]),
                        "reference_binary64": float(truth[c["observable"]]),
                        "absolute_tolerance": math.ulp(float(truth[c["observable"]]))}
                       for c in case["claims"]],
            "cross_checks": runs,
            "qualified_numerically": all(all(r["exact_agreement"].values()) for r in runs)}


def build():
    spec = json.loads((HERE / "spec.json").read_text())
    # Axial claims, loading conventions and tolerances stay in their original home.
    axial = json.loads((ROOT / spec["reused_axial"]["result"]).read_text())
    axial_contract = json.loads((ROOT / spec["reused_axial"]["contract"]).read_text())
    results = [{"id": c["id"], "family": c["family"],
                "controls": [qualify(c, control) for control in c["controls"]]}
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
            "all_new_controls_agree_exactly": all(c["qualified_numerically"] for r in results for c in r["controls"]),
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
             "The following controls compare exact closed-form answers with separately assembled",
             "stiffness or heat-balance systems. Fractions in JSON retain the exact values.", ""]
    for case in result["cases"]:
        lines += [f'## {case["family"].replace("_", " ").capitalize()}', "",
                  "| Control | Observable [unit] | Reference | Binary64 tolerance | Exact cross-checks |",
                  "| :--- | :--- | ---: | ---: | :---: |"]
        for control in case["controls"]:
            for claim in control["claims"]:
                name = claim["observable"]
                passes = sum(r["exact_agreement"][name] for r in control["cross_checks"])
                lines.append(f'| {control["control"].replace("_", " ")} | {name.replace("_", " ")} [{claim["unit"]}] | {claim["reference_binary64"]:.9g} | {claim["absolute_tolerance"]:.3g} | {passes}/{len(control["cross_checks"])} |')
        lines += [""]
    lines += ["Exact equality is the qualification criterion. The tolerance column applies only",
              "to binary64 serialization of each exact claim; it is one ULP in that row's unit.",
              "It is not a physical allowable or a tolerance for an approximate FEA model.",
              "Changing partitions tests assembly and boundary handling; these polynomial",
              "problems do not establish general mesh convergence or statistical independence.", "",
              "The thermal HTML source omits x in its printed solution; the pinned PDF includes",
              "it. The implemented solution satisfies both face temperatures and heat balance.", "",
              "Reproduce: `python -m studies.reference_qualification.run`."]
    return "\n".join(lines) + "\n"


def main():
    result = build()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT / "matrix.md").write_text(table(result))
    if not result["all_new_controls_agree_exactly"]:
        raise SystemExit("reference qualification mismatch; inspect results before admission")


if __name__ == "__main__":
    main()
