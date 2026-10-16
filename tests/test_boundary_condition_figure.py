"""The boundary-condition figure shows only stored values, and its words live in the caption.

These checks need matplotlib, which CI does not install; they skip there and
run wherever the figure can be generated.
"""
import json
from pathlib import Path

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")
from matplotlib.text import Text  # noqa: E402

from studies import figure_style as style  # noqa: E402
from studies.evidence_sufficiency import plot  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/evidence-sufficiency"


@pytest.fixture(scope="module")
def built():
    result = json.loads((OUT / "results.json").read_text())
    spec = json.loads((ROOT / "studies/evidence_sufficiency/spec.json").read_text())
    fig = plot.figure(result, spec)
    yield result, spec, fig
    matplotlib.pyplot.close(fig)


def expected_points(result):
    """(loading, output key, check) -> list of (variant, value, passed), in panel order."""
    rows = {(r["loading"], r["variant"]): r for r in result["rows"]}
    return [[(v, rows[(loading, v)]["output"][key], rows[(loading, v)]["checks"][check])
             for v in plot.SERIES]
            for loading in plot.LOADINGS for key, check, _, _ in plot.OBSERVABLES]


def test_markers_carry_stored_values_and_check_outcomes(built):
    result, _, fig = built
    for ax, points in zip(fig.axes, expected_points(result)):
        markers = [line for line in ax.lines if len(line.get_xdata()) == 1]
        assert len(markers) == len(points)
        for line, (variant, value, passed) in zip(markers, points):
            assert line.get_ydata()[0] == value
            assert line.get_marker() == style.VARIANTS[variant]["marker"]
            assert line.get_markerfacecolor() == style.FILL[passed]


def test_canvas_holds_only_axes_text_panel_letters_and_legend(built):
    _, _, fig = built
    printed = {t.get_text() for t in fig.findobj(Text) if t.get_visible() and t.get_text().strip()}
    allowed = {f"({c})" for c in plot.LETTERS}
    allowed |= {label for _, _, label, _ in plot.OBSERVABLES}
    allowed |= {v["label"] for v in style.VARIANTS.values()}
    allowed |= {t.get_text() for legend in fig.legends for t in legend.get_texts()}
    allowed |= {t.get_text() for ax in fig.axes for t in ax.get_xticklabels() + ax.get_yticklabels()}
    assert printed <= allowed, printed - allowed


def test_nothing_printed_touches_anything(built):
    _, _, fig = built
    assert style.audit(fig) == []


def test_caption_matches_data_file_and_readme(built):
    result, spec, _ = built
    text = plot.caption(result, spec)
    assert text == (OUT / "boundary-condition.caption.md").read_text().strip()
    assert "1000 N" in text and "0.025 mm" in text
    assert "only the extension check detects the fault" in text
    assert "the stress and reaction checks detect the fault" in text
    squash = lambda s: " ".join(s.split())
    assert squash(text) in squash((ROOT / "README.md").read_text())
