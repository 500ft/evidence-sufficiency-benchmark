"""Render preserved development outcomes; no solve, model call or uncertainty fit.

The canvas shows only the stored values. Everything in words, including which
checks detect the fault, is written by ``caption()`` to a file beside the image
and copied into the README under it.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator

from .. import figure_style as style

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports/evidence-sufficiency"
STEM = OUT / "boundary-condition"
SERIES = ("correct_control", "modulus_fault")
# Output key, check id, axis label, check name used in the caption.
OBSERVABLES = (("stress", "stress", "Stress [MPa]", "stress"),
               ("displacement", "displacement", "Extension [mm]", "extension"),
               ("force", "reaction", "Reaction [N]", "reaction"))
LOADINGS = ("force", "displacement")
LETTERS = "abcdef"

# Layout in inches: 183 mm wide, two rows of three panels, legend above.
WIDTH, HEIGHT = 7.2, 4.4
MARGINS = {"left": .085, "right": .99, "top": .87, "bottom": .10, "wspace": .62, "hspace": .40}


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
    """Validated inputs shared by the figure and its caption."""
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


def caption(result: dict, spec: dict) -> str:
    _, _, detecting, loads, (length, area) = panels(result, spec)
    return (
        "Seeded development example, not physical validation. Six panels show the "
        "stored stress [MPa], extension [mm] and reaction [N] for the control "
        "(circles) and the half-modulus artifact (squares). Panels (a) to (c): "
        f'prescribed force, {loads["force"]}. Panels (d) to (f): prescribed '
        f'displacement, {loads["displacement"]}. The dashed line is the independent '
        "specification reference. A filled marker means the panel's check passes "
        "against that reference; a hollow marker means it fails. Under prescribed "
        f'force {found(detecting["force"])}; under prescribed displacement '
        f'{found(detecting["displacement"])}. Both half-modulus artifacts fail the '
        f"full response tuple. Uniform axial bar, {length:g} mm long, {area:g} mm² "
        "section; one deterministic artifact per point, so there are no error bars. "
        "Values: matrix.md. Sources: results.json and spec.json."
    )


def figure(result: dict, spec: dict):
    _, subsets, _, _, _ = panels(result, spec)
    style.apply()
    fig, axes = plt.subplots(len(LOADINGS), len(OBSERVABLES), figsize=(WIDTH, HEIGHT))
    fig.subplots_adjust(**MARGINS)
    for i, loading in enumerate(LOADINGS):
        subset = subsets[loading]
        for j, (key, check, label, _) in enumerate(OBSERVABLES):
            ax = axes[i, j]
            # The reference is the independent specification answer, shared by every row of a loading.
            references = {r["reference"][key] for r in subset.values()}
            assert len(references) == 1, references
            ax.axhline(references.pop(), zorder=1, **style.REFERENCE)
            # Equal limits within each observable, with zero visible; units are never mixed.
            top_value = max(r["output"][key] for r in result["rows"] if r["variant"] in SERIES)
            ax.set(xlim=(-.5, 1.5), ylim=(0, top_value * 1.25), ylabel=label)
            ax.set_xticks([0, 1], [style.VARIANTS[v]["label"] for v in SERIES])
            ax.tick_params(axis="x", labelbottom=i == len(LOADINGS) - 1, length=3)
            ax.tick_params(axis="y", length=3)
            ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
            for x, variant in enumerate(SERIES):
                row = subset[variant]
                ax.plot(x, row["output"][key], marker=style.VARIANTS[variant]["marker"],
                        mfc=style.FILL[row["checks"][check]], zorder=3, **style.MARKER)
            ax.text(0, 1.04, f"({LETTERS[i * len(OBSERVABLES) + j]})", transform=ax.transAxes,
                    ha="left", va="bottom", size=style.LETTER_SIZE)
    handles = [Line2D([], [], marker=v["marker"], mfc=style.FILL[True], label=v["label"], **style.MARKER)
               for v in (style.VARIANTS[key] for key in SERIES)]
    handles.append(Line2D([], [], marker="s", mfc=style.FILL[False], label="Hollow: check fails", **style.MARKER))
    handles.append(Line2D([], [], label="Specification reference", **style.REFERENCE))
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.5, .995), ncol=len(handles),
               columnspacing=1.4, handletextpad=.5, borderaxespad=0)
    return fig


def main():
    result = json.loads((OUT / "results.json").read_text())
    spec = json.loads((ROOT / "studies/evidence_sufficiency/spec.json").read_text())
    fig = figure(result, spec)
    style.save(fig, STEM)
    STEM.with_suffix(".caption.md").write_text(caption(result, spec) + "\n")
    plt.close(fig)


if __name__ == "__main__":
    main()
