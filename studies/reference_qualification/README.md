# Development reference qualification

The [executed matrix](../../reports/reference-qualification/matrix.md) compares
closed-form answers with independent stiffness and heat-balance solutions.
It extends the existing axial foundation with beam bending, thick-cylinder
elasticity and steady heat conduction, giving four distinct development families.
All problems are development candidates pending independent human
review. M1.2 remains incomplete; this is no admission or reviewer-performance
result.

## Contracts and coverage

[spec.json](spec.json) is the input home for exact rational parameters,
geometry, loading, claim locations, units, assumptions, controls and partitions.
The retained beam/slab use SI; VM25 uses inch/psi and VM92 uses foot/Btu/hour
and Fahrenheit temperature differences, explicitly named in every parameter.
Decimal strings represent exact specified model inputs, not measured precision.
[source records](sources.json) pin the inspected references by URL, section and
SHA-256. The references support the continuum equations and boundaries; the
local implementations and calculations were written separately.

| Family | Definition and reference | Separate route | Qualification boundary |
| :--- | :--- | :--- | :--- |
| Axial response | Existing [M1.1 contract](../evidence_sufficiency/claims/spec.json), [geometry/loading](../evidence_sufficiency/spec.json) and [derivation](../evidence_sufficiency/claims/README.md) | Existing [global stiffness tests](../../tests/test_evidence_sufficiency.py) | Reused unchanged; loading variants count once |
| Beam bending | Uniformly loaded rectangular cantilever, ideal clamp, free tip | Cubic Hermite stiffness assembly with consistent distributed loading | New authored parameter set; nominal beam stress and nodal deflection only |
| Thick-cylinder elasticity | VM25 pressure-only cylinder with zero axial end resultant | Radial equilibrium/constitutive BVP, independently stepped with RK4 shooting | Approximate cross-method values and step refinement; no rotation or end-cap load |
| Steady conduction | VM92 layered wall with film boundaries; retained MFiX FLD02 slab control | Local conduction/convection balances and interface continuity | One conduction family; no vendor solver reproduction or imported solver output |

The [generated JSON](../../reports/reference-qualification/results.json) holds
all computed values, exact fractions, per-partition checks and source hashes.
The Markdown matrix is a view of that JSON. Boundary and scaling controls do
not increase the family count. The existing end-point-loaded cantilever
regressions remain intact; the new bending case uses a distributed load and a
separate assembled route. The retained slab is a supporting conduction control and does not create a
fifth family. These families do not satisfy the provisional target of ten
qualified problems. VM142 and the proposed connector witness remain outside
this task.

## Independent admission review scope

The owner selected independent mechanics/heat-transfer review as the next gate.
Use the existing public specifications and results below. Review the reference
source scope and reuse rights, the derivation separately from its computational
cross-check, observable locations and units, decision tolerance, controls and
excluded physics. Record an explicit case-by-case disposition and any resolved
discrepancy before admitting a problem. Four families remain development
candidates, with none admitted; loading and parameter variants do not
increase the independent-problem count.

- **Axial response:** Read the [claim contract](../evidence_sufficiency/claims/spec.json),
  [force/displacement and geometry inputs](../evidence_sufficiency/spec.json),
  [analytic reference](../evidence_sufficiency/reference.py),
  [separate compliance artifact](../evidence_sufficiency/artifact.py) and
  [stiffness regressions](../../tests/test_evidence_sufficiency.py). Check the
  fixed-left bar under prescribed force and, separately, prescribed end
  displacement. Confirm stress in MPa and deflection in mm against the inclusive
  decision and observation tolerances in the claim contract's
  [`claims[*].absolute_tolerance` and `observations[*].absolute_tolerance`](../evidence_sufficiency/claims/spec.json)
  fields. Check the force-controlled modulus null space with opposite
  deflection decisions. Admit this family only if those assumptions,
  independent answer and finite explanation boundary support the
  stated claims; the historical full-response tuple has a different scope.
- **Distributed-load bending:** Read the [beam case](spec.json),
  [continuum derivation](reference.py), [Hermite stiffness and reaction route](assembled.py)
  and [regressions](../../tests/test_reference_qualification.py). Check signed
  uniform transverse dead load on the full span, an ideal left clamp, free
  right tip, rectangular section and nominal root stress without a local clamp
  concentration. Confirm tip deflection in m, root stress in Pa, reaction in N
  and couple in N*m. Check rational nodal/action agreement and serialized-value
  decisions against [`qualification_rule` and `numeric_claim_rule`](spec.json).
  Decide whether the observable and omitted shear, geometric nonlinearity and
  local stress effects permit the
  proposed claim before admission.
- **Pressure-only thick cylinder:** Read the [VM25-derived case](spec.json),
  [Lamé reference](reference.py), [independent radial BVP](radial.py),
  [wider-domain result](../../reports/development-compute/matrix.md) and
  [frozen convergence manifest](../cylinder_convergence/manifest.json) and
  [registered investigation](../cylinder_convergence/README.md).
  Check internal/external radial tractions, zero axial end resultant, free
  axial strain, tension-positive stresses and displacement in inch, with no
  rotation or end-cap pressure. Confirm the psi stress units and the inherited
  [case `qualification` fields](spec.json) `relative_scale_budget`,
  `stress_scale` and `displacement_scale`, then the manifest's
  `budget_relative`, `scales` and `new_resolution_gate`. Earlier coarse-step
  failures stay failed; selected finer resolutions have a separate convergence
  and energy audit. Decide which stated input domain
  and numerical rule can support admission without treating the conditional
  error estimate as a certified bound or using a plane-strain/closed-end value.
- **Steady conduction:** Read the [VM92 wall and MFiX slab cases](spec.json),
  [resistance/Fourier references](reference.py), [local heat-balance route](assembled.py)
  and [source comparison](../../reports/reference-qualification/matrix.md).
  Check prescribed slab face temperatures with insulated remaining faces,
  and, separately, wall fluid films, two layers, perfect contact and no
  generation or radiation. Confirm K and W/m² for slab values; degF and Btu/hr
  for wall values, with Fahrenheit used through differences. Check the
  independent rational heat balances and serialized-value decisions against
  [`qualification_rule` and `numeric_claim_rule`](spec.json).
  Resolve the VM92 displayed outer-wall value versus the exact-input value in
  the linked source comparison, which lies outside a nearest-unit rounding
  interval, or explicitly confine the display to coarse supporting evidence
  before treating it as a published-reference problem.
  The slab is a control within this family, not another admitted base problem.

The reviewer should return the specification/claim scope accepted, the
independence and budget rationale checked, each discrepancy with its resolution,
and any exclusion or revision needed. An unreviewed row remains a candidate.
The completed [synthetic fault-detectability result](../../reports/development-compute/matrix.md)
can inform later control design only within its declared bounded-error model;
it does not supply admission or empirical reviewer sensitivity. The retained
[FEA records](../../reports/fea-interpretation.json) have no eligible GCI.
The person, availability and review outcome are unresolved. No named referral
or signature is assumed.

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

## VM25 pressure-only thick cylinder

The [VM25 specification](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/ans_vm/Hlp_V_VM25.html)
and [pressure-step axial constraints](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/ans_vm/Hlp_V_VM25TXT.html)
define the source scope. The pinned input couples one end's axial displacement
while leaving its resultant free; no end-cap pressure is applied. Thus the
homogeneous solution has sigma_z = 0 and a uniform free axial strain.
Constraining that strain to zero or applying closed-end pressure changes radial
displacement. Rotation is a separate published case and is excluded here.
The source's exterior printout pressure is recorded as a numerical dummy; a
regression checks its effect against the local numerical budget. No vendor
input file or figure is redistributed.

For radii a,b and pressures pi,po, tension-positive radial traction is -pi at
a and -po at b. Equilibrium sigma_r' = (sigma_theta-sigma_r)/r, compatibility
and isotropic elasticity give

```
A = (pi*a² - po*b²)/(b²-a²); B = (pi-po)*a²*b²/(b²-a²)
sigma_r = A - B/r²; sigma_theta = A + B/r²
u_r = ((1-nu)*A*r + (1+nu)*B/r)/E     [sigma_z = 0]
```

Claims specify inner displacement and radial/hoop stress at the inner,
mid-thickness and outer radii. Units are inch and psi. The independent
[radial route](radial.py) never computes A or B. It integrates the state (u,s):

```
u' = (1-nu²)*s/E - nu*u/r
s' = E*u/r² - (1-nu)*s/r
```

Two RK4 trajectories and a scalar shooting solve enforce both radial tractions.
Step doubling checks the output error against the exact reference. A separate
trapezoid integral checks [r*sigma_r] = integral sigma_theta dr. Its second-order
residual is retained, separate from the fourth-order displacement error.
Tests cover zero pressure, modulus scaling and zero Poisson ratio, and reject
closed-end and plane-strain displacement as answers to this contract.

The cylinder's numeric claim and cross-method tolerance is one part per million
of max(pi,po) for stress and of a*max(pi,po)/E for displacement. These dimensions
come from traction and elastic compliance; the fraction is a declared development
accuracy budget, not a certified bound or physical allowable. All specified step
counts must meet it, and regression tests require refinement of both displacement
error and the separately recovered equilibrium residual. Published display
precision is a separate comparison and never supplies the truth labels.

## VM92 layered wall and evidence precision

The [VM92 specification](https://ansyshelp.ansys.com/public/Views/Secured/corp/v252/en/ans_vm/Hlp_V_VM92.html)
provides both layer thicknesses, conductivities, film coefficients, fluid
temperatures and area. These facts are stored once in the specification.
With perfect contact and no generation, each series path carries the same rate:

```
R = (1/hi + L1/k1 + L2/k2 + 1/ho)/area
Q = (Thot - Tambient)/R
Ti = Thot - Q/(hi*area); To = Tambient + Q/(ho*area)
Tinterface = Ti - Q*L1/(k1*area)
```

The independent assembly uses separate convection edges and partitioned layer
conductances, solves each nodal energy balance and recovers all edge heat rates.
It never calls the resistance formula. Interface continuity, reversed/equal
fluid temperatures and area scaling are checked. Fahrenheit values enter flux
calculations only through differences; adding a common temperature offset must
leave Q unchanged. Rates are Btu/hr and temperatures degF, with no implicit SI
conversion or misuse of absolute-temperature ratios.

The source labels its targets rounded-off. Local exact arithmetic and independent
balances determine the reference from inputs. The generated source comparison
shows the displayed target, derived value, difference, and half-/whole-display-unit
consistency. The outer target is outside a nearest-unit rounding interval even
though it is within a full display unit. The source does not specify a rounding
mode that resolves this last-digit discrepancy. Therefore the display is coarse
support only; it is never an acceptance target at 1e-8 or at serialization precision.
The exact value and other source comparisons are in the generated matrix rather
than a second hand-maintained numeric table. Source precision is not uncertainty
in a physical measurement, and no evidence-sufficiency label is inferred from
this coarse comparison.

## Decisions, tolerances and checks

For beam and conduction controls, qualification requires **exact equality** of
rational values from [reference.py](reference.py) and the independent assembly.
All declared model inputs and
beam/conduction matrix operations are rational, so there is no truncation or
floating-point solve tolerance hidden in those comparisons. The cylinder
uses its explicit independent numerical budget described above. A discrepancy
fails the runner.
This verifies the declared observables, not every possible solver output.

For beam/conduction output reporting a binary64 value, the explicit decision rule
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
source values; another plot would add little to this reference comparison.

Source documents were inspected and hashed, and are linked rather than
redistributed. No third-party figures, prose, solver code or output datasets
are bundled. Public accessibility does not establish permission for later
redistribution; the source records preserve that unresolved rights boundary.
The beam parameters are locally authored; the cylinder and thermal definitions
use published continuum setups. No candidate is an admitted benchmark problem.

Independent human review must examine the problem definitions, source scope,
derivations, observable choices, tolerance suitability and implementation
independence before admission. The suggested external title,
Evidence Sufficiency for Engineering Verification,
and a Gupta reviewer referral were historical recommendations. The owner
has different independent reviewer candidates in mind, with no appointment
or contact yet. No naming change has been adopted. No reserved families, new
defect campaign, reviewer pilot or CAD/FEA host run was added.
