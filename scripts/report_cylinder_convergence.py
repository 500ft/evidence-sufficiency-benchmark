#!/usr/bin/env python3
"""Render the registered cylinder investigation from its executed numeric source."""
from collections import Counter
from fractions import Fraction as F
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/cylinder-convergence'


def table(r):
    s=r['summary']
    lines=['# Cylinder convergence investigation','',
           f'**{s["new_resolution_qualified"]}/{s["specifications"]} inputs qualify at the prospectively selected resolution: '
           f'{s["prior_failed_specifications"]} earlier failures and {s["controls"]} controls.**','',
           'The original coarse-grid failures remain unchanged. This result qualifies numerical',
           'resolution for the declared linear cylinder equations; physical validity and human',
           'benchmark admission remain unestablished. No bending/wall grid or fault study was repeated.','',
           'Source: [results.json](results.json). [Derivation, frozen criteria and reproduction](../../studies/cylinder_convergence/README.md).','',
           '## Selected resolution','',
           '| Radial steps | Previously failing inputs | Controls |',
           '| ---: | ---: | ---: |']
    counts=Counter((c['purpose'],c['selected_steps']) for c in r['cases'])
    for n in sorted({c['selected_steps'] for c in r['cases'] if c['selected_steps'] is not None}):
        lines.append(f'| {n} | {counts[("inherited_gate_failure",n)]} | {counts[("control",n)]} |')
    lines+=['',f'Observed refinement orders range from {s["observed_order_range"][0]:.6f} to {s["observed_order_range"][1]:.6f} for non-roundoff-limited cases.',
            f'The maximum selected claim error is {s["max_exact_error_over_inherited_budget"]:.6g} times the original budget.',
            'Resolution selection uses successive numerical outputs and independent balance checks.',
            'The exact reference is consulted only after selection stops. No claim tolerance was increased.','',
            '## Why the inherited coarse grids failed','',
            '| Input | Steps | Largest claim error / original budget [1] | Energy/work residual / characteristic scale [1] | Selected |',
            '| :--- | ---: | ---: | ---: | :---: |']
    budget=float(F(json.loads((ROOT/'studies/cylinder_convergence/manifest.json').read_text())['budget_relative']))
    for identity in ('prior_153','prior_210'):
        c=next(c for c in r['cases'] if c['id']==identity)
        for level in c['levels']:
            lines.append(f'| {identity} | {level["steps"]} | {max(level["exact_error_normalized"].values())/budget:.6g} | {level["normalized_checks"]["energy_work"]:.6g} | {level["steps"]==c["selected_steps"]} |')
    lines+=['','The first retained failure and the worst retained coarse-grid failure show fourth-order',
            'truncation behavior. The stricter independent energy/quadrature check can require more',
            'steps than output agreement alone. All inputs and full diagnostic histories are linked',
            'from the frozen input file and numeric result.','',
            '| Arithmetic diagnostic | Maximum binary64 minus 50-digit output / scale [1] | Maximum 50-digit coarse error / scale [1] |',
            '| :--- | ---: | ---: |']
    for c in r['cases']:
        if 'arithmetic_diagnostic' in c:
            a=c['arithmetic_diagnostic']
            lines.append(f'| {c["id"]} | {max(a["binary64_difference_normalized"].values()):.6g} | {max(a["decimal_exact_error_normalized"].values()):.6g} |')
    lines+=['','High-precision arithmetic retains the coarse error. These diagnostics and the observed',
            'refinement support under-resolution as the mechanism; they do not indicate a formula',
            'or floating-arithmetic defect in the original integrator.',
            f'The largest selected dimensionless fundamental-matrix condition number is {s["max_dimensionless_condition"]:.6g}.',
            'The 50-digit route is an arithmetic diagnostic using the same ODE, not another physical reference.',
            'Pressure-only zero axial resultant is retained. Independent tests reject plane-strain',
            'and closed-end displacement answers for this convention.','',
            '## Independent balances','',
            '| Check | Largest selected residual or estimate / characteristic scale [1] | Allocation [1] |',
            '| :--- | ---: | ---: |']
    allocation=next(c for c in r['cases'] if c['new_resolution_qualified'])['levels'][-1]['resolution_decision']['allocation_relative']
    for name,value in s['max_selected_normalized_balances'].items():
        lines.append(f'| {name.replace("_"," ")} | {value:.6g} | {allocation:.6g} |')
    lines+=['','Equilibrium uses the scale aP [psi*in]; energy/work uses a²P²/E [psi*in²];',
            'tractions use P [psi]. Composite Simpson integrals and subsampled differences',
            'separate quadrature diagnostics from RK4 output errors. Exact zero and equal-pressure',
            'controls check the limiting cases. A separate analytic strain-energy integral verifies',
            'the reported numerical energy on every selected input.','',
            'The safety-factored step-difference estimate is conditional on observed asymptotic',
            'behavior. It is not a certified general error bound or a GCI for the historical FEA.','',
            '## Execution and remaining gates','']
    e=r['execution']
    lines += [f'Pilot plus focused sweep: {e["elapsed_seconds"]:.3f} s cumulative compute, '
              f'{e["peak_rss_bytes"]/2**20:.2f} MiB recorded peak RSS. One worker and one numerical thread;',
              'deterministic inputs, no random seed or Monte Carlo. Pilot rows were reused without',
              'duplication. Raw logs and checkpoint stay outside git; their hashes and execution',
              'metadata are retained in the source JSON.','',
              'Coverage remains four development families and zero admitted problems. Human review,',
              'reviewed labels and the applicable-check/cost matrix still gate policy baselines.',
              'The published wall-display discrepancy, retained FEA nonconvergence and owner decisions',
              'are unchanged. No new defect campaign, holed plate, host, hardware or reserved case was run.']
    return '\n'.join(lines)+'\n'


if __name__=='__main__':
    (OUT/'matrix.md').write_text(table(json.loads((OUT/'results.json').read_text())))
