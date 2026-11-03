"""Export the plotted values and the caption of the boundary-condition figure.

No solve, model call or uncertainty fit happens here. This module checks the
stored outcomes, writes the 12 plotted points to ``boundary-condition-data.csv``
and writes the caption beside the image. MATLAB draws the figure from that CSV:
``matlab -batch "addpath matlab; render_figures"`` (see ``matlab/README.md``).
The caption is copied into the README under the image.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports/evidence-sufficiency"
STEM = OUT / "boundary-condition"
DATA = OUT / "boundary-condition-data.csv"
SERIES = ("correct_control", "modulus_fault")
SERIES_LABELS = {"correct_control": "control", "modulus_fault": "half modulus"}
# Output key, check id, unit, check name used in the caption.
OBSERVABLES = (("stress", "stress", "MPa", "stress"),
               ("displacement", "displacement", "mm", "extension"),
               ("force", "reaction", "N", "reaction"))
LOADINGS = ("force", "displacement")
LETTERS = "abcdef"
COLUMNS = ("panel", "loading", "load", "observable", "unit", "variant", "label",
           "value", "reference", "check_passes")


def detecting_checks(rows: dict) -> list[str]:
    """Names of the observable checks that fail for the half-modulus artifact."""
    return [name for _, check, _, name in OBSERVABLES if not rows["modulus_fault"]["checks"][check]]


def found(detecting: list[str]) -> str:
    if not detecting:
        return "no observable check detects the fault"
    if len(detecting) == 1:
        return f"only the {detecting[0]} check detects the fault"
    return f'the {" and ".join(detecting)} checks detect the fault'


def panels(result: dict, spec: dict):
    """Validated inputs shared by the plotted data and the caption."""
    cases = {c["loading"]: c for c in spec["cases"]}
    subsets = {loading: {r["variant"]: r for r in result["rows"] if r["loading"] == loading}
               for loading in LOADINGS}
    detecting = {loading: detecting_checks(subsets[loading]) for loading in LOADINGS}
    # The caption must hold for every plotted row.
    assert detecting["force"] != detecting["displacement"], detecting
    assert all(detecting.values()), detecting
    assert not any(subsets[l]["modulus_fault"]["correct"] for l in LOADINGS)
    assert all(subsets[l]["correct_control"]["correct"] for l in LOADINGS)
    geometry = {(c["length"], c["area"]) for c in spec["cases"]}
    assert len(geometry) == 1, geometry
    loads = {"force": f'{cases["force"]["force"]:g} N',
             "displacement": f'{cases["displacement"]["displacement"]:g} mm'}
    return cases, subsets, detecting, loads, geometry.pop()


def plot_rows(result: dict, spec: dict) -> list[dict]:
    """One row per plotted point, in panel order (a) to (f), control first."""
    _, subsets, _, loads, _ = panels(result, spec)
    rows = []
    for i, loading in enumerate(LOADINGS):
        subset = subsets[loading]
        for j, (key, check, unit, _) in enumerate(OBSERVABLES):
            # The reference is the independent specification answer, shared by every row of a loading.
            references = {r["reference"][key] for r in subset.values()}
            assert len(references) == 1, references
            reference = references.pop()
            for variant in SERIES:
                row = subset[variant]
                rows.append({"panel": LETTERS[i * len(OBSERVABLES) + j], "loading": loading,
                             "load": loads[loading], "observable": key, "unit": unit,
                             "variant": variant, "label": SERIES_LABELS[variant],
                             "value": row["output"][key], "reference": reference,
                             "check_passes": row["checks"][check]})
    return rows


def write_data(rows: list[dict], path: Path = DATA) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows({**r, "check_passes": str(r["check_passes"]).lower()} for r in rows)


def caption(result: dict, spec: dict) -> str:
    _, _, detecting, loads, (length, area) = panels(result, spec)
    return (
        "Seeded development example, not physical validation. Six panels show the "
        "stored stress [MPa], extension [mm] and reaction [N] for the control "
        "(blue circles) and the half-modulus artifact (orange squares). Panels (a) to (c): "
        f'prescribed force, {loads["force"]}. Panels (d) to (f): prescribed '
        f'displacement, {loads["displacement"]}. The dotted grey line is the independent '
        "specification reference. A filled marker means the panel's check passes "
        "against that reference; a hollow marker means it fails. Under prescribed "
        f'force {found(detecting["force"])}; under prescribed displacement '
        f'{found(detecting["displacement"])}. Both half-modulus artifacts fail the '
        f"full response tuple. Uniform axial bar, {length:g} mm long, {area:g} mm² "
        "section; one deterministic artifact per point, so there are no error bars. "
        "Values: matrix.md. Sources: results.json and spec.json."
    )


def main():
    result = json.loads((OUT / "results.json").read_text())
    spec = json.loads((ROOT / "studies/evidence_sufficiency/spec.json").read_text())
    write_data(plot_rows(result, spec))
    STEM.with_suffix(".caption.md").write_text(caption(result, spec) + "\n")


if __name__ == "__main__":
    main()
