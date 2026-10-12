# Bounded development computation

The executed [result](../../reports/development-compute/matrix.md) extends the
four-family reference foundation from PR #21. It measures the limits of its
numerical gates across parameter grids and then evaluates eligible nominal
specimens under a synthetic observation model. The later
[Claude AI technical review reconciliation](../../reports/reference-admission/README.md)
admitted the four base development references at their stated scopes. The
generated result and frozen manifest retain their earlier admission status.

The [manifest](manifest.json) was committed before any campaign results in
`a6ae617`. It freezes the Cartesian axes, units, conventions, tolerances, error
model, boundary searches, exposure rules and resource caps. The manifest's null
seed means deterministic enumeration, with no random draws. Existing axial,
slab, historical FEA and reference-qualification outputs are reused unchanged.
The new parameter variants do not add independently qualified problems.

## Independent reference routes

The existing [derivations and implementations](../reference_qualification/README.md)
remain the source of the governing models and units. This study changes their
inputs only. The beam uses exact Hermite stiffness and consistent distributed
loads against continuum equilibrium/curvature; the wall uses exact nodal heat
balances against summed conduction and film resistance; the cylinder uses
radial constitutive/equilibrium ODE integration against Lamé's exact solution.
These are checks of idealized equations, with no physical model validation.

The beam grid covers reversed/zero loads, section dimensions, span and modulus.
Its minimum span/depth is checked. This sweep verifies the linear beam
equations without qualifying omitted geometric nonlinearity. Exact agreement concerns the declared nodal and
reaction observables, not the interpolated field everywhere in an element.
The wall grid spans conductivity contrasts, relative layer thickness, films,
area and zero/reversed temperature differences. Exact nodal conduction uses
piecewise linear fields with an explicit interface. Conductivities and film
coefficients remain constant even at the idealized VM92 temperatures.

The cylinder grid spans geometry scale, thickness ratio, modulus, stable
Poisson ratios and internal/external/equal pressure limits. No end-cap resultant
is added. The inherited coarse-step gate is preserved; additional finer steps
expose discretization error without rescuing failed specifications. The report
keeps a full first failing example, and every failing input remains in the raw
JSONL. Traction residuals, output errors and integrated equilibrium residuals
remain separate quantities. A wider valid domain would require a separately
reviewed numerical specification, not retrospective tolerance inflation.

## Synthetic observation decisions

For a selected claim, define exact discrepancy `d = |y_artifact - y_nominal|`,
frozen tolerance `t`, bounded observation error `e_obs` and independently checked
numerical budget `e_num`. The declared model has no probability distribution.
All errors are in the observable's unit. Agreement is inclusive:

- Guaranteed pass: `d + e_obs + e_num <= t`.
- Guaranteed detection: `d - e_obs - e_num > t`.
- Otherwise the result depends on the bounded error.

Artifact correctness for this synthetic claim is independently recorded as
`d <= t`. It is distinct from detection under bounded observations, and from
M1.1's explanation-set evidence sufficiency. No new general sufficiency label
or reviewer sensitivity is inferred. The new synthetic tolerance does not
replace PR #21's numerical qualification budget or a physical allowable.

For a fractional modulus reduction `m`, beam/cylinder displacement scales by
`1/(1-m)`, while the specified stress is independent of modulus. That exact
null space follows from equilibrium, not a fault name. For the wall,
`R(m) = R_other + R_layer2/(1-m)` and `Q(m) = delta_T/R(m)`.
The outer-wall rise is `Q/(h_outer*A)`, so it has the same normalized signal.
Tests independently solve these algebraic boundary equations and compare them
with the bisection brackets. Nonzero signals below tolerance remain distinct
from the exact stress null space. Correct, benign partition/refinement and
steady-state density/heat-capacity nuisance controls are retained.

Every evaluated magnitude is independently qualified before use. The raw file
contains the search evaluations, numerical errors and controls; the compact
result contains the grid magnitudes and boundary brackets. Failed cylinder
sweep specimens are never used for downstream decisions. Baseline policies
remain blocked by admission and the missing reviewed outcome/cost matrix.

## Retained FEA

The offline assessment reads the original geometry, material, loads, nominal
mesh sizes and two observables. Global peak stress changes sign during
refinement. Maximum displacement is monotone, but its finest-three increments
cannot fit a positive leading-error order even using nominal target sizes.
For `h0 > h1 > h2` and positive `p`, the ratio
`(h0^p-h1^p)/(h1^p-h2^p)` exceeds the limit
`log(h0/h1)/log(h1/h2)`; the recorded displacement ratio is below that limit.
This rules out that leading-error model for those grids, without fitting an
oscillatory sequence or claiming a bound from small absolute changes.

The individual locally refined records have only one mesh each; their global
size and hole divisions change in conflicting directions. They cannot be
combined into a consistent refinement sequence. No GCI is calculated. Original
solver-completion, reference-agreement and nonconvergence results are preserved.
The finite holed plate also lacks an admitted exact reference and a feasible
independent solve within this task; neither infinite Kirsch nor the different
VM142 finite geometry supplies its answer.

## Reproduction and resource use

From the repository root, choose a fresh raw directory outside the repository:

```sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
RAW_DIR=/absolute/path/outside/repository/development-compute
.venv/bin/pytest -q tests/test_development_compute.py tests/test_reference_qualification.py
.venv/bin/python -m studies.development_compute.run --phase pilot --raw-dir "$RAW_DIR"
.venv/bin/python -m studies.development_compute.run --phase full --raw-dir "$RAW_DIR"
.venv/bin/python scripts/report_development_compute.py
```

The measured pilot gates the full run against a conservative resource projection.
The runner logs each completed grid entry, flushes JSONL, records its PID and
next-index checkpoint, and stops at the frozen caps. A matching incomplete run
can resume with the same command and raw directory; an executed run is reused.
Changed input or code hashes require a fresh directory. Raw data stays outside
git, with hashes and compact executed outputs committed. Runtime, PID and RSS
are machine-dependent metadata; exact rational results and bracket endpoints
are deterministic. Binary64 radial errors may differ by platform roundoff.

The original VM92 display discrepancy, source-rights statements and pending
owner naming/reviewer recommendations remain in the parent documentation.
