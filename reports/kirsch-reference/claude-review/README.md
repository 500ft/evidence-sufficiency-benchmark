# Reconciled scoped Claude AI technical review

The verbatim [review report](REPORT.md), [reviewer-authored independent checker](independent_check.py), [independent output](independent_results.json) and [input hashes](input-hashes.txt) are retained here. The report reviewed technical commit `190871bed8de6a3e350322b2fd17ac6840dcad28`. Its SHA-256 is `611108338c43185441c2eb53ee91dcf014baeece1280d8bee73972d4814e4dbf`. The checker and output hashes are in the report and can be rechecked with `shasum -a 256` or `hashlib`. The original files also remain in the external task handoff. No vendor pages or FE decks are redistributed.

The actual CLI response confirms Claude Opus 5.5 (`claude-opus-5-5`), Claude Code session `82b83c51-fd15-4b9c-99cf-76cf8fdadf78`, successful exit and no completed Write tool call. The model build is unknown. The review is non-blind: the reviewer saw the specification, implementation and expected outputs before its own calculation. Its checker imports no repository reference routine and uses complex potentials, rational stress checks and independent boundary integration. This is separately derived computation by an exposed AI reviewer, not independent authorship, human review, external peer review, FE validation or a scored pilot. The report's statement that the timeout cut its review short is imprecise: the CLI exited successfully before its configured timeout. The reviewer did not inspect LE1 external pages; the repository's [separate conditional audit](../le1-audit.md) did.

The reviewer recommended admission of the exact-restriction holed-plate claim after the following documentation corrections. The numeric result, gates and retained pilot were not edited in reconciliation.

| Finding | Verified disposition |
| :--- | :--- |
| F1, all-level hypothesis and changed gate | Confirmed from the commit history and retained pilot. The initial all-level closure hypothesis failed. The postpilot amendment added levels and changed the gate to the finest level without changing budgets. The [result narrative](../matrix.md) states both; an original all-level pass is not claimed. Independently integrated exact resultants in the reviewer output establish the mathematical boundary closure separately. |
| F2, displacement/plane-stress evidence gap | The reviewer independently derived complex-potential displacements, checked symmetry and plane-stress Hooke residuals, and found no contradiction. This evidence is reviewer-authored and non-blind; the repository's own generator remains stress-only. |
| F3, auxiliary unregistered settings | Confirmed by inspection. The [result narrative](../matrix.md) now points to `run.py` as the home of auxiliary grids, derivative step and far-field gate. The specification remains the home of primary budgets and sweep. |
| F4, Airy tautologies | Confirmed analytically. Divergence and contour closure of a smooth Airy field test implementation and orientation; independent complex-potential and rational checks provide the stronger cross-check. The narrative now distinguishes them. |
| F5, zero-load sensitivity | Confirmed: zero load is an offset control, not proof against load-proportional mistakes. The narrative now says so. |
| F6, initial pilot command | The first command was not retained and is not reconstructed as historical fact. The reviewer reproduced the pilot from the original archived commit; its exact reproduction command is in the report. The failed data remain unchanged. |
| F7, wording | The narrative clarifies the hole-circle coordinate guard, all five contour segments and the limited symmetry-based material independence. The original specification and reviewed technical snapshot remain preserved in Git. |

To reproduce the reviewer's check without importing project code:

```sh
python3 -I reports/kirsch-reference/claude-review/independent_check.py reports/kirsch-reference/results.json reports/kirsch-reference/pilot-failures.json > /tmp/kirsch-review-rerun.json
cmp /tmp/kirsch-review-rerun.json reports/kirsch-reference/claude-review/independent_results.json
```

That command reproduced the committed independent output byte-for-byte during reconciliation. Later commit `6ca7392` changed only the committed-result regression: Linux and macOS differ at roundoff scale in floating diagnostics, so the test compares those fields within a tighter reproduction tolerance while `build()` still enforces every original scientific gate. The Claude reviewer did not review this test-only follow-up; specification, generator, pilot and numerical result hashes remain those of the reviewed technical commit. The supported admission is **one derived development base problem**: the ideal plane-stress exact-restriction quarter plate, with full Kirsch traction on both artificial outer edges, traction-free circular hole, symmetry displacement constraints and the specified hole-hoop-stress claim. It covers the registered development inputs only. It does not count as a firm published-reference problem, freeze artifact labels or enlarge the reviewer pilot scope. LE1 remains excluded. The [current admission ledger](../../reference-admission/README.md) holds the count.
