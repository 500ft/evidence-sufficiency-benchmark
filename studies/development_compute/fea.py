"""Eligibility assessment of the three retained records; no solver or GCI fit."""
import hashlib
import json
import math
from .experiment import ROOT


def assess():
    prior_path = ROOT / 'reports/fea-interpretation.json'
    prior = json.loads(prior_path.read_text())
    results = []
    specs = []
    for retained in prior['records']:
        path = ROOT / retained['source']
        data = json.loads(path.read_text())
        specs.append({k: data[k] for k in ('geometry_mm', 'material', 'load_case')})
        meshes = data['meshes']
        h = [m['element_size_mm'] for m in meshes]
        outcomes = {}
        for observable, unit in [('max_von_mises_mpa_at_hole', 'MPa'), ('max_displacement_mm', 'mm')]:
            y = [m[observable] for m in meshes]
            differences = [b-a for a, b in zip(y, y[1:])]
            reasons = []
            ratios = [a/b for a, b in zip(h, h[1:])]
            if len(h) < 3:
                reasons.append('Only one mesh in this local-refinement record; fewer than three grids.')
            elif any(a*b <= 0 for a, b in zip(differences, differences[1:])):
                reasons.append('Successive observable changes reverse sign; a single monotone leading-error power is unsupported.')
            else:
                # For h0>h1>h2 and p>0, (h0^p-h1^p)/(h1^p-h2^p)
                # exceeds its p->0 limit log(h0/h1)/log(h1/h2).
                observed = abs(differences[-2]/differences[-1])
                minimum = math.log(h[-3]/h[-2])/math.log(h[-2]/h[-1])
                if observed <= minimum:
                    reasons.append('Finest-three changes admit no positive leading-error order using the recorded target sizes.')
                else:
                    reasons.append('No demonstrated systematically similar local mesh family or asymptotic-order verification.')
            outcomes[observable] = {'unit': unit, 'values': y, 'successive_changes': differences,
                                    'eligible': False, 'reasons': reasons,
                                    'order': None, 'extrapolated': None, 'gci': None}
            if len(h) >= 3 and all(d > 0 for d in differences):
                outcomes[observable]['finest_difference_ratio'] = observed
                outcomes[observable]['positive_order_ratio_lower_bound'] = minimum
        results.append({'source': retained['source'], 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'target_size_mm': h,
                        'nominal_refinement_ratios': [a/b for a, b in zip(h, h[1:])],
                        'hole_divisions_per_line': [m.get('hole_divisions_per_line') for m in meshes],
                        'node_counts': [m['n_nodes'] for m in meshes],
                        'same_problem_within_record': True,
                        'mesh_scope': 'Unstructured 3D SOLID186; target edge size is not demonstrated effective h at a moving sampled peak.',
                        'solver_completed': retained['solver_completed'],
                        'reference_agrees': retained['reference_agrees'],
                        'retained_convergence_status': retained['convergence_status'],
                        'observables': outcomes})
    return {'status': 'GCI_unavailable', 'same_geometry_material_load_across_records': all(s == specs[0] for s in specs),
            'combination_exclusion': 'Local records change hole divisions 24 to 48 while global size coarsens 3 to 5 mm; neither belongs to the global-only refinement sequence. Counts cannot establish a common refinement ratio.',
            'records': results,
            'interpretation_sha256': hashlib.sha256(prior_path.read_bytes()).hexdigest()}
