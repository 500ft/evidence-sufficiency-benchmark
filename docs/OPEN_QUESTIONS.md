# Decisions and open questions

## AUD-1: bounded software adoption, 2026-10-06

Adopt the evidence-sufficiency question in [ROADMAP.md](../ROADMAP.md), with the
[executed result](../reports/evidence-sufficiency/matrix.md) in the same change.
Owner instruction: implement the reviewed v2 pivot and update the repository's
questions, figures and obsolete material while keeping useful work. The reviewed
handoff permits an independently checkable minimal result before expansion.
This records no hardware readiness, purchases, funding, human recruitment or
permission for external model spending.

## Superseded active questions

- The old priority to collect wild failures and execute the week-by-week v1
  schedule is superseded by AUD-1. It is not answered by challenge captures.
  Obsolete schedules were removed in the owner-directed cleanup;
  [history](history/README.md) links their pre-cleanup source. Captures remain intact.
- FEA implementation and parametric re-drive are recorded capabilities, so
  their old "not implemented" questions are closed with links to
  [CAD records](../cadloop/evidence/README.md) and
  [FEA interpretation](../reports/fea-interpretation.json).
- Mesh convergence remains unresolved for the hole-refined runs. Their close
  peaks under simultaneously changed global and local meshes are evidence of
  agreement between those discretizations, not an error bound.

## AUD-2: working copy

Use this clean isolated clone. The separate Developer working copy, including
its modified JSON and untracked instructions, was neither read nor changed.

## AUD-3: PR #5 review

[PR #5](https://github.com/500ft/evidence-sufficiency-benchmark/pull/5) contains only CodeQL,
Dependency Review and Dependabot configuration. Its diff and recorded successful
checks were inspected on 2026-10-06 at head
`f27458001d304cc179f05a1b99fef4bf6866d300`. Live inspection on 2026-10-07
confirmed that PR #5 and the substantive pivot [PR #10](https://github.com/500ft/evidence-sufficiency-benchmark/pull/10)
are merged. CI maintenance is not research evidence.
No new review of its action versions or rerun of its historical checks is claimed.

## AUD-4: dependency plan and cleanup adoption, 2026-10-07

The owner requested an active roadmap with no dates or schedule estimates,
prerequisites and completion evidence, plus actual removal of obsolete active
code and documentation. [ROADMAP.md](../ROADMAP.md) adopts that dependency plan
and is the sole active task list. This implements section 1 of the external
`ROADMAPS_20261007.md` handoff with the project-specific corrections.

The benchmark target in the roadmap includes its published-reference cases.
It remains subject to independent qualification. Holdout freezing moves before
reviewer or policy tuning. Applicability and setup plus execution costs are
required; defects must match the physics. The existing public bar example is
development evidence, not a qualified claim-specific or hidden benchmark.

The cleanup removes the old capture CLI, obsolete schedules, prompt-hardening
instructions and active requests to fill old capture slots. The
[history index](history/README.md) records the consumer checks and specific
retentions. This adoption does not authorize running the proposed experiments.

## AUD-5: bounded M1.1 implementation

The owner authorized implementation of the axial-bar claim contract and a
scoped review PR. The [executed claim matrix](../reports/claim-sufficiency/matrix.md)
separates artifact correctness from evidence sufficiency. It demonstrates
compatible explanations with opposite deflection decisions while resolving
stress agreement under force control. The
[derivation and tests](../studies/evidence_sufficiency/claims/README.md) include
the loading convention and decision boundaries. The original full-tuple
development result remains reproducible.

This authorization ends at M1.1. It supplies no independent problem review,
source reuse rights, model spending, host execution or reserved-case expansion.

## Bounded M1.2 development authorization

The owner authorized the weekly reference-qualification implementation.
The [executed candidates](../reports/reference-qualification/matrix.md) reuse
the axial foundation and add bending, cylinder and conduction specifications with
independent computational routes. This authorization covers development
qualification only. No problem has been admitted and no independent human
review has taken place. The research supplement suggested the external title
"Evidence Sufficiency for Engineering Verification" and a Gupta referral for
independent review. They are historical recommendations, not approvals. AUD-6
records the later owner decision to consider different reviewer candidates;
no naming change, reviewer appointment or contact is recorded.

## AUD-6: adopted admission order, 2026-10-12

The owner adopted independent reference admission as the next gate after the
merged [development qualification](../reports/reference-qualification/matrix.md)
and [cylinder investigation](../reports/cylinder-convergence/matrix.md).
The [family-specific review scope](../studies/reference_qualification/README.md#claude-ai-technical-review-scope)
names the contracts, independent methods, loading conventions and numerical
budgets that an independent mechanics/heat-transfer reviewer must assess.
Review and discrepancy resolution are required case by case before a problem
is admitted. The owner has different human reviewer candidates in mind; none
is appointed or contacted, and zero problems are admitted today.
AUD-7 changes the reviewer type while retaining this dependency order and
case-specific scope.

After admission, freeze claim truth, compatible-explanation witnesses and
reserved whole families. Then execute the applicable-check matrix with setup,
execution and shared costs. Only a reviewed matrix and cost model permit the
cost-matched rule table, checklist, random, sensitivity and greedy baselines.
The completed [synthetic fault-detectability study](../reports/development-compute/matrix.md)
is reusable within its stated error model; it is not a reviewer result. The
retained FEA evidence remains ineligible for Richardson/GCI. No model or
human pilot is approved by this decision.

For a conditional physical extension, self-funded equipment and independently
arranged space can satisfy an access route once the actual setup is qualified.
University lab membership is not a prerequisite. This supplies no equipment,
site, operating procedure, budget or permission for a physical run.

## AUD-7: Claude AI technical review for current admission

The owner authorized Claude AI technical review to satisfy the current
reference-admission review gate. This changes the reviewer requirement in
AUD-6: independent human review is deferred and is not a prerequisite for this
scoped development admission. The existing Claude reviewers are researching,
but their completed reports are not available. Assignment is not completion;
no case is admitted. The [family review scope](../studies/reference_qualification/README.md#claude-ai-technical-review-scope)
states the case-specific questions.

Before admission, each Claude AI technical review needs a pinned report with
reviewed commit and source hashes, model/session provenance where known, prior
exposure, independently derived checks, per-claim findings and dispositions.
Repository authors must reconcile findings, document resolutions and exclusions,
and decide admission case by case. A second AI session and an independently
derived calculation are different evidence; neither is called human review or
external peer review. The existing specification's historical review-status
field and generated numerical reports remain unchanged to preserve their
provenance; this decision record and roadmap state the current gate.

This technical reference review is separate from the future scored reviewer
pilot and optional human-comparison study. Their funding, exposure, recruitment
and authorization gates remain. No new model campaign, baseline study, reserved
data access, hardware run or publication follows from this decision.

## AUD-8: reconciled Claude AI technical review, 2026-10-12

The completed [case-by-case admission record](../reports/reference-admission/README.md)
reconciles the owner's supplied non-blind Claude AI technical report and
focused reproductions. It records the admitted development reference problems
and their published-reference count. VM92 is admitted as derived; its disputed
printed outer-wall target is excluded from published corroboration. M1.2
remains incomplete against its provisional target. This decision supersedes
the pending-admission status in AUD-6 and AUD-7. Their text and the generated
development report remain historical snapshots.

The original report hash, reviewed commit, model/session provenance, prior
exposure, separate calculation and finding dispositions are in the admission
record. Raw source hashes remain as-fetched history; a versioned canonical-text
method now documents the dynamic Ansys pages. R1–R5 remain prerequisites for
label freeze, with the proposed observation-tolerance shortcut rejected as a
general remedy. This admits reference problems only. It authorizes no labels,
cost matrix, baselines, scored reviewer pilot, human comparison or physical work.

## AUD-9: VM92 artifact-class rule

The owner authorized a bounded implementation of artifact-class and tolerance
rules on the existing derived VM92 wall before any new case. The
[executed result](../reports/vm92-artifact-evidence/matrix.md) keeps exact
control output, rounded source display and conditional numerical-solver output
distinct. It treats claim acceptance error, evidence precision and numerical
reference error as separate inputs. The source does not state a rounding
convention; the result records the conflicting conditional interpretations
without choosing one. The supplied later Kreith and Bohn edition did not
establish the cited earlier printing's display rule in the inspected passages.

The result does not alter the four scoped admissions, numerical budgets,
historical results or the disputed display exclusion. R1 has an executed VM92
example, while artifact classes and explanation sets for other claims remain
unfrozen. R2's broader compatible explanations need claim-specific witnesses;
R3's beam exclusions, R4's cylinder zero-load rule and R5's cylinder input
domain remain at their recorded scopes. M1.3 label freeze, new base problems,
policy costs and any pilot still require their own prerequisites.

## AUD-10: early Kreith source check

[Two visually inspected early Kreith copies](../studies/vm92_early_sources.json)
print the VM92 furnace-wall Example 2-5 and its disputed outer target. The
1958-copyright copy has no identified printing; the other explicitly states
third printing, August 1960. This improves provenance of the printed target.
Neither inspected page gives the final-value rounding convention or the
owner-reported intermediate value. The exact 1959 second printing cited by
Ansys remains uninspected. The [artifact-class result](../reports/vm92-artifact-evidence/matrix.md)
and derived-only admission retain the exact-input discrepancy, original
tolerances and exclusion from published corroboration.

## Remaining inputs and decisions

- M1.2 still needs distinct qualified problems to meet its provisional
  coverage target. The current admitted count and scope are in the [admission ledger](../reports/reference-admission/README.md); AUD-8 remains the historical four-family decision.
- R1–R5 in the admission record require resolution before M1.3 label freeze.
  The current admissions need no additional human-review gate.
- Model pilot execution and resources require separate owner authorization.
- Human comparison is optional and requires the institution's determination
  and separate authorization before recruitment.
- Host CAD/FEA execution, physical study, hardware, funding, purchases, naming
  and publication have no new approval here. Useful CAD position checks and
  latency questions remain outside this cleanup; see [CAD limitations](cad_fea_loop.md).
- Naming: Zhang and Wu 2026 already use the title "Evidence Sufficiency
  Benchmark" for an unrelated LLM abstention benchmark. See the README section
  [Prior work and positioning (2026-10-09)](../README.md#prior-work-and-positioning-2026-10-09)
  and [references.bib](references.bib). External write-ups need a
  distinguishing title; the repository name is unchanged and renaming remains
  an owner decision that has not been made.
- Reserved families must remain unexposed until the registered evaluation.
  No existing holdout was opened or used in this task.
