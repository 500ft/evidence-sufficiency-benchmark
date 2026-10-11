"""Frozen public-development grids and bounded synthetic observation decisions."""
import copy
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

from studies.reference_qualification import assembled, radial, reference
from studies.reference_qualification.run import qualify

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / 'manifest.json').read_text())
SPEC = json.loads((ROOT / 'studies/reference_qualification/spec.json').read_text())
CASES = {c['id']: c for c in SPEC['cases']}


def grid(case_id):
    axes = MANIFEST['sweep'][case_id]['axes']
    for values in product(*axes.values()):
        case = copy.deepcopy(CASES[case_id])
        p = case['parameters']
        for key, value in zip(axes, values):
            if key == 'radius_ratio':
                p['outer_radius_in'] = str(F(p['inner_radius_in']) * F(value))
            elif key == 'pressure_pair_psi':
                p['internal_pressure_psi'], p['external_pressure_psi'] = value
            elif key == 'temperature_pair_F':
                p['hot_temperature_F'], p['ambient_temperature_F'] = value
            elif key == 'layer_length_factors':
                for i, factor in enumerate(value, 1):
                    p[f'layer{i}_ft'] = str(F(p[f'layer{i}_ft']) * F(factor))
            elif key == 'film_factors':
                for name, factor in zip(('inner', 'outer'), value):
                    k = f'{name}_h_Btu_per_hr_ft2_F'
                    p[k] = str(F(p[k]) * F(factor))
            elif key in ('k1_factor', 'k2_factor'):
                k = key[:2] + '_Btu_per_hr_ft_F'
                p[k] = str(F(p[k]) * F(value))
            else:
                p[key] = value
        yield case


def validate(case, diagnostic=True):
    result = qualify(case, {'id': 'sweep'})
    extra = []
    if diagnostic and case.get('model') == 'thick_cylinder':
        truth = reference.solve(case)
        for steps in MANIFEST['sweep'][case['id']]['diagnostic_steps']:
            output, diagnostics = radial.solve(reference.parameters(case), steps)
            extra.append({'steps': steps, 'output_binary64': output,
                          'absolute_error': {k: abs(v-float(truth[k])) for k, v in output.items()},
                          'diagnostics': diagnostics})
    return {'case_id': case['id'], 'parameters': case['parameters'],
            'qualification': result, 'diagnostic_refinements': extra}


def bounded_decision(signal, tolerance, error):
    if signal + error <= tolerance:
        return 'guaranteed_pass'
    if signal - error > tolerance:
        return 'guaranteed_detection'
    return 'error_dependent'


def boundary(predicate, low, high, steps):
    """Bracket a false-to-true transition; exact rationals preserve inclusivity."""
    if predicate(low):
        return {'status': 'already_true_at_lower', 'lower': str(low)}
    if not predicate(high):
        return {'status': 'no_crossing_in_domain', 'upper': str(high)}
    for _ in range(steps):
        middle = (low + high) / 2
        if predicate(middle):
            high = middle
        else:
            low = middle
    return {'status': 'bracketed', 'last_false': str(low), 'first_true': str(high)}


def fault_study(case_id):
    config = MANIFEST['faults']
    contract = config['cases'][case_id]
    original = CASES[case_id]
    nominal = reference.solve(original)
    cache = {}

    def evaluate(magnitude):
        if magnitude in cache:
            return cache[magnitude]
        changed = copy.deepcopy(original)
        p = changed['parameters']
        p[contract['parameter']] = str(F(p[contract['parameter']]) * (1-magnitude))
        validation = validate(changed, diagnostic=False)
        if not validation['qualification']['qualified_numerically']:
            raise ValueError(f'Fault specification failed qualification: {case_id}, {magnitude}')
        truth = reference.solve(changed)
        claims = {}
        for obs in contract['observables']:
            scale = abs(nominal[obs])
            if obs == 'outer_surface_temperature':
                scale = abs(nominal[obs] - F(original['parameters']['ambient_temperature_F']))
            assert scale > 0
            tolerance = scale * F(config['claim_tolerance_fraction'])
            observation_error = scale * F(config['bounded_observation_error_fraction'])
            numerical_error = F(0)
            if changed.get('model') == 'thick_cylinder':
                pressure = max(F(p['internal_pressure_psi']), F(p['external_pressure_psi']))
                characteristic = pressure
                if obs == 'inner_displacement':
                    characteristic *= F(p['inner_radius_in']) / F(p['modulus_psi'])
                numerical_error = characteristic * F(original['qualification']['relative_scale_budget'])
            signal = abs(truth[obs] - nominal[obs])
            total_error = observation_error + numerical_error
            unit = next(c['unit'] for c in original['claims'] if c['observable'] == obs)
            claims[obs] = {'unit': unit, 'scale_exact': str(scale),
                           'signal_exact': str(signal), 'tolerance_exact': str(tolerance),
                           'bounded_observation_error_exact': str(observation_error),
                           'numerical_budget_exact': str(numerical_error),
                           'artifact_correct_for_synthetic_claim': signal <= tolerance,
                           'decision': bounded_decision(signal, tolerance, total_error),
                           'exact_zero_signal': signal == 0}
        result = {'magnitude': str(magnitude), 'claims': claims, 'validation': validation}
        cache[magnitude] = result
        return result

    rows = [evaluate(F(m)) for m in config['magnitudes']]
    boundaries = {}
    search = config['boundary_search']
    low, high = map(F, search['bracket'])
    for obs in contract['observables']:
        boundaries[obs] = {
            name: boundary(lambda m: evaluate(m)['claims'][obs]['decision'] in decisions,
                           low, high, search['bisections'])
            for name, decisions in (
                ('leaves_guaranteed_pass', {'error_dependent', 'guaranteed_detection'}),
                ('enters_guaranteed_detection', {'guaranteed_detection'}))}
    # Controls execute the independent route. Steady models omit inertial/storage terms.
    nuisance = copy.deepcopy(original)
    nuisance['parameters']['nuisance_density_or_heat_capacity'] = '12345'
    nuisance_result = validate(nuisance, diagnostic=False)
    benign = copy.deepcopy(original)
    if benign.get('model') == 'thick_cylinder':
        benign['qualification']['steps'] = [256, 512]
    else:
        benign['partitions'] = [['0', '1/3', '2/3', '1']]
    benign_result = validate(benign, diagnostic=False)
    controls = {'correct': rows[0]['validation'], 'benign_refinement': benign_result,
                'nuisance': nuisance_result}
    assert all(r['qualification']['qualified_numerically'] for r in controls.values())
    assert reference.solve(nuisance) == nominal
    return {'case_id': case_id, 'parameter': contract['parameter'],
            'status': 'provisional_numerically_qualified', 'rows': rows,
            'boundaries': boundaries, 'controls': controls,
            'evaluated_magnitudes': [cache[m] for m in sorted(cache)]}
