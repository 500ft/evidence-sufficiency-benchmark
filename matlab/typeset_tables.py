"""Typeset the MATLAB-written table fragments as PDF and 300-dpi PNG.

Run from the repository root after ``matlab -batch "addpath matlab; render_figures"``:

    python matlab/typeset_tables.py

Each ``*-table.tex`` fragment is wrapped in a standalone page (booktabs,
siunitx, Latin Modern through fontspec, xcolor) and compiled with tectonic,
or with xelatex when tectonic is not installed. pdftoppm (poppler) then
writes the PNG. No value is computed here.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAGMENTS = (
    "reports/evidence-sufficiency/outcomes-table.tex",
    "reports/evidence-sufficiency/policies-table.tex",
    "reports/claim-sufficiency/explanations-table.tex",
    "reports/claim-sufficiency/decisions-table.tex",
)
PAGE = r"""\documentclass[border=6pt]{standalone}
\usepackage{fontspec}
\usepackage{booktabs}
\usepackage{siunitx}
\usepackage{xcolor}
\sisetup{group-separator={,}}
\begin{document}
\input{fragment.tex}
\end{document}
"""


def compile_pdf(work: Path) -> None:
    if shutil.which("tectonic"):
        command = ["tectonic", "--keep-logs", "table.tex"]
    elif shutil.which("xelatex"):
        command = ["xelatex", "-interaction=nonstopmode", "-halt-on-error", "table.tex"]
    else:
        sys.exit("needs tectonic or xelatex")
    subprocess.run(command, cwd=work, check=True, capture_output=True)


def typeset(fragment: Path) -> None:
    stem = fragment.with_suffix("")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        shutil.copy(fragment, work / "fragment.tex")
        (work / "table.tex").write_text(PAGE)
        compile_pdf(work)
        shutil.copy(work / "table.pdf", stem.with_suffix(".pdf"))
    subprocess.run(["pdftoppm", "-r", "300", "-png", "-singlefile",
                    str(stem.with_suffix(".pdf")), str(stem)], check=True)
    print("wrote", stem.with_suffix(".pdf").relative_to(ROOT), stem.with_suffix(".png").relative_to(ROOT))


if __name__ == "__main__":
    for name in FRAGMENTS:
        typeset(ROOT / name)
