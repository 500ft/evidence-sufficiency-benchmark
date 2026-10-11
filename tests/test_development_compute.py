"""Independent limits and decision boundaries for the executed development study."""
import copy
from fractions import Fraction as F
import json
import math

import pytest
from studies.development_compute.experiment import (
    CASES, MANIFEST, ROOT, boundary, bounded_decision, fault_study, grid, validate,
)
from studies.development_compute.fea import assess
from studies.reference_qualification import radial, reference


def test_grid_domains_and_counts():
    assert [sum(1 for _ in grid(k)) for k in MANIFEST['sweep']] == [72, 320, 486]
    for c in grid('cantilever_uniform_load'):
        p = reference.parameters(c)
        assert p['length_m']/p['height_m'] >= 30
    c = list(grid('vm92_layered_wall'))[-1]
    assert F(c['parameters']['layer1_ft']) == F(3, 2)
    assert F(c['parameters']['layer2_ft']) == F(5, 24)
    assert c['parameters']['hot_temperature_F'] == c['parameters']['ambient_temperature_F']


def test_independent_cylinder_equal_pressure_limit():
    # Uniform hydrostatic in-plane stress solves equilibrium at every radius.
    # sigma_z=0 gives epsilon_theta=-(1-nu)*pressure/E, hence u=a*epsilon_theta.
    case = copy.deepcopy(CASES['vm25_pressure_only'])
    case['parameters'].update(outer_radius_in='32', poisson_ratio='-1/2', external_pressure_psi='30000')
    p = reference.parameters(case)
    output, diagnostics = radial.solve(p, 128)
    exact_u = -p['inner_radius_in']*(1-p['poisson_ratio'])*p['internal_pressure_psi']/p['modulus_psi']
    assert output['inner_displacement'] == pytest.approx(float(exact_u), abs=1e-14)
    for key, value in output.items():
        if key.endswith('stress'):
            assert value == pytest.approx(-30000, abs=1e-7)
    assert abs(diagnostics['integrated_equilibrium_residual_psi_in']) < 1e-6


def test_cylinder_dimensions_under_length_and_pressure_rescaling():
    # All lengths scaled by lambda, pressure and E by mu: strain unchanged,
    # displacement multiplied by lambda, stress by mu. Independent BVP route.
    base = reference.parameters(CASES['vm25_pressure_only'])
    changed = dict(base)
    for k in ('inner_radius_in', 'outer_radius_in'):
        changed[k] *= F(127, 5)
    for k in ('modulus_psi', 'internal_pressure_psi', 'external_pressure_psi'):
        changed[k] *= F(689475729, 100000000000)
    a, _ = radial.solve(base, 128)
    b, _ = radial.solve(changed, 128)
    for k in a:
        scale = F(127, 5) if k == 'inner_displacement' else F(689475729, 100000000000)
        assert b[k] == pytest.approx(a[k]*float(scale), abs=1e-9, rel=1e-10)


def test_bounded_errors_and_inclusive_thresholds():
    t, e = F(1, 100), F(1, 500)
    assert bounded_decision(t-e, t, e) == 'guaranteed_pass'
    assert bounded_decision(t+e, t, e) == 'error_dependent'
    assert bounded_decision(t+e+F(1, 10**9), t, e) == 'guaranteed_detection'
    assert bounded_decision(F(0), t, e) == 'guaranteed_pass'
    result = boundary(lambda m: m > F(1, 8), F(0), F(1, 2), 24)
    assert F(result['last_false']) == F(1, 8)
    assert F(result['first_true']) > F(1, 8)


@pytest.mark.parametrize('case_id', list(MANIFEST['faults']['cases']))
def test_fault_boundaries_against_independent_algebra(case_id):
    result = fault_study(case_id)
    f = F(200, 273)  # R_layer2 / R_total = (25/6)/(91/16).
    eta = F(30, 59)*F(1, 1000000)  # cylinder a*p/E divided by nominal u.
    for obs, bounds in result['boundaries'].items():
        if obs.endswith('stress'):
            assert all(v['status'] == 'no_crossing_in_domain' for v in bounds.values())
            assert all(row['claims'][obs]['signal_exact'] == '0' for row in result['rows'])
            continue
        for name, alpha in [('leaves_guaranteed_pass', F(1, 125)),
                            ('enters_guaranteed_detection', F(3, 250))]:
            if case_id == 'vm92_layered_wall':
                root = alpha/(f+alpha*(1-f))
            else:
                correction = eta if case_id == 'vm25_pressure_only' else 0
                root = (alpha + (correction if name == 'enters_guaranteed_detection' else -correction))/(1+alpha)
            bound = bounds[name]
            assert F(bound['last_false']) <= root < F(bound['first_true'])
            assert F(bound['first_true'])-F(bound['last_false']) <= F(1, 2**25)
    assert all(r['qualification']['qualified_numerically'] for r in result['controls'].values())


def test_retained_fea_unavailable_for_both_observables():
    result = assess()
    assert result['same_geometry_material_load_across_records']
    assert [len(r['target_size_mm']) for r in result['records']] == [4, 1, 1]
    global_record = result['records'][0]
    stress = global_record['observables']['max_von_mises_mpa_at_hole']
    assert [math.copysign(1, d) for d in stress['successive_changes']] == [1, -1, 1]
    disp = global_record['observables']['max_displacement_mm']
    assert disp['finest_difference_ratio'] < disp['positive_order_ratio_lower_bound']
    # Independently evaluate positive powers: none reproduces the last-three ratio.
    for p in (0.01, 0.5, 1, 2, 4, 8):
        ratio = (3**p-2**p)/(2**p-1.5**p)
        assert ratio > disp['finest_difference_ratio']
    for r in result['records']:
        for out in r['observables'].values():
            assert not out['eligible'] and out['gci'] is None
    retained = json.loads((ROOT/'reports/fea-interpretation.json').read_text())
    assert retained['records'][0]['converged'] is False


def test_committed_report_provenance_and_retained_failures():
    import hashlib
    from scripts.report_development_compute import table
    from studies.development_compute.run import provenance
    result = json.loads((ROOT/'reports/development-compute/results.json').read_text())
    assert result['provenance'] == provenance()
    assert (ROOT/'reports/development-compute/matrix.md').read_text() == table(result)
    for case_id, group in result['sweeps'].items():
        assert group['evaluated'] == sum(1 for _ in grid(case_id))
        assert group['qualified'] + group['failed'] == group['evaluated']
        if group['first_failure']:
            failure = group['first_failure']
            case = copy.deepcopy(CASES[case_id])
            case['parameters'] = failure['parameters']
            reproduced = validate(case)
            assert not reproduced['qualification']['qualified_numerically']
            assert reproduced['parameters'] == failure['parameters']
    assert result['sweeps']['vm25_pressure_only']['failed'] > 0
    assert result['fea'] == assess()
    for record in result['fea']['records']:
        assert hashlib.sha256((ROOT/record['source']).read_bytes()).hexdigest() == record['sha256']
    assert result['coverage'] == {'development_families': 4, 'admitted_problems': 0, 'independent_human_reviews': 0}
    assert result['execution']['pilot']['independent_validation_passed']
    for phase in ('pilot', 'full'):
        assert result['execution'][phase]['status'] == 'executed'
        assert result['execution'][phase]['peak_rss_bytes'] < MANIFEST['resources']['rss_stop_bytes']
