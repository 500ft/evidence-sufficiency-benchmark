"""Bounded VM92 artifact-class demonstration; no new case or solver run."""

import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

from studies.artifact_evidence import (
    bounded, claim_decision, displayed, exact,
)
from studies.reference_qualification import assembled

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "studies/reference_qualification/spec.json"
HISTORICAL = ROOT / "reports/reference-qualification/results.json"
OUT = ROOT / "reports/vm92-artifact-evidence"
LATER_BOOK = {
    "title": "Principles of Heat Transfer",
    "authors": "Frank Kreith and Mark S. Bohn",
    "edition": "Fourth Edition",
    "copyright_year": 1986,
    "supplied_pdf_sha256": "3c4f5bfa8fb6f0c4f22b5fb21e44e7ee129afeab056b18e5f69d911058f96c85",
    "inspected_printed_pages": [28, 29, 32],
    "scope": "Different one-layer SI example on pp. 28-29; p. 32 does not establish the cited 1959 display rule",
}


def build():
    spec = json.loads(SPEC.read_text())
    case = next(c for c in spec["cases"] if c["id"] == "vm92_layered_wall")
    old = next(c for c in json.loads(HISTORICAL.read_text())["cases"]
               if c["id"] == case["id"])
    p = {key: F(value) for key, value in case["parameters"].items()}

    # Independently sum the four thermal drops per unit outward heat rate.
    area = p["area_ft2"]
    drops = [1 / (p["inner_h_Btu_per_hr_ft2_F"] * area),
             p["layer1_ft"] / (p["k1_Btu_per_hr_ft_F"] * area),
             p["layer2_ft"] / (p["k2_Btu_per_hr_ft_F"] * area),
             1 / (p["outer_h_Btu_per_hr_ft2_F"] * area)]
    rate = (p["hot_temperature_F"] - p["ambient_temperature_F"]) / sum(drops)
    outer = p["ambient_temperature_F"] + rate * drops[-1]
    assembled_output, _ = assembled.solve(case, case["partitions"][0])
    assert assembled_output["heat_rate"] == rate
    assert assembled_output["outer_surface_temperature"] == outer
    nominal = next(c for c in old["controls"] if c["control"] == "nominal")
    claim = next(c for c in nominal["claims"] if c["observable"] == "outer_surface_temperature")
    assert F(claim["reference_exact"]) == outer
    target = next(c for c in case["published_evidence"]["targets"]
                  if c["observable"] == "outer_surface_temperature")

    tolerance = F(claim["absolute_tolerance"])
    reported, unit = F(target["displayed"]), F(target["display_unit"])
    reference = exact(outer)  # This VM92 route has zero numerical reference error.
    modes = {}
    for name in ("nearest_half_away_from_zero", "truncate_toward_zero"):
        interval = displayed(reported, unit, name)
        modes[name] = {
            "interval": {"low": str(interval.low), "high": str(interval.high),
                         "low_closed": interval.low_closed,
                         "high_closed": interval.high_closed},
            "exact_reference_compatible": interval.contains(outer),
            "claim_decision_if_this_were_an_artifact": claim_decision(interval, reference, tolerance),
        }
    # A binary64 projection of the executed exact assembly is used only to
    # illustrate a conditional numerical-solver rule, not to claim a solver run.
    binary64 = F(float(assembled_output["outer_surface_temperature"]))
    solver = bounded(binary64, tolerance)
    return {
        "scope": "VM92 nominal derived development reference; no new case, label or solver run",
        "later_edition_source_review": LATER_BOOK,
        "provenance_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in (SPEC, HISTORICAL, Path(__file__),
                                           ROOT / "studies/artifact_evidence.py")},
        "observable": "outer_surface_temperature",
        "unit": "degF",
        "resistance_exact_hr_F_per_Btu": str(sum(drops)),
        "heat_rate_exact_Btu_per_hr": str(rate),
        "reference_exact_F": str(outer),
        "numerical_reference_error_F": "0",
        "claim_acceptance_error_F": str(tolerance),
        "exact_control_decision": claim_decision(exact(assembled_output["outer_surface_temperature"]), reference, tolerance),
        "published_display_F": str(reported),
        "display_unit_F": str(unit),
        "rounding_convention": "unreported by the cited source",
        "possible_display_conventions": modes,
        "unknown_convention_source_compatibility": "ambiguous" if len({m["exact_reference_compatible"] for m in modes.values()}) > 1 else ("compatible" if next(iter(modes.values()))["exact_reference_compatible"] else "incompatible"),
        "illustrative_solver": {
            "reported_binary64_F": repr(float(binary64)),
            "assumed_output_error_F": str(tolerance),
            "decision": claim_decision(solver, reference, tolerance),
            "status": "conditional bound on a binary64 projection of exact assembly; no numerical-solver qualification",
        },
    }


def table(result):
    modes = result["possible_display_conventions"]
    lines = ["# VM92 artifact class and evidence precision", "",
             "This is a development decision-rule demonstration on the already admitted",
             "derived wall problem. [results.json](results.json) is the numeric source.",
             "The [reference specification](../../studies/reference_qualification/spec.json)",
             "and [source record](../../studies/reference_qualification/sources.json)",
             "remain unchanged, as does the historical qualification output.", "",
             f'The exact series-drop derivation gives resistance {result["resistance_exact_hr_F_per_Btu"]} hr degF/Btu,',
             f'heat rate {result["heat_rate_exact_Btu_per_hr"]} Btu/hr and outer face',
             f'{result["reference_exact_F"]} degF. A separately assembled balance agrees exactly.',
             f'The original claim acceptance error is {result["claim_acceptance_error_F"]} degF;',
             f'numerical reference error here is {result["numerical_reference_error_F"]} degF.',
             "Neither is the precision of a printed source value or an engineering allowable.", "",
             "| Artifact or evidence | Declared precision | Relation to exact reference | Claim decision |",
             "| :--- | :--- | :--- | :--- |",
             f'| Exact rational assembled control | Exact | Equal | {result["exact_control_decision"]} |']
    for name, row in modes.items():
        interval = row["interval"]
        left = "[" if interval["low_closed"] else "("
        right = "]" if interval["high_closed"] else ")"
        span = f'{left}{interval["low"]}, {interval["high"]}{right} degF'
        compatibility = "compatible" if row["exact_reference_compatible"] else "incompatible"
        lines.append(f'| Published {result["published_display_F"]} degF if {name.replace("_", " ")} | {span} | {compatibility} | {row["claim_decision_if_this_were_an_artifact"]} if treated as artifact |')
    solver = result["illustrative_solver"]
    lines += [f'| Binary64 projection as conditional numerical solver | Assumed output error {solver["assumed_output_error_F"]} degF | Reference error remains zero | {solver["decision"]} |', "",
              "The cited source gives no rounding convention. The two explicit conventions",
              "give different source-compatibility outcomes, so the printed value remains",
              "ambiguous and is excluded from published corroboration. Even a compatible",
              "coarse display cannot establish acceptance at the claim precision. The",
              "numerical-solver row is a conditional rule check, not an executed solver",
              "measurement or a new admission. Reference error, output uncertainty and",
              "claim acceptance error remain separate inputs. No VM92 explanation set is",
              "frozen, so these are claim classifications, not evidence-sufficiency labels.", "",
              "The owner-reported 336.54 degF has no verified source and is not an input.",
              f'The supplied {result["later_edition_source_review"]["authors"]}',
              f'{result["later_edition_source_review"]["edition"]} ({result["later_edition_source_review"]["copyright_year"]}) contains a different',
              "one-layer SI wall example at printed pp. 28-29; its inspected printed p. 32",
              "does not establish the VM92 display rule. The VM92 citation is to an earlier",
              "1959 printing, which was not obtained. The supplied PDF SHA-256 is",
              f'`{result["later_edition_source_review"]["supplied_pdf_sha256"]}`;',
              "no book pages are redistributed.", "",
              "Reproduce: `python -m studies.vm92_artifact_evidence`."]
    return "\n".join(lines) + "\n"


def main():
    result = build()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT / "matrix.md").write_text(table(result))


if __name__ == "__main__":
    main()
