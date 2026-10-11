"""Single-process campaign with bounded resources, raw JSONL and checkpoints."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path
import resource
import sys
import time

from .experiment import CASES, HERE, MANIFEST, ROOT, fault_study, grid, validate
from .fea import assess

THREAD_VARS = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
               'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS')


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def provenance():
    paths = [*sorted(HERE.glob('*.py')), HERE/'manifest.json',
             *sorted((ROOT/'studies/reference_qualification').glob('*.py')),
             ROOT/'studies/reference_qualification/spec.json',
             ROOT/'reports/reference-qualification/results.json',
             ROOT/'reports/claim-sufficiency/results.json',
             ROOT/'cadloop/fea/run_fea.py']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def rss_bytes():
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss if sys.platform == 'darwin' else rss*1024


def summary(records):
    groups = {}
    for row in records:
        case_id = row['case_id']
        group = groups.setdefault(case_id, {'evaluated': 0, 'qualified': 0, 'failed': 0,
                                           'claim_comparisons': 0, 'failed_claim_comparisons': 0,
                                           'max_error_over_budget_by_steps': {}, 'first_failure': None})
        group['evaluated'] += 1
        q = row['qualification']
        passed = q['qualified_numerically']
        group['qualified' if passed else 'failed'] += 1
        for run in q['cross_checks']:
            group['claim_comparisons'] += len(run['agreement'])
            group['failed_claim_comparisons'] += sum(not v for v in run['agreement'].values())
        if 'steps' in q['cross_checks'][0]:
            budgets = q['cross_checks'][0]['cross_method_absolute_tolerance']
            for run in q['cross_checks'] + row['diagnostic_refinements']:
                ratios = [e/budgets[k] if budgets[k] else (0.0 if e == 0 else float('inf'))
                          for k, e in run['absolute_error'].items()]
                key = str(run['steps'])
                group['max_error_over_budget_by_steps'][key] = max(max(ratios), group['max_error_over_budget_by_steps'].get(key, 0))
        if not passed and group['first_failure'] is None:
            # Complete minimal input and route outcomes, sufficient to reproduce independently.
            group['first_failure'] = row
    return groups


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument('--phase', choices=('pilot', 'full'), required=True)
    parser.add_argument('--raw-dir', type=Path, required=True)
    args = parser.parse_args()
    for name in THREAD_VARS:
        if os.environ.get(name) != '1':
            raise SystemExit(f'{name}=1 required for this campaign')
    raw = args.raw_dir.resolve()
    if raw == ROOT or ROOT in raw.parents:
        raise SystemExit('Raw campaign artifacts must be outside the repository')
    raw.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    checkpoint = raw/f'{args.phase}-checkpoint.json'
    log = raw/f'{args.phase}.jsonl'
    metadata = {'phase': args.phase, 'provenance': provenance(), 'pid': os.getpid(),
                'workers': 1, 'thread_environment': {k: os.environ[k] for k in THREAD_VARS},
                'seed': MANIFEST['seed']}
    records = []
    prior_seconds = 0
    if checkpoint.exists():
        previous = json.loads(checkpoint.read_text())
        if previous['provenance'] != metadata['provenance']:
            raise SystemExit('Checkpoint code/input hashes changed; use a new raw directory')
        if previous['status'] == 'executed':
            raise SystemExit('Already executed; reuse the completed output')
        prior_seconds = previous['elapsed_seconds']
        if log.exists():
            records = [json.loads(line) for line in log.read_text().splitlines()]
    total = sum(sum(1 for _ in grid(k)) for k in MANIFEST['sweep'])
    if args.phase == 'pilot':
        jobs = [(case_id, c) for case_id in MANIFEST['sweep']
                for c in [CASES[case_id], *itertools.islice(grid(case_id), 2)]]
    else:
        pilot = json.loads((raw/'pilot-checkpoint.json').read_text())
        if pilot['status'] != 'executed' or pilot['provenance'] != metadata['provenance']:
            raise SystemExit('A completed matching pilot is required')
        if not pilot['independent_validation_passed']:
            raise SystemExit('Pilot independent validation failed')
        if pilot['projected_full_seconds'] + pilot['elapsed_seconds'] > MANIFEST['resources']['max_seconds'] or pilot['projected_full_bytes'] > MANIFEST['resources']['max_new_bytes']:
            raise SystemExit('Pilot projection exceeds allocation')
        jobs = [(case_id, c) for case_id in MANIFEST['sweep'] for c in grid(case_id)]

    def progress(status):
        elapsed = prior_seconds + time.monotonic()-start
        size = sum(p.stat().st_size for p in raw.iterdir() if p.is_file())
        state = {**metadata, 'status': status, 'completed_grid_entries': len(records),
                 'next_index': len(records), 'elapsed_seconds': elapsed, 'peak_rss_bytes': rss_bytes(),
                 'raw_directory_bytes': size, 'planned_grid_entries': len(jobs)}
        dump(checkpoint, state)
        return state

    with log.open('a') as stream:
        for _, case in jobs[len(records):]:
            state = progress('running')
            pilot_elapsed = pilot['elapsed_seconds'] if args.phase == 'full' else 0
            if state['elapsed_seconds'] + pilot_elapsed >= MANIFEST['resources']['max_seconds'] or state['peak_rss_bytes'] >= MANIFEST['resources']['rss_stop_bytes'] or state['raw_directory_bytes'] >= MANIFEST['resources']['max_new_bytes']:
                progress('resource_stopped')
                raise SystemExit('Resource cap: checkpoint retained; process stopped')
            row = validate(case)
            stream.write(json.dumps(row, allow_nan=False) + '\n')
            stream.flush()
            records.append(row)
            if len(records) % 50 == 0:
                print(f'{args.phase}: {len(records)}/{len(jobs)} entries, {time.monotonic()-start:.1f}s', flush=True)
    groups = summary(records)
    if args.phase == 'pilot':
        state = progress('executed')
        state['independent_validation_passed'] = all(r['qualification']['qualified_numerically'] for r in records)
        state['projected_full_seconds'] = state['elapsed_seconds']*total/len(records)*2
        state['projected_full_bytes'] = log.stat().st_size*total/len(records)*2
        dump(checkpoint, state)
        dump(raw/'pilot-summary.json', groups)
        print(json.dumps(state, indent=2))
        return

    faults = []
    for case_id in MANIFEST['faults']['cases']:
        # A coarse cylinder failure elsewhere cannot qualify that failed specification.
        # Nominal and each changed fault specification are checked separately below.
        if case_id != 'vm25_pressure_only' and groups[case_id]['failed']:
            faults.append({'case_id': case_id, 'status': 'blocked_by_exact_reference_failure'})
            continue
        faults.append(fault_study(case_id))
        dump(raw/'faults.json', faults)
        print(f'fault boundaries: {case_id} complete', flush=True)
    state = progress('executed')
    result = {'status': 'executed_provisional_development', 'provenance': metadata['provenance'],
              'seed': MANIFEST['seed'], 'sampling': MANIFEST['sampling'],
              'sweeps': groups,
              'faults': [{k: v for k, v in f.items() if k != 'evaluated_magnitudes'} for f in faults],
              'fault_evaluation_counts': {f['case_id']: len(f.get('evaluated_magnitudes', [])) for f in faults},
              'fea': assess(), 'exclusions': MANIFEST['excluded'],
              'coverage': {'development_families': 4, 'admitted_problems': 0, 'independent_human_reviews': 0},
              'execution': {'pilot': pilot, 'full': state},
              'raw_files': {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
                            for p in (log, raw/'faults.json', raw/'pilot.jsonl')}}
    output = ROOT/'reports/development-compute'
    output.mkdir(parents=True, exist_ok=True)
    dump(output/'results.json', result)
    print(json.dumps({'status': result['status'], 'elapsed_seconds': state['elapsed_seconds'],
                      'peak_rss_bytes': state['peak_rss_bytes'], 'raw_directory_bytes': state['raw_directory_bytes'],
                      'counts': {k: {n: v[n] for n in ('evaluated', 'qualified', 'failed')} for k, v in groups.items()}}, indent=2))


if __name__ == '__main__':
    main()
