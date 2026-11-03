# MATLAB figure and table rendering

MATLAB R2025b draws the data figure and writes the headline result tables.
Python still computes every result. These scripts only read committed files
under `reports/` and change no result.

## Regenerate

Run from the repository root:

```bash
python -m studies.evidence_sufficiency.plot
matlab -batch "addpath matlab; render_figures"
python matlab/typeset_tables.py
```

1. The Python step checks the stored outcomes and writes the 12 plotted points
   to `reports/evidence-sufficiency/boundary-condition-data.csv` and the caption
   to `boundary-condition.caption.md`.
2. The MATLAB step draws `boundary-condition.png` (300 dpi), `.pdf` and `.svg`
   from that CSV. It also writes four LaTeX table fragments (booktabs and
   siunitx) from `results.json` and `policies.csv`.
3. The last step typesets each fragment to PDF and a 300-dpi PNG. It needs
   tectonic or xelatex, plus pdftoppm.

## Files

| File | Role |
| --- | --- |
| `render_figures.m` | Driver. Renders each output in its own try/catch and fails if any output fails. |
| `make_boundary_condition.m` | Six-panel figure: stress, extension and reaction under prescribed force and displacement. |
| `make_result_tables.m` | Outcome, policy, explanation and decision tables. |
| `fig_style.m` | Shared style: LaTeX text, 9/8/7 pt sizes, MATLAB blue and orange, grey reference lines. |
| `export_pair.m` | Writes the vector PDF and the 300-dpi PNG. |
| `typeset_tables.py` | Typesets the table fragments. |

## Style

The canvas holds data, axes and short direct labels only. The caption file
carries the reading of the figure. Blue marks the control and orange the
half-modulus artifact. A filled marker means the check passes; a hollow marker
means it fails. Tables use the same marks: a blue dot passes and an orange
open dot fails. `docs/data-and-figures.md` shows the typeset PNGs and keeps
each Markdown table under "Table as text".
