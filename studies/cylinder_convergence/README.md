# Cylinder numerical resolution investigation

This follow-on study preserves the original coarse-grid failures and qualifies
a new resolution choice for those inputs only. The frozen [manifest](manifest.json)
and [inputs](inputs.json) precede its results. The original radial integrator and
closed-form implementation are unchanged and remain separate. No bending or
conduction sweep is repeated.

## Prospective numerical criteria

Let $P = \max(p_i, p_o)$, $S_u = aP/E$ and $S_{\mathrm{stress}} = P$, in inches and psi.
The inherited claim budget remains $B_j = 10^{-6} S_j$. For doubling radial steps,
$D_N = \max_j \lvert y_N - y_{N/2} \rvert / S_j$. If the error is $C h^4$ in the asymptotic regime,
the finest error is approximately $D_N/(2^4 - 1)$. This study requires three
levels, observed order between 3.5 and 4.5, and a safety-factored estimate
$2 D_N/15 \le 10^{-6}/4$. It also requires the independent balances below to fit
the same quarter-budget allocation. A roundoff-floor control can replace the
order check when both differences are negligible by the frozen rule.

This conditional estimate is not a rigorous error bound. After selecting a
resolution without the exact answer, all numerical observables must separately
agree with the rational closed-form answer within the original full budget.
An audit failure stays failed; it does not trigger truth-based retuning. The
original all-coarse-level gate is never relabeled.

The pressure-only open-end convention has $\sigma_z = 0$; radial tension is positive
and pressure is compressive. For numerical states recovered from the radial
ODE, use $\sigma_\theta = E u/r + \nu \sigma_r$. Independent composite Simpson
integrals check radial equilibrium and energy/work, per unit axial length:

```math
\begin{aligned}
\left[ r \sigma_r \right]_a^b &= \int_a^b \sigma_\theta \, dr \\
\frac{W}{2\pi} &= a p_i u(a) - b p_o u(b) \\
\frac{U}{\pi} &= \int_a^b \left( \sigma_r^2 + \sigma_\theta^2 - 2 \nu \sigma_r \sigma_\theta \right) \frac{r}{E} \, dr \\
\frac{W}{2\pi} &= \frac{U}{\pi}
\end{aligned}
```

The integral-equilibrium unit is psi*in. The energy/work unit here is psi*in^2
(force, since this is energy per unit axial length). Their scales are $aP$
and $a^2 P^2/E$. Simpson versus subsampled-Simpson differences separately
estimate quadrature error. They are not the existing trapezoid residual or the
RK4 output error. Both tractions are checked. Pure zero loading requires exact
zero outputs and balances, with no division by zero or invented order.

Dimensionless state $v = E u/(aP)$, $s = \sigma_r/P$, coordinate $\rho = r/a$ obeys
$v' = (1 - \nu^2) s - \nu v/\rho$, $s' = v/\rho^2 - (1 - \nu) s/\rho$.
The numerical fundamental matrix exposes shooting sensitivity without mixed-unit
condition numbers. A separate 50-digit implementation on the frozen diagnostic
controls distinguishes floating arithmetic from truncation. It shares the ODE,
so it is an arithmetic diagnostic, not an independent physical reference.
Tests separately reject constrained plane-strain and closed-end displacement
answers for the open-end contract.

## Scope and reproduction

The retained input outputs are pinned extracts of the prior public-development
JSONL and qualification report. They permit reproduction without redistributing
large raw files. Field integration is necessary to obtain the new energy and
equilibrium diagnostics, which were absent from the retained observables.
Only failed inputs and the named controls are processed. Parameter variants do
not create new families, reviewed labels or qualified benchmark problems.
The investigation itself made no case-admission decision. The later
[Claude AI technical review reconciliation](../../reports/reference-admission/README.md)
admits the pressure-only reference within its declared inputs and selected
resolutions. Policy, reserved-data and physical-validity gates remain unchanged.

## Executed result and reproduction

The [executed report](../../reports/cylinder-convergence/matrix.md) records
selected levels, errors, balance residuals, observed orders and conditioning.
The largest coarse failure persists in 50-digit arithmetic but shrinks with
fourth-order refinement. This supports under-resolution rather than a change
to the formula or constitutive convention. The independent energy/quadrature
gate sometimes requires finer resolution than output agreement alone.
The conditional estimate is checked against the exact reference after selection;
it does not establish a general rigorous bound outside the declared inputs.

```sh
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1
RAW_DIR=/absolute/path/outside/repository/cylinder-convergence
.venv/bin/pytest -q tests/test_cylinder_convergence.py
.venv/bin/python -m studies.cylinder_convergence.run --phase pilot --raw-dir "$RAW_DIR"
.venv/bin/python -m studies.cylinder_convergence.run --phase full --raw-dir "$RAW_DIR"
.venv/bin/python scripts/report_cylinder_convergence.py
```

Use a fresh raw directory for a new reproduction. The full phase reuses every
completed pilot row. An interrupted matching run resumes remaining IDs; a
completed run is reused. The checkpoint records PID, elapsed compute, RSS,
source hashes and pending IDs. It stops at the registered resource caps or
maximum resolution, retaining any unqualified result. Runtime/PID/RSS vary
by machine; binary64 diagnostics can vary at roundoff level. The outcome
criteria and immutable retained observations stay fixed.
