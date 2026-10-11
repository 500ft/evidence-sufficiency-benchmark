#!/usr/bin/env python3
"""Render the compact executed study report without rerunning the campaign."""
from fractions import Fraction as F
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'reports/development-compute'
LABELS = {'cantilever_uniform_load': 'Cantilever', 'vm25_pressure_only': 'Pressure-only cylinder', 'vm92_layered_wall': 'Layered wall'}


def table(r):
    lines = ['# Development compute results', '',
             '**Executed synthetic development study. Independent human admission remains pending.**', '',
             'Source: [results.json](results.json). [Frozen domain and reproduction](../../studies/development_compute/README.md).', '',
             '## Reference sweep', '',
             '| Model | Parameter variants | Numerically qualified | Failed inherited gate | Claim comparisons | Failed comparisons |',
             '| :--- | ---: | ---: | ---: | ---: | ---: |']
    for k, v in r['sweeps'].items():
        lines.append(f'| {LABELS[k]} | {v["evaluated"]} | {v["qualified"]} | {v["failed"]} | {v["claim_comparisons"]} | {v["failed_claim_comparisons"]} |')
    lines += ['', 'Counts are parameter variants and comparisons within existing development families.',
              'Bending and conduction require exact rational agreement on every inherited partition.',
              'Cylinder qualification retains every inherited radial-step budget. Extra finer steps',
              'diagnose errors without changing a failed specification to a pass.', '',
              '| Cylinder radial steps | Largest absolute error / declared budget [1] |',
              '| ---: | ---: |']
    for steps, value in r['sweeps']['vm25_pressure_only']['max_error_over_budget_by_steps'].items():
        lines.append(f'| {steps} | {value:.6g} |')
    failure = r['sweeps']['vm25_pressure_only']['first_failure']
    p = failure['parameters']
    lines += ['', 'A complete minimal failure is retained in the numeric source, with all claim errors and diagnostics.',
              f'The first failure has a = {p["inner_radius_in"]} in, b = {p["outer_radius_in"]} in, '
              f'E = {p["modulus_psi"]} psi, nu = {p["poisson_ratio"]}, '
              f'internal pressure {p["internal_pressure_psi"]} psi and external pressure {p["external_pressure_psi"]} psi.',
              'The pressure-only, zero-end-resultant convention is unchanged. Radial tractions and',
              'trapezoid integrated-equilibrium residuals are in the raw records; that quadrature',
              'residual has its own error and is not the RK4 claim-error budget.', '',
              '## Conditional synthetic detectability', '',
              'Each nominal and changed specification passed its own independent numerical gate.',
              'Only the frozen public nominal specimens enter these fault studies; failed sweep specimens do not.',
              'The agreement tolerance is 1% of the declared scale, with bounded observation error of 0.2%.',
              'Cylinder observations also include the verified numerical budget. Temperature uses',
              'the outer-surface rise above ambient, avoiding a percentage of an affine absolute temperature.', '',
              '| Model / observable | Exit guaranteed-pass boundary [reduction %] | Enter guaranteed-detection boundary [reduction %] |',
              '| :--- | ---: | ---: |']
    def bracket(b):
        if b['status'] != 'bracketed':
            return 'No crossing in domain'
        return f'{100*float(F(b["last_false"])):.8f} to {100*float(F(b["first_true"])):.8f}'
    for f in r['faults']:
        for obs, b in f['boundaries'].items():
            lines.append(f'| {LABELS[f["case_id"]]} / {obs.replace("_", " ")} | {bracket(b["leaves_guaranteed_pass"])} | {bracket(b["enters_guaranteed_detection"])} |')
    lines += ['', 'Reduction means E for bending/cylinder and layer-2 conductivity for the wall.',
              'Each bracket runs from the last false predicate to the first true predicate in the',
              'frozen bisection. Pass is inclusive at the tolerance. Between these two boundaries,',
              'the decision depends on the bounded observation error; these are not probabilities.', '',
              'Bending root stress and cylinder hoop stress have an exact modulus null space under',
              'the specified loads. A nonzero deflection signal below tolerance has a different cause.',
              'Correct, benign-refinement and nuisance controls passed their numerical checks.',
              'All grid magnitudes, exact signals, tolerances, correctness decisions and control outcomes',
              'are retained in JSON; no mutation name or selection policy supplies truth.', '',
              '## Retained FEA eligibility', '',
              '| Record | Mesh count | Solver completed | Reference agrees | Retained stability status | Richardson / GCI |',
              '| :--- | ---: | :---: | :---: | :--- | :--- |']
    for record in r['fea']['records']:
        lines.append(f'| {Path(record["source"]).name} | {len(record["target_size_mm"])} | {record["solver_completed"]} | {record["reference_agrees"]} | {record["retained_convergence_status"]} | Unavailable |')
    for record in r['fea']['records']:
        lines += ['', f'**{Path(record["source"]).name}**', '']
        for obs, v in record['observables'].items():
            lines.append(f'- {obs} [{v["unit"]}]: ' + ' '.join(v['reasons']))
    disp = r['fea']['records'][0]['observables']['max_displacement_mm']
    lines += ['', f'The finest-three displacement-change ratio is {disp["finest_difference_ratio"]:.6g}; '
              f'a positive leading-error order with the recorded target sizes requires more than {disp["positive_order_ratio_lower_bound"]:.6g}.',
              r['fea']['combination_exclusion'],
              'The global unstructured meshes do not demonstrate systematic local similarity. No element-count-derived h or oscillation fit was used.', '',
              '## Execution and gates', '']
    full = r['execution']['full']
    lines += [f'The full run completed in {full["elapsed_seconds"]:.3f} s; recorded peak RSS was '
              f'{full["peak_rss_bytes"]/2**20:.2f} MiB and raw artifacts occupied {full["raw_directory_bytes"]} bytes at completion.',
              'One worker and one numerical thread were used. Sampling was deterministic; random seed and Monte Carlo are inapplicable.',
              'Raw file hashes, source hashes and checkpoint/resource metadata are in the numeric source.', '',
              f'Coverage remains {r["coverage"]["development_families"]} development families and {r["coverage"]["admitted_problems"]} admitted problems.', '',
              '- Holed plate: ' + r['exclusions']['holed_plate'],
              '- Baselines: ' + r['exclusions']['baselines'], '',
              'The VM92 published outer-wall display discrepancy remains in the parent qualification report.',
              'No new source-rights, naming, recruitment, publication, hardware or reserved-data decision is implied.']
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    result = json.loads((OUT/'results.json').read_text())
    (OUT/'matrix.md').write_text(table(result))
