# SDLV302 analytical modal reference

The [registered specification](../../studies/sdlv302_modal/spec.json) extracts
one claim from the official Code_Aster [problem](https://code-aster.org/doc/v17/manuals/man_v/v2/v2.04.302/Probl_me_de_r_f_rence.html)
and [solution](https://code-aster.org/doc/v17/manuals/man_v/v2/v2.04.302/Solution_de_r_f_rence.html):
the first XY-plane flexural cyclic frequency of a simply supported, uniform
Timoshenko beam. Its shear deformation, rotary inertia, modal observable and
support conditions distinguish it from this repository's static
Euler-Bernoulli cantilever. The claim concerns the ideal one-dimensional beam.
The manual's 3D HEXA20 validation model is an approximate comparison; no 3D
solve or convergence result is asserted here.

The [executed results](results.json) are the numeric output source. The
source's dimensionless expression and a separately derived stiffness-mass
determinant agree at the registered flexural modes. They solve the same modal
quadratic, so this chiefly checks transcription. The first result falls in
the source's printed display interval. The generator checks flexural order,
matrix residual and the Euler-Bernoulli limit, and computes an axial frequency.
It does not gate the registered scaling or global-mode-order controls. The
[non-blind Claude AI reviewer checker](claude-review/independent_check.py)
executes those controls and independently discretizes the beam. These are
numerical reproduction and reporting-precision checks; no engineering
acceptance tolerance or benchmark artifact label is inferred.

The manual's displayed second moment disagrees with its dimensions and
formula. It approximately equals the weak-axis moment from swapping width
and height. The manual also omits unit exponents for both area and inertia.
Using the printed inertia number misses the first printed frequency. We use
the stated geometry and formula, and retain the alternative calculation in
`results.json`. The fourth printed flexural frequency falls outside
nearest-tenth rounding of the derived value but inside four-significant-figure
rounding. The source does not state a display convention. The result's
fourth-mode flag tests nearest-tenth only; that mode is outside this claim.
The original execution and later source-description correction remain in Git
history. Neither finding changed the first-mode gate or computation.

The official manual's repository carries a [GNU FDL 1.3 licence](https://gitlab.com/codeaster/doc/docaster/-/blob/v17/LICENSE.txt)
and identifies GNU FDL in its build configuration. The rendered page shows
only a copyright footer. The GNU FDL requires retaining copyright and licence
notices for verbatim copies and GNU FDL licensing for modified document copies.
The separate Code_Aster [source repository](https://gitlab.com/codeaster/src/-/blob/main/LICENSE)
uses GPL v3; its SDLV302 command file has a GPL v3-or-later header. We
inspected that deck but do not reproduce it. The documentation licence does
not establish rights in the cited third-party Samtech report or any separately
owned material. The manual cites that report
as theoretical provenance. That report was unavailable and no rights in it
are inferred. The manual calls its values analytical, while the deck marks
the corresponding test reference type as undefined. The manual supports the
narrow analytical claim here. We link to the official pages, independently
write the specification and implementation, and copy no vendor text, figure
or deck. The specification pins the v17 source and retrieved page hashes;
downloaded pages remain local scratch material.

The [reconciled review](claude-review/README.md) supports admission of this
first XY-plane analytical frequency only. The printed display interval is
neither an acceptance band for the 3D model nor a physical/application
tolerance. No labels, costs, baselines or reviewer pilot follow from this
admission. Reproduce from the repository root with
`python3 -m studies.sdlv302_modal.run` and
`pytest -q tests/test_sdlv302_modal.py`.
