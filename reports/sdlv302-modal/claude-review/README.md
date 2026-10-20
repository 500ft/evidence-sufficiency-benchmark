# Reconciled scoped Claude AI technical review

The original [report](REPORT.md), [checker](independent_check.py),
[independent output](independent_results.json), [input/source hashes](input-hashes.txt)
and [report hash](REPORT.sha256) are preserved. The report's SHA-256 is
`feb3042b62e649770659382a6cdb889540b34d9c856241eec39e60dc8c0e8a1b`.
It reviewed technical commit `93afbc8e42b32167f2f9729079bd1215b6421ce3`.
The reviewer was Claude Opus 5.5 (`claude-opus-5-5`) in Claude Code 2.1.304,
session `d9bd23ac-3272-41d0-a20c-85b2ab0f9800`; the model build is unknown.
The review was non-blind: the reviewer saw the implementation and numerical
result before deriving its own calculation. Its script imports no repository
routine and includes an independently discretized beam route. This is a
separately derived AI calculation, not independent authorship, human review,
external peer review, physical validation or a scored reviewer pilot.
The report calls the session "interactive"; the actual invocation used
`claude -p --model opus --output-format json`, which is headless. The CLI
returned success and the session ID above. This provenance correction does
not change the technical findings; the original report remains verbatim.

The [result narrative](../matrix.md) and [specification](../../../studies/sdlv302_modal/spec.json)
reconcile the findings without changing the first-mode computation or its
registered display gate:

| Finding | Disposition |
| :--- | :--- |
| F1, first-mode value | Independent high-precision determinant, source expression and discretized beam route support the narrow first XY-plane analytical frequency. The reviewer checker reproduced the repository result. |
| F2, printed inertia | Confirmed. It approximately equals the weak-axis moment, while the manual's formula, geometry and first printed target use the strong-axis moment. The prose now states the likely axis swap and notes omitted unit exponents; the printed number stays excluded. |
| F3, fourth-mode display | Corrected the initial claim of a source discrepancy. The value is outside nearest-tenth rounding but inside four-significant-figure rounding. The manual leaves convention unspecified. The diagnostic flag in the historical result means nearest-tenth only. This mode remains outside admission. |
| F4, registered controls | The repository generator did not execute scaling or global-mode-order gates. The reviewer's standalone checker executed both and passed. The result narrative now separates those checks from generator checks. No new post-result gate was added. |
| F5, route independence | The two repository routes reduce to the same modal quadratic, chiefly testing transcription. The reviewer's separate discretization provides a different numerical route. |
| F6–F7, source and licence | The v17 documentation branch and separate documentation/code licences were verified. The manual's reference label differs from the GPL deck's test tag. The cited third-party Samtech report was unavailable; no report/deck/figure is copied and no rights in it are inferred. |
| F8–F9, model and tolerance | The admitted claim is the ideal one-dimensional beam. The 3D comparison and physical/application tolerance remain outside scope. Display precision does not qualify an artifact class. |
| F10, observable | The specification now names XY-plane strong-axis bending explicitly. |
| F11, historical status | The specification's pending-execution status is a preserved registration snapshot. The current admission status is this record and the admission ledger. The interval is half-open as its convention field and implementation state. |
| F12, distinctness | Dynamic Timoshenko eigenfrequency, support conditions and published source define a distinct base problem from the earlier static Euler-Bernoulli cantilever. |
| F13, registration | Git preserves the specification before execution and the later source-description correction. The first-mode computation and gate were unchanged by reconciliation. |

The review recommended admission after the F2, F3, F4 and F10 corrections.
We admit only the first XY-plane analytical frequency as a second firm
published-reference development base problem. The official manual's first
printed answer is reproduced from its dimensions and equation; its conflicting
inertia display is explicitly excluded. This is a scoped technical decision,
not admission of the entire SDLV302 3D test or its higher modes. Benchmark
labels, artifact sufficiency, costs and pilot work remain gated.

Reproduce the reviewer calculation from the repository root:
The checker uses NumPy for its separate Galerkin discretization.

```sh
python3 -I reports/sdlv302-modal/claude-review/independent_check.py reports/sdlv302-modal/results.json > /tmp/sdlv302-review-rerun.json
cmp /tmp/sdlv302-review-rerun.json reports/sdlv302-modal/claude-review/independent_results.json
shasum -a 256 reports/sdlv302-modal/claude-review/REPORT.md
```

The standalone checker and `cmp` passed byte-for-byte during reconciliation.
The later specification edits only clarify source/observable wording and
provenance; the generated result's specification hash is refreshed, while
its numerical fields and decisions remain unchanged. The report pins the
pre-reconciliation technical commit, and the final diff is reviewed separately.
Downloaded Code_Aster pages and figures remain outside the repository. The
small [HTML text helper](html_text.py) can parse a fresh local fetch, while
raw page hashes in the report record the actual reviewed fetches.
