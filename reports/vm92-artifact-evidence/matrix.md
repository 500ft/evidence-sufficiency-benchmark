# VM92 artifact class and evidence precision

This is a development decision-rule demonstration on the already admitted
derived wall problem. [results.json](results.json) is the numeric source.
The [reference specification](../../studies/reference_qualification/spec.json)
and [source record](../../studies/reference_qualification/sources.json)
remain unchanged, as does the historical qualification output.

The exact series-drop derivation gives resistance 91/16 hr degF/Btu,
heat rate 46720/91 Btu/hr and outer face
30640/91 degF. A separately assembled balance agrees exactly.
The original claim acceptance error is 1/17592186044416 degF;
numerical reference error here is 0 degF.
Neither is the precision of a printed source value or an engineering allowable.

| Artifact or evidence | Declared precision | Relation to exact reference | Claim decision |
| :--- | :--- | :--- | :--- |
| Exact rational assembled control | Exact | Equal | accept |
| Published 336 degF if nearest half away from zero | [671/2, 673/2) degF | incompatible | reject if treated as artifact |
| Published 336 degF if truncate toward zero | [336, 337) degF | compatible | ambiguous if treated as artifact |
| Binary64 projection as conditional numerical solver | Assumed output error 1/17592186044416 degF | Reference error remains zero | ambiguous |

The cited source gives no rounding convention. The two explicit conventions
give different source-compatibility outcomes, so the printed value remains
ambiguous and is excluded from published corroboration. Even a compatible
coarse display cannot establish acceptance at the claim precision. The
numerical-solver row is a conditional rule check, not an executed solver
measurement or a new admission. Reference error, output uncertainty and
claim acceptance error remain separate inputs. No VM92 explanation set is
frozen, so these are claim classifications, not evidence-sufficiency labels.

The owner-reported 336.54 degF has no verified source and is not an input.
The supplied Frank Kreith and Mark S. Bohn
Fourth Edition (1986) contains a different
one-layer SI wall example at printed pp. 28-29; its inspected printed p. 32
does not establish the VM92 display rule. The VM92 citation is to an earlier
1959 printing, which was not obtained. The supplied PDF SHA-256 is
`3c4f5bfa8fb6f0c4f22b5fb21e44e7ee129afeab056b18e5f69d911058f96c85`;
no book pages are redistributed.

Reproduce: `python -m studies.vm92_artifact_evidence`.
