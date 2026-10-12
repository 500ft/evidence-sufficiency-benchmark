"""Checkpointed focused continuation; completed pilot specimens are never rerun."""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import time

from .audit import HERE, ROOT, INPUTS, MANIFEST, investigate

THREADS=('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')


def dump(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def provenance():
    files=[*sorted(HERE.glob('*.py')), HERE/'manifest.json',HERE/'inputs.json',
           ROOT/'studies/reference_qualification/radial.py',ROOT/'studies/reference_qualification/reference.py',
           ROOT/'reports/development-compute/results.json']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


def summarize(rows):
    selected=[r['levels'][-1] for r in rows if r['new_resolution_qualified']]
    orders=[s['resolution_decision']['observed_order'] for s in selected if s['resolution_decision']['observed_order'] is not None]
    return {'specifications':len(rows),'prior_failed_specifications':sum(r['purpose']=='inherited_gate_failure' for r in rows),
            'controls':sum(r['purpose']=='control' for r in rows),
            'new_resolution_qualified':sum(r['new_resolution_qualified'] for r in rows),
            'unqualified_ids':[r['id'] for r in rows if not r['new_resolution_qualified']],
            'selected_steps':dict(sorted(Counter(str(r['selected_steps']) for r in rows if r['new_resolution_qualified']).items())),
            'observed_order_range':[min(orders),max(orders)] if orders else None,
            'max_exact_error_over_inherited_budget':max((max(s['exact_error_normalized'].values())/float(F(MANIFEST['budget_relative'])) for s in selected),default=None),
            'max_selected_normalized_balances':{k:max(s['normalized_checks'][k] for s in selected) for k in selected[0]['normalized_checks']} if selected else {},
            'max_dimensionless_condition':max((s['conditioning']['infinity_norm_condition'] for s in selected),default=None)}


def main():
    parser=argparse.ArgumentParser(__doc__)
    parser.add_argument('--phase',choices=('pilot','full'),required=True)
    parser.add_argument('--raw-dir',type=Path,required=True)
    args=parser.parse_args()
    if any(os.environ.get(v)!='1' for v in THREADS):
        raise SystemExit('All numerical thread controls must be one')
    raw=args.raw_dir.resolve()
    if ROOT==raw or ROOT in raw.parents:
        raise SystemExit('Raw directory must be outside repository')
    raw.mkdir(parents=True,exist_ok=True)
    checkpoint=raw/'checkpoint.json'
    logfile=raw/'cases.jsonl'
    provenance_now=provenance()
    prior_elapsed=0
    previous={}
    if checkpoint.exists():
        previous=json.loads(checkpoint.read_text())
        if previous['provenance']!=provenance_now:
            raise SystemExit('Source changed: preserve old run and choose a fresh raw directory')
        if previous['status']=='executed':
            raise SystemExit('Already completed; reuse results')
        prior_elapsed=previous['elapsed_seconds']
    rows=[json.loads(line) for line in logfile.read_text().splitlines()] if logfile.exists() else []
    done={r['id'] for r in rows}
    pilot_ids=set(MANIFEST['pilot_ids'])
    if args.phase=='full':
        if not pilot_ids <= done or 'pilot' not in previous:
            raise SystemExit('Completed measured pilot required')
        estimate=previous['pilot']['projected_total_seconds']
        size_estimate=previous['pilot']['projected_total_bytes']
        if estimate>MANIFEST['resources']['max_seconds'] or size_estimate>MANIFEST['resources']['max_bytes']:
            raise SystemExit('Pilot projection exceeds allowance')
    jobs=[i for i in INPUTS['cases'] if i['id'] not in done and (args.phase=='full' or i['id'] in pilot_ids)]
    started=time.monotonic()
    def state(status):
        rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)
        result={'status':status,'phase':args.phase,'pid':os.getpid(),'provenance':provenance_now,
                'elapsed_seconds':prior_elapsed+time.monotonic()-started,'peak_rss_bytes':rss,
                'completed_count':len(rows),'completed_ids':[r['id'] for r in rows],
                'pending_ids':[i['id'] for i in INPUTS['cases'] if i['id'] not in {r['id'] for r in rows}],
                'artifact_bytes':sum(p.stat().st_size for p in raw.iterdir() if p.is_file()),
                'workers':1,'threads':{k:os.environ[k] for k in THREADS}}
        if 'pilot' in previous:
            result['pilot']=previous['pilot']
        dump(checkpoint,result)
        return result
    with logfile.open('a') as stream:
        for item in jobs:
            progress=state('running')
            limits=MANIFEST['resources']
            if progress['elapsed_seconds']>=limits['max_seconds'] or progress['peak_rss_bytes']>=limits['max_rss_bytes'] or progress['artifact_bytes']>=limits['max_bytes']:
                state('resource_stopped')
                raise SystemExit('Resource stop; resumable checkpoint retained')
            try:
                row=investigate(item)
            except Exception:
                state('implementation_error')
                raise
            stream.write(json.dumps(row,allow_nan=False)+'\n')
            stream.flush()
            rows.append(row)
            state('running')
            print(f'{len(rows)}/{len(INPUTS["cases"])} {item["id"]}: {row["status"]}, N={row["selected_steps"]}',flush=True)
    final=state('pilot_executed' if args.phase=='pilot' else 'executed')
    if args.phase=='pilot':
        final['pilot']={'completed_ids':[r['id'] for r in rows], 'elapsed_seconds':final['elapsed_seconds'],
                        'peak_rss_bytes':final['peak_rss_bytes'], 'pid':final['pid'],
                        'projected_total_seconds':final['elapsed_seconds']*len(INPUTS['cases'])/len(rows)*2,
                        'projected_total_bytes':logfile.stat().st_size*len(INPUTS['cases'])/len(rows)*2}
        dump(checkpoint,final)
        dump(raw/'pilot-summary.json',summarize(rows))
    else:
        # Raw history retains all levels; public JSON retains compact per-case metrics.
        compact=[]
        for row in rows:
            item={k:v for k,v in row.items() if k!='levels'}
            item['levels']=[{k:v for k,v in level.items() if k not in ('output',)} for level in row['levels']]
            compact.append(item)
        result={'status':'executed_numerical_investigation_pending_human_admission',
                'provenance':provenance_now,'summary':summarize(rows),'cases':compact,
                'execution':final,'raw':{'file':logfile.name,'sha256':hashlib.sha256(logfile.read_bytes()).hexdigest(),'bytes':logfile.stat().st_size},
                'coverage':{'development_families':4,'admitted_problems':0},
                'preservation':'Original failed gate remains failed; no fault study, baseline or human admission was reopened.'}
        out=ROOT/'reports/cylinder-convergence'
        out.mkdir(parents=True,exist_ok=True)
        dump(out/'results.json',result)
    print(json.dumps({'execution':final,'summary':summarize(rows)},indent=2))


if __name__=='__main__':
    main()
