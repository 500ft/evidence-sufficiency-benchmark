# Claude AI technical review reconciliation

This ledger records which development problems have an accepted numerical
reference for a specified claim. **Five base problems are included at the
scopes below; one has a firm published reference (VM25). M1.2 remains
incomplete at 5/10 against its provisional coverage target, including 1/2
published-reference problems.** The generated
[reference qualification](../reference-qualification/matrix.md),
[development compute](../development-compute/matrix.md) and
[cylinder convergence](../cylinder-convergence/matrix.md) reports retain their
earlier zero-admission or pending-human-review statements as historical
snapshots. Their numeric sources are unchanged; this record gives the current
admission status. The original
[claim contract](../../studies/evidence_sufficiency/claims/spec.json),
[reference specification](../../studies/reference_qualification/spec.json),
numeric budgets and [convergence manifest](../../studies/cylinder_convergence/manifest.json)
also remain unchanged.

## Review provenance and verification

The owner authorized Claude AI technical review for this development gate.
The completed owner-supplied `REPORT.md` has SHA-256
`3200da8e7b588aeeeb83616303745b6b9dd530e32e88dfd79ec10160cedc2516`.
It reports Claude Opus 5.5 (`claude-opus-5-5`) in Claude Code CLI, session
`6652078a-15d2-4eed-89e5-6c7f7bb2b219` inferred from the scratchpad path;
the model build is unknown. Its reviewed technical snapshot was
`d2ef04c64842c79302425a8adddfa0e31d8cabea`. The owner's original
report, script, results and source lists remain in the review handoff. They
were not rewritten or copied into the public repository. The supplied
`independent_checks.py` has SHA-256
`c1af9a27589c4df78a0a2ccf535b12ac6ad8e32748db285d2b809f794c3aa7c6`.
Its `results.json` has SHA-256
`5616095abac315550eca1fdf161468c2386d985bcd38c9c0658fa3c0f3d93806`;
`source-hashes.txt` has SHA-256
`3c13f19913f008c8b56e077f91222b7d4c7d9173dbcdcb37d2b22dfa58a93b00`.
All non-Markdown files in its source-hash list matched the reviewed commit;
subsequent edits through the protocol decision changed only documentation.

The review was **not blind**: the reviewer had already seen the repository
reference implementations, specification, reference matrix and published
targets. Its script imports no repository reference routine and separately
computes the claims, but it was written by the exposed reviewer. This is a
separately derived calculation, not independent authorship, human review,
external peer review, physical validation or a scored reviewer pilot. Running
the unchanged reviewer script from a separate scratch directory reproduced
all entries of its supplied `results.json`. The focused
[reproducer](review_repro.py) and its
[output](reproduction.json) independently recheck the consequential VM92 and
cylinder observations using specification inputs and retained results as data.

Fresh fetches of the official [VM25](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/ans_vm/Hlp_V_VM25.html),
[VM25 input](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/ans_vm/Hlp_V_VM25TXT.html)
and [VM92](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/ans_vm/Hlp_V_VM92.html)
pages confirmed the cited inputs, loading and displays. The original raw
SHA-256 entries in [sources.json](../../studies/reference_qualification/sources.json)
remain historical as-fetched pins. The separate
[versioned content hashes](../../studies/reference_qualification/source-content-hashes.json)
record two fresh raw hashes per page, their matching canonical visible-text
hashes, URLs by source key and the exact
[hash method](source_text_hash.py).
The v3 parser also removes uppercase and spaced script/style tags; the inspected pages'
digests remain identical to the reviewer's hashes. Stability across two fetches
does not guarantee permanent stability or redistribution
rights. No vendor page bytes are committed.

## Case dispositions

In the table, *admitted* means accepted as a development reference for the
stated model and observable after technical review. It does not establish a
final artifact label, an engineering acceptance limit or reviewer performance.

| Base problem | Admission and supported claim scope | Published-reference count |
| :--- | :--- | :---: |
| Axial response | **Admitted**, one fixed-left uniform bar problem. Force and prescribed-displacement configurations; stress in MPa and deflection in mm under the [finite explanation contract](../../studies/evidence_sufficiency/claims/spec.json). The force-controlled stress/deflection witness is scoped to its declared explanations. | No |
| Distributed-load bending | **Admitted**, one repository-authored Euler-Bernoulli cantilever with uniform dead load, ideal clamp, nominal root stress and the specified tip/reaction observables. Exact-arithmetic reference and consistent-load stiffness route; excluded shear, gravity, local clamp stress and nonlinear behavior are outside the claims. | No |
| Pressure-only thick cylinder | **Admitted**, one VM25 published-reference problem. Open-end, zero axial end resultant and free uniform axial strain; specified radial/hoop stress locations and radial displacement in inch/psi. The RK4 qualification covers only declared inputs at their qualified resolutions. Original coarse failures remain failed. Rotation and end-cap loading are excluded. | Yes |
| Steady conduction | **Admitted as a derived problem**, one VM92-parameter wall with convection films, perfect contact and exact-input heat balance; the MFiX slab is a control within this family. The published VM92 heat-rate and inner-face displays provide coarse corroboration. The disputed printed outer-face target is excluded from published corroboration and from the published-reference count. Exact equations and values are unchanged. | No |
| Holed-plate elasticity | **Admitted as a derived problem** after a separate [non-blind Claude AI technical review](../kirsch-reference/claude-review/README.md), one ideal plane-stress quarter-square exact restriction of the remote-y Kirsch field. Full position-dependent traction, including shear, is applied on both artificial outer edges. The traction-free hole and symmetry constraints support the specified hoop-stress claim at the +x hole point. The initial all-level quadrature hypothesis failed; a postpilot finer-level decision rule passes at the registered inputs. No finite-edge uniform-load or LE1 published target is admitted. | No |

These admissions qualify the stated **development reference problems**. They
do not freeze defect labels, validate physical artifacts or establish a
selection-policy benchmark. Claim tolerances are serialization or numerical
solver budgets, not engineering allowables. Published display precision is
separate from those budgets.

The later [VM92 artifact-class demonstration](../vm92-artifact-evidence/matrix.md)
applies an explicit interval rule to exact output, declared display conventions
and a conditional numerical-solver bound. It does not change this admission:
the source's rounding convention is unverified, and the printed outer target
remains excluded from published corroboration.

The Kirsch review is a separate later admission. The provenance and verification section above documents the original four-family review only; the [Kirsch record](../kirsch-reference/claude-review/README.md) pins its own reviewed commit, exposed model/session, independent calculations and finding dispositions. Its admission changes coverage, not the historical hashes or dispositions below.

## Finding resolution and boundaries

| Finding | Reconciliation |
| :--- | :--- |
| **F1, VM92 display:** reproduced discrepancy | The [exact-input comparison](../reference-qualification/matrix.md#vm92-layered-wall) and [focused reproduction](reproduction.json) put the outer value outside nearest-unit rounding of the printed target. [Two inspected early Kreith copies](../../studies/vm92_early_sources.json) print that target, tracing it to the textbook lineage, but the cited 1959 printing and final-value convention remain unverified. Truncation or intermediate rounding can reproduce the printout; neither has been established as its rule. VM92 remains admitted only as derived. The heat-rate and inner-face displays are coarse support; the outer printed value is excluded. The source equation and local exact values remain intact. |
| **F2, Ansys page hashes:** reproduced provenance defect | Fresh raw pages differed across requests and from the earlier raw pins. The pins remain dated as-fetched history. [Canonical-text hashes and method](../../studies/reference_qualification/source-content-hashes.json) now permit current content comparison without storing vendor pages. Two matching fetches establish only this observation, not permanent stability. |
| **F3, cylinder trapezoid:** verified limitation, no claim-value defect | The [focused reproduction](reproduction.json) evaluates the trapezoid balance on the exact Lamé field, where integration error is zero, and compares it with the retained RK4-field residual. Their closeness shows the residual is dominated by quadrature for this nominal check. It does not isolate an RK4 error fraction. The separate [Simpson equilibrium and energy audit](../cylinder-convergence/matrix.md) supplies the stronger declared checks. No budget or test was relaxed. |
| **F4, VM25 rotation:** verified exclusion | The official VM25 input listing uses a separate rotation load step and different axial constraint. Its rotation target is outside this pressure-only claim. Substitution into the reviewer's stated thin-disk formula reproduces the printed target, but the source does not label it a thin-disk solution. No rotating-cylinder reference is admitted here. |
| **R1, artifact class:** label-freeze prerequisite | The admitted references describe exact-arithmetic/serialized outputs or the specified RK4 solver budget. M1.3 must declare which artifact classes each decision tolerance judges and justify any new class-specific margin before labels are frozen. The existing budgets remain unchanged. |
| **R2, explanation set and labels:** label-freeze prerequisite | Axial sufficiency is valid only for the declared finite explanation set and known loading. The reviewer's doubled-prescribed-displacement counterexample changes that contract; it is not a current compatible explanation. A broadened set needs new claim-specific witnesses and truth labels. A smaller observation tolerance alone does not universally resolve ambiguity; the proposed evidence and decision margins must be proved. Area mutation under displacement control does not make stress or deflection wrong merely by name. |
| **R3, beam model:** scoped exclusion | The admitted claim is ideal Euler-Bernoulli bending. Shear, self-weight, local clamp stress and geometric nonlinearity were excluded in the specification. A quoted shear estimate assumed an undeclared Poisson ratio, so it is not adopted as a case result. No physical small-error guarantee is inferred. |
| **R4, cylinder zero-load budget:** scoped control | The declared zero-load control has exact-zero output and budget. No absolute floor is added to the preserved specification. A later artifact class with roundoff at zero needs a separately justified rule before label freeze. |
| **R5, cylinder domain:** scoped exclusion | The [registered convergence result](../cylinder-convergence/matrix.md) supports only its declared inputs and selected resolutions. Observed order is not a uniform error guarantee; original coarse failures remain failed. Any new input domain requires its own qualification. |

The later [public artifact-rule witnesses](../artifact-rule-witnesses/matrix.md) execute R1–R5 boundaries for the admitted development scopes. This does not retroactively change the review findings or freeze final labels; any broader explanation class or application tolerance still needs its own declaration and review.

The reviewer's statement that the trapezoid percentage can be attributed to
quadrature is narrowed here: the two residuals can partially cancel, so their
ratio is not a rigorous error decomposition. Its suggested universal remedy
of simply lowering the axial observation tolerance is also rejected for the
reason in R2. These corrections do not alter a numerical reference.

## Reproduce the reconciliation

From the repository root:

```sh
python3 reports/reference-admission/review_repro.py
python3 reports/reference-admission/source_text_hash.py /path/to/fresh/vm25.html /path/to/fresh/vm25-input.html /path/to/fresh/vm92.html
.venv/bin/pytest -q
```

The first command should match [reproduction.json](reproduction.json).
For the second, fetch each URL from `sources.json` to scratch space, run it on
two independently fetched copies of each page, and compare the output and raw
SHA-256 to `source-content-hashes.json`. Do not substitute an old raw hash for
the canonical digest. These commands do not access reserved cases.

Checks executed for this reconciliation:

| Command or operation | Observed result |
| :--- | :--- |
| Copy the supplied `independent_checks.py` to scratch; `python3 -I independent_checks.py <checkout>`; compare its JSON with the untouched supplied `results.json` | All 50 keys matched. The supplied original files were not overwritten. |
| `python3 reports/reference-admission/review_repro.py > /tmp/repro.json`; `cmp /tmp/repro.json reports/reference-admission/reproduction.json` | Byte-identical. |
| Fetch each Ansys URL in `sources.json` twice with `curl --fail --location --silent --show-error --max-time 30 --header 'Cache-Control: no-cache'`; run `source_text_hash.py` on all six scratch files and compare raw SHA-256 | Raw hashes differed for each pair; both canonical hashes for each page matched `source-content-hashes.json` and the supplied reviewer record. The v3 uppercase and spaced-tag controls also passed. |
| `.venv/bin/pytest -q` | 189 passed, 2 skipped. |
| `.venv/bin/engineering-audit eval benchmark/ --report /tmp/evidence-review-reconcile-benchmark.md` | 17 passed, 0 failed, 2 skipped. |
| `git diff --check`; check links and heading anchors in the changed Markdown | Passed. |

M1.2 still needs distinct base problems with complete specifications,
independent answers and technical review to meet its provisional target; any
target change requires an explicit decision. Before M1.3 fixes final labels,
resolve the R1–R5 questions for artifact classes, allowed explanations and
application decision errors at each accepted claim scope. Numerical solver
budgets and source-display intervals remain separate quantities. The
applicable-check and cost matrix, baselines, scored reviewer pilot, optional
human comparison, CAD/FEA host work and publication retain their own
prerequisites and approvals.
