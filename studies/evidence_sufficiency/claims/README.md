# Claim-relative axial-bar development

Under prescribed force, observing the bar's stress settles whether its stress
agrees with the specification, but it does not settle the deflection decision.
The [executed table](../../../reports/claim-sufficiency/matrix.md) contains two
allowed implementations that produce the same observed stress and opposite
deflection decisions. This is the public development result for roadmap M1.1.

## Claim contract

[spec.json](spec.json) declares the claims and evidence contract, validated by
[schema.py](schema.py). Geometry, loads and implemented parameter variants are
read from the existing [foundation specification](../spec.json). They are not
copied into a second input table. The legacy verifier schema is unchanged.

| Field | Meaning |
| :--- | :--- |
| `claims` | Named observable, canonical unit, decision rule and absolute agreement tolerance |
| `observations` | Available observable, canonical unit and evidence compatibility tolerance |
| `cases` | Foundation case identifier and explicit force or displacement loading convention |
| `allowed_explanations` | Finite set of possible implementations, each referencing a foundation variant |
| `assumptions` | Physical model and allowed implementation uncertainty |
| `evidence_source_variant` | Retained artifact supplying the observed values |

The rule accepts a named output when it agrees with the original specification
within the declared absolute numerical tolerance, including the boundary.
The contract gives units in MPa, mm or N and adds no relative tolerance.
The claim-decision tolerance and the observation-compatibility tolerance serve
different comparisons. Neither supplies a physical design allowable or a
measurement-uncertainty interval.

**Artifact correctness** compares one executed output with the independent
answer for its named claim. **Evidence sufficiency** asks whether all allowed
implementations consistent with the observations produce the same correctness
decision. Agreement on acceptance or rejection settles that decision. Two
consistent implementations with opposite decisions demonstrate insufficiency.
If none fits the observations, the evidence is inconsistent. These are
separate fields in the
[numeric result](../../../reports/claim-sufficiency/results.json).

## Independent derivation and explanation boundary

The model is a uniform straight bar of length L, area A and elastic modulus E,
fixed at the left end and free to contract laterally. Linear elasticity, small
axial deformation, zero body force/inertia and zero thermal strain apply.
Equilibrium gives constant axial force N; Hooke's law gives strain N/(EA).

For prescribed force F, equilibrium alone gives stress sigma = F/A. Integrating
strain along the bar gives end deflection delta = FL/(EA). Stress has no modulus
dependence under this loading convention, whereas deflection varies inversely
with modulus. For prescribed displacement d, compatibility gives strain d/L,
so sigma = Ed/L and reaction = EAd/L; end deflection is d regardless of modulus.
Units close as MPa = N/mm² and FL/(EA) = mm. Increasing E drives force-controlled
deflection toward zero while increasing displacement-controlled stress.

The intended specification is fixed and known. Only the modulus used by the
implementation is uncertain: H1 uses the intended modulus and H2 uses the
existing half-modulus variant. Geometry, applied loading and the physical
assumptions remain fixed. These are implementation explanations, not competing
physical measurements of the material. Sufficiency is conditional on this
declared finite set. It does not establish correctness of arbitrary code,
material conformance, or performance over other defect families.

For the force-controlled case, both implementations predict the observed
stress, yet their deflections lead to opposite agreement decisions. Under
displacement control, observing stress rules out H2. The
[table](../../../reports/claim-sufficiency/matrix.md) compares unrounded values
for both configurations. They remain one mechanics family.

[evaluate.py](evaluate.py) derives compatibility and decisions from numerical
predictions. It does not use mutation names, historical full-tuple labels,
selector choices or scores as truth. The foundation's closed-form
[reference](../reference.py) predicts each explanation; the separate
[compliance artifact](../artifact.py) supplies its executed output. Regression
tests independently assemble a stiffness matrix, solve constrained nodal
displacements and recover force to verify both implementations and claim labels.

## Reproduce and verify

From the repository root after installing `.[test]`:

```bash
python -m studies.evidence_sufficiency.claims.run
pytest tests/test_claim_sufficiency.py tests/test_evidence_sufficiency.py
```

The runner reads the existing public executed rows and writes only
`reports/claim-sufficiency/results.json` and its generated Markdown table.
The JSON records SHA-256 hashes of the claim specification, computation source
and foundation source, plus a canonical JSON hash of the retained rows.
Presentation and selector metadata are not consumed as evidence.

Tests cover both loading conventions, opposite-decision witnesses, independent
stiffness recovery, inclusive and just-outside boundaries, separate evidence
and claim tolerances, rejection, inconsistent evidence, and invariance to
identifier changes and removal of legacy labels. Changing the observed
quantity also changes which decision is resolved, as the derivation requires.

The historical [full-tuple result](../README.md) and its reproduction command
remain intact. No selector comparison, independent-problem qualification,
reviewer evaluation, new FEA run or reserved-case evaluation is added here.
