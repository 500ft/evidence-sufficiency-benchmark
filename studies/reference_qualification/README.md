# Development reference qualification

The [executed matrix](../../reports/reference-qualification/matrix.md) compares
closed-form answers with independent stiffness and heat-balance solutions.
It extends the existing axial foundation with beam bending and steady heat
conduction. All problems are development candidates pending independent human
review. M1.2 remains incomplete; this is no admission or reviewer-performance
result.

## Contracts and coverage

[spec.json](spec.json) is the input home for exact rational SI parameters,
geometry, loading, claim locations, units, assumptions, controls and partitions.
Decimal strings represent exact specified model inputs, not measured precision.
[source records](sources.json) pin the inspected references by URL, section and
SHA-256. The references support the continuum equations and boundaries; the
local implementations and calculations were written separately.

| Family | Definition and reference | Separate route | Qualification boundary |
| :--- | :--- | :--- | :--- |
| Axial response | Existing [M1.1 contract](../evidence_sufficiency/claims/spec.json), [geometry/loading](../evidence_sufficiency/spec.json) and [derivation](../evidence_sufficiency/claims/README.md) | Existing [global stiffness tests](../../tests/test_evidence_sufficiency.py) | Reused unchanged; loading variants count once |
| Beam bending | Uniformly loaded rectangular cantilever, ideal clamp, free tip | Cubic Hermite stiffness assembly with consistent distributed loading | New authored parameter set; nominal beam stress and nodal deflection only |
| Steady conduction | MFiX FLD02 continuum slab with prescribed opposing face temperatures and insulated remaining faces | Local conductance balances on separate partitions | Published boundary-value definition; no MFiX solver reproduction or imported numerical output |

The [generated JSON](../../reports/reference-qualification/results.json) holds
all computed values, exact fractions, per-partition checks and source hashes.
The Markdown matrix is a view of that JSON. Boundary and scaling controls do
not increase the family count. The existing end-point-loaded cantilever
regressions remain intact; the new bending case uses a distributed load and a
separate assembled route. Thick-cylinder and plate-with-hole problems were not
added merely to increase coverage. VM142 and the proposed connector witness
remain outside this task.

## Bending derivation and independent route

Let x run from the clamp to the free tip, w be positive in the applied load
direction, and q be a signed uniform load per length. For rectangular width b
and bending height h, I = b h³/12. Section equilibrium gives the curvature
moment M(x) = q(L-x)²/2. Integrating EI w'' = M with w(0) = w'(0) = 0 gives

```
w(x) = q x² (6L² - 4Lx + x²) / (24EI)
w(L) = q L⁴ / (8EI)
|sigma_root| = |q| L² h / (4I)
R = -qL; C = -qL²/2
```

R and C are the support force and couple, with positive directions conjugate
to w and w'. Stress is the magnitude at the root extreme fiber. Force times
length divided by section modulus has units Pa; qL⁴/(EI) has units m.
These equations agree with the uniformly loaded cantilever shown on printed
p. 268 of [MIT's bending chapter](https://ocw.mit.edu/courses/1-050-solid-mechanics-fall-2004/f9a4d5764b9b0f51ffaacbdf69f7aed8_emech10_04.pdf).

The separate route makes the potential energy stationary, using
integrals of EI N''ᵢN''ⱼ for stiffness and qNᵢ for consistent nodal loading.
This follows the displacement energy formulation in
[MIT Lecture 8, section 8.3](https://ocw.mit.edu/courses/2-080j-structural-mechanics-fall-2013/2d0cc95bd3556fdadc28226acabafa51_MIT2_080JF13_Lecture8.pdf).
[assembled.py](assembled.py) assembles cubic Hermite elements, eliminates the
clamped DOFs, solves the rational system, and recovers support reactions from
Ku-f. Root stress is recovered from that reaction couple and the section
integral. It never calls the closed-form reference or a selector.

The piecewise cubic field does not reproduce the quartic continuum shape
inside an element. For this constant-EI uniform-load problem, nodal values and
support actions are exact; tests check the nodal field and global balance.
No continuum stress-convergence claim follows from matching these quantities.
The ideal beam omits shear deformation, clamp concentration and material
failure. The control's small deflection is checked, but physical validity is
not inferred from this numerical agreement.

## Conduction derivation and source discrepancy

The source is [MFiX VVUQ v1.3.1, section 3.2](https://mfix.netl.doe.gov/wp-content/uploads/2018/10/MDV3-VVUQ_v1.3.1.pdf),
printed pp. 41–43. The exact length, height, conductivity and face temperatures
are recorded in the local specification. With constant k, no generation and
no transverse heat flow, conservation gives (kT')' = 0. Applying both Dirichlet
conditions yields T(x) = T_left + (T_right-T_left)x/L and
j = -kT' = k(T_left-T_right)/L. The midpoint claim uses x=L/2. Flux j is signed
along +x in W/m². No slab depth or total heat-rate claim is needed.

Each interval in the independent route has conductance per unit area k/dx.
At an interior node, incoming and outgoing heat balance determines temperature.
After solving this system, flux is recovered on every interval. Equality of
all interval fluxes and both face temperatures are checked separately. This
linear solution is represented exactly on nonuniform as well as uniform
partitions; it does not measure a general spatial convergence rate.

**Source discrepancy:** [HTML Eq. (3.4)](https://mfix.netl.doe.gov/doc/vvuq-manual/main/html/fluid/fld-02.html#equation-fld02eq2)
omits the multiplier x. The pinned PDF Eq. (3-4) includes it. The literal HTML
expression has incorrect dimensions and cannot satisfy both distinct face
temperatures. The regression retains this counterexample. The local solution
uses the PDF and independently derived boundary-value solution; the published
solver's error figures were not imported as local evidence.

## Decisions, tolerances and checks

Reference qualification requires **exact equality** of rational values from
[reference.py](reference.py) and the independent assembly. All inputs and
matrix operations are rational, so there is no truncation or floating-point
solve tolerance hidden in that comparison. A discrepancy fails the runner.
This verifies the declared observables, not every possible solver output.

For a numeric artifact reporting a binary64 value, the explicit decision rule
is absolute error no greater than one ULP of the correctly rounded exact
reference, inclusive. Each tolerance is derived from that observable's value
and canonical unit via `math.ulp`; zero uses the smallest positive binary64
subnormal. This allows one adjacent representation for output serialization.
It is not an engineering allowable, model-error bound or a tolerance suitable
for general approximate FEA. Such artifacts would need their own justified
error budget before admission. The inherited axial contract and its tolerances
are unchanged.

Tests exercise both sides of tolerance boundaries, zero load, reversed load,
modulus scaling, equal face temperatures, reversed heat flow and conductivity
scaling. They check exact fields/balances and reject an injected bad deflection
without changing the stress result. Control identifiers do not define truth.
The local Gaussian solver also has a coupled-system and singular-system check.
Software route independence does not constitute independent human review.

## Reproduction and remaining qualification

```bash
python -m studies.reference_qualification.run
pytest tests/test_reference_qualification.py tests/test_claim_sufficiency.py tests/test_evidence_sufficiency.py
```

The runner uses only Python's standard library and existing public axial
results. It writes only the new result JSON and Markdown table. It does not
contact hosts or retrieve references at run time. Original axial results and
figures remain unchanged. Tables retain accessible text and full-precision
source values; another plot would add little to this exact comparison.

Source documents were inspected and hashed, and are linked rather than
redistributed. No third-party figures, prose, solver code or output datasets
are bundled. Public accessibility does not establish permission for later
redistribution; the source records preserve that unresolved rights boundary.
The beam's parameters are locally authored; the thermal problem uses the
published continuum setup. Neither is an admitted benchmark problem yet.

Independent human review must examine the problem definitions, source scope,
derivations, observable choices, tolerance suitability and implementation
independence before admission. The external title and reviewer remain
proposals. No reserved families, new defect campaign, reviewer pilot or
CAD/FEA host run was added.
