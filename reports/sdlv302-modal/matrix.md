# SDLV302 analytical modal reference, pending scoped review

The [registered specification](../../studies/sdlv302_modal/spec.json) extracts one
published-reference claim from the official Code_Aster [problem](https://code-aster.org/doc/v17/manuals/man_v/v2/v2.04.302/Probl_me_de_r_f_rence.html)
and [solution](https://code-aster.org/doc/v17/manuals/man_v/v2/v2.04.302/Solution_de_r_f_rence.html):
the first flexural cyclic frequency of a simply supported, uniform Timoshenko
beam. This is a dynamic shear and rotary-inertia problem, distinct from the
repository's static Euler-Bernoulli cantilever. The claim is for the ideal
one-dimensional beam. The manual's 3D HEXA20 validation model is an approximate
comparison with that analytical reference; no 3D solve or convergence result
is asserted here.

The [executed results](results.json) are the sole numeric output source. The
source's dimensionless expression and a separately derived stiffness-mass
determinant agree at the registered flexural modes. The first result lies in
the source's printed display interval. An axial extension mode, mode ordering,
matrix residual and Euler-Bernoulli limiting check provide controls. These
are numerical reproduction and reporting-precision checks, not an engineering
acceptance tolerance or benchmark artifact label.

There are two visible source discrepancies. The manual prints a section
second moment that disagrees with the stated dimensions and its own formula;
using that printed number misses the first printed frequency. We use the
dimensionally correct expression and retain the alternative computation in
`results.json`. The fourth printed flexural frequency also lies outside its
nearest-tenth display interval when the published formula and exact geometric
expression are used. That higher mode is diagnostic only; it is not the
specified first-mode claim. No tolerance was widened to absorb either
discrepancy. The historical first execution and the subsequent source
correction remain separate Git commits.

The official manual is published under the documentation repository's
[GNU FDL 1.3 licence](https://gitlab.com/codeaster/doc/docaster/-/blob/main/LICENSE.txt).
The separate Code_Aster [source repository](https://gitlab.com/codeaster/src/-/blob/main/LICENSE)
uses GPL v3, and its SDLV302 command file has a GPL v3-or-later header. We
inspected that deck only to distinguish the code terms; it is not reproduced.
The manual cites a Samtech report as theoretical provenance, but that
third-party report has not been inspected and no rights in it are inferred.
This repository links to the official pages and independently writes its
specification and implementation; it copies no vendor text, figures or deck.
The manual's source-page URLs, retrieved HTML hashes and the two repository
heads at audit are in the specification. Raw downloaded pages remain local
scratch material.

Reproduce from the repository root with `python3 -m studies.sdlv302_modal.run`
and run `pytest -q tests/test_sdlv302_modal.py`. This public development
result is awaiting a pinned, reconciled Claude AI technical review. It does
not yet increase the admitted count or open labels, costs or a pilot.
