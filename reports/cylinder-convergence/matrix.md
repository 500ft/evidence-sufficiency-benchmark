# Cylinder convergence investigation

**99/99 inputs qualify at the prospectively selected resolution: 96 earlier failures and 3 controls.**

The original coarse-grid failures remain unchanged. This result qualifies numerical
resolution for the declared linear cylinder equations; physical validity and human
benchmark admission remain unestablished. No bending/wall grid or fault study was repeated.

Source: [results.json](results.json). [Derivation, frozen criteria and reproduction](../../studies/cylinder_convergence/README.md).

## Selected resolution

| Radial steps | Previously failing inputs | Controls |
| ---: | ---: | ---: |
| 128 | 12 | 3 |
| 256 | 36 | 0 |
| 512 | 48 | 0 |

Observed refinement orders range from 3.998735 to 4.010016 for non-roundoff-limited cases.
The maximum selected claim error is 0.00669941 times the original budget.
Resolution selection uses successive numerical outputs and independent balance checks.
The exact reference is consulted only after selection stops. No claim tolerance was increased.

## Why the inherited coarse grids failed

| Input | Steps | Largest claim error / original budget [1] | Energy/work residual / characteristic scale [1] | Selected |
| :--- | ---: | ---: | ---: | :---: |
| prior_153 | 32 | 1.71775 | 3.16612e-05 | False |
| prior_153 | 64 | 0.107433 | 2.0251e-06 | False |
| prior_153 | 128 | 0.00669941 | 1.27186e-07 | True |
| prior_210 | 32 | 122.784 | 0.00179072 | False |
| prior_210 | 64 | 7.76653 | 0.000130173 | False |
| prior_210 | 128 | 0.483114 | 8.50508e-06 | False |
| prior_210 | 256 | 0.0300368 | 5.37874e-07 | False |
| prior_210 | 512 | 0.00187103 | 3.37201e-08 | True |

The first retained failure and the worst retained coarse-grid failure show fourth-order
truncation behavior. The stricter independent energy/quadrature check can require more
steps than output agreement alone. All inputs and full diagnostic histories are linked
from the frozen input file and numeric result.

| Arithmetic diagnostic | Maximum binary64 minus 50-digit output / scale [1] | Maximum 50-digit coarse error / scale [1] |
| :--- | ---: | ---: |
| prior_153 | 9.72243e-17 | 1.71775e-06 |
| prior_210 | 5.36551e-16 | 0.000122784 |
| nominal | 5.42094e-16 | 7.191e-08 |

High-precision arithmetic retains the coarse error. These diagnostics and the observed
refinement support under-resolution as the mechanism; they do not indicate a formula
or floating-arithmetic defect in the original integrator.
The largest selected dimensionless fundamental-matrix condition number is 468.872.
The 50-digit route is an arithmetic diagnostic using the same ODE, not another physical reference.
Pressure-only zero axial resultant is retained. Independent tests reject plane-strain
and closed-end displacement answers for this convention.

## Independent balances

| Check | Largest selected residual or estimate / characteristic scale [1] | Allocation [1] |
| :--- | ---: | ---: |
| equilibrium | 4.83945e-08 | 2.5e-07 |
| energy work | 1.27186e-07 | 2.5e-07 |
| equilibrium quadrature estimate | 8.50487e-08 | 2.5e-07 |
| energy quadrature estimate | 2.26229e-07 | 2.5e-07 |
| inner traction | 0 | 2.5e-07 |
| outer traction | 1.21266e-16 | 2.5e-07 |

Equilibrium uses the scale aP [psi*in]; energy/work uses a²P²/E [psi*in²];
tractions use P [psi]. Composite Simpson integrals and subsampled differences
separate quadrature diagnostics from RK4 output errors. Exact zero and equal-pressure
controls check the limiting cases. A separate analytic strain-energy integral verifies
the reported numerical energy on every selected input.

The safety-factored step-difference estimate is conditional on observed asymptotic
behavior. It is not a certified general error bound or a GCI for the historical FEA.

## Execution and remaining gates

Pilot plus focused sweep: 0.552 s cumulative compute, 21.72 MiB recorded peak RSS. One worker and one numerical thread;
deterministic inputs, no random seed or Monte Carlo. Pilot rows were reused without
duplication. Raw logs and checkpoint stay outside git; their hashes and execution
metadata are retained in the source JSON.

Coverage remains four development families and zero admitted problems. Human review,
reviewed labels and the applicable-check/cost matrix still gate policy baselines.
The published wall-display discrepancy, retained FEA nonconvergence and owner decisions
are unchanged. No new defect campaign, holed plate, host, hardware or reserved case was run.
