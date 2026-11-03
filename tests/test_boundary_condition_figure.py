"""The boundary-condition figure data, caption and typeset tables match the stored results.

MATLAB draws the figure from boundary-condition-data.csv and writes the table
fragments (matlab/render_figures.m). CI has no MATLAB, so these tests check the
committed inputs and outputs it reads and writes, not the drawing itself.
"""
import csv
import json
import re
from pathlib import Path

from studies.evidence_sufficiency import plot
from studies.evidence_sufficiency.run import VARIANT_LABELS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/evidence-sufficiency"
CLAIMS = ROOT / "reports/claim-sufficiency"
RESULT = json.loads((OUT / "results.json").read_text())
SPEC = json.loads((ROOT / "studies/evidence_sufficiency/spec.json").read_text())


def committed_rows():
    with (OUT / "boundary-condition-data.csv").open(newline="") as f:
        return list(csv.DictReader(f))


def test_plot_data_file_reproduces_from_results(tmp_path):
    path = tmp_path / "data.csv"
    plot.write_data(plot.plot_rows(RESULT, SPEC), path)
    assert path.read_text() == (OUT / "boundary-condition-data.csv").read_text()


def test_plot_data_carries_stored_values_and_check_outcomes():
    rows = {(r["loading"], r["variant"]): r for r in RESULT["rows"]}
    data = committed_rows()
    assert len(data) == 12
    assert [r["panel"] for r in data] == [c for c in plot.LETTERS for _ in plot.SERIES]
    for r in data:
        stored = rows[(r["loading"], r["variant"])]
        check = {key: check for key, check, _, _ in plot.OBSERVABLES}[r["observable"]]
        assert float(r["value"]) == stored["output"][r["observable"]]
        assert float(r["reference"]) == stored["reference"][r["observable"]]
        assert r["check_passes"] == str(stored["checks"][check]).lower()


def test_figure_outputs_exist_beside_the_data():
    for ext in ("png", "pdf", "svg"):
        assert (OUT / f"boundary-condition.{ext}").stat().st_size > 0


def test_caption_matches_data_file_and_readme():
    text = plot.caption(RESULT, SPEC)
    assert text == (OUT / "boundary-condition.caption.md").read_text().strip()
    assert "1000 N" in text and "0.025 mm" in text
    assert "only the extension check detects the fault" in text
    assert "the stress and reaction checks detect the fault" in text
    squash = lambda s: " ".join(s.split())
    assert squash(text) in squash((ROOT / "README.md").read_text())
    manifest = json.loads((ROOT / "docs/figure-manifest.json").read_text())
    assert manifest["figures"][0]["caption"] == text


def tex_rows(path: Path) -> list[list[str]]:
    """Body rows of a generated tabular fragment, split into stripped cells."""
    body = path.read_text().split("\\midrule", 1)[1].split("\\bottomrule", 1)[0]
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.endswith("\\\\") or line.startswith("\\multicolumn"):
            continue
        rows.append([c.strip() for c in line[:-2].split("&")])
    return rows


def label(cell: str) -> str:
    return re.sub(r"\\quad\s*|\\textit\{|\}", "", cell).strip()


def mark(passed: bool) -> str:
    return "\\passmark" if passed else "\\failmark"


def test_outcomes_table_matches_results():
    labels = {v: k for k, v in VARIANT_LABELS.items()}
    rows = [r for r in tex_rows(OUT / "outcomes-table.tex") if label(r[0]) != "Specification reference"]
    stored = [r for loading in plot.LOADINGS for r in RESULT["rows"] if r["loading"] == loading]
    assert len(rows) == len(stored) == 12
    for cells, r in zip(rows, stored):
        o, c = r["output"], r["checks"]
        assert labels[label(cells[0])] == r["variant"]
        assert cells[1:] == [f'{o["stress"]:.1f}', mark(c["stress"]), f'{o["displacement"]:.4f}',
                             mark(c["displacement"]), f'{o["force"]:.1f}', mark(c["reaction"]),
                             "correct" if r["correct"] else "incorrect"]


def test_policies_table_matches_results():
    rows = tex_rows(OUT / "policies-table.tex")
    assert len(rows) == len(RESULT["scores"])
    for cells, s in zip(rows, RESULT["scores"]):
        error = "{n/a}" if s["error_among_decisions"] is None else f'{100 * s["error_among_decisions"]:.1f}'
        assert cells[1:] == [f'{s["wrong_accepts"]:g}', f'{s["wrong_rejects"]:g}', f'{s["abstentions"]:g}',
                             f'{100 * s["coverage"]:.1f}', f'{s["mean_cost"]:g}', error]


def test_claim_tables_match_results():
    result = json.loads((CLAIMS / "results.json").read_text())
    yes = lambda ok: ("yes~\\passmark" if ok else "no~\\failmark")
    explanations = tex_rows(CLAIMS / "explanations-table.tex")
    expected = [[a["id"], f'{a["implemented_modulus_MPa"]:g}', f'{a["output"]["stress"]:.1f}',
                 f'{a["output"]["displacement"]:.4f}', yes(a["claim_correctness"]["stress"]),
                 yes(a["claim_correctness"]["deflection"])]
                for case in result["cases"] for a in case["artifacts"]]
    assert [[label(r[0])] + r[1:] for r in explanations] == expected
    decisions = tex_rows(CLAIMS / "decisions-table.tex")
    expected = [[name, ", ".join(a["compatible_explanations"]) or "none", yes(a["sufficient"]),
                 a["decision"] or a["status"],
                 " / ".join(a["opposite_decision_witness"]) if a["opposite_decision_witness"] else "none"]
                for case in result["cases"] for name, a in case["claims"].items()]
    assert [[label(r[0])] + r[1:] for r in decisions] == expected


def test_typeset_tables_have_images_and_text_copies():
    doc = (ROOT / "docs/data-and-figures.md").read_text()
    for stem in (OUT / "outcomes-table", OUT / "policies-table",
                 CLAIMS / "explanations-table", CLAIMS / "decisions-table"):
        for ext in ("png", "pdf"):
            assert stem.with_suffix(f".{ext}").stat().st_size > 0
        assert f"{stem.relative_to(ROOT)}.png" in doc
    # The Markdown tables kept under "Table as text" are copies of the generated matrices.
    matrices = (OUT / "matrix.md").read_text() + (CLAIMS / "matrix.md").read_text()
    blocks = re.findall(r"<details><summary>Table as text</summary>\n(.*?)</details>", doc, re.S)
    assert len(blocks) == 4
    for block in blocks:
        for line in block.splitlines():
            if line.startswith("|"):
                assert line in matrices, line
