from fractions import Fraction as F
import math
import pytest
from studies.cylinder_convergence.audit import (
    INPUTS, MANIFEST, fields, simpson, resolution_decision, decimal_output,
)
from studies.reference_qualification import reference, radial


def params(identity):
    return {k:F(v) for k,v in next(x for x in INPUTS['cases'] if x['id']==identity)['parameters'].items()}


def test_registered_population_and_legacy_failures():
    assert len(INPUTS['cases'])==99
    assert sum(not x['legacy_qualified'] for x in INPUTS['cases'])==96
    assert len({x['id'] for x in INPUTS['cases']})==99
    for x in INPUTS['cases']:
        if x['purpose']=='inherited_gate_failure':
            assert F(x['parameters']['outer_radius_in'])/F(x['parameters']['inner_radius_in']) in (4,8)
    assert F(MANIFEST['budget_relative'])==F(1,1000000)


def test_simpson_and_hydrostatic_limits():
    assert simpson([float(F(i,8)**3) for i in range(9)],1/8)==pytest.approx(1/4)
    with pytest.raises(ValueError):
        simpson([0,1,2,3],1)
    p=params('equal_pressure_prior_196')
    out=fields(p,64)
    # Uniform in-plane pressure: sr=st=-P; u=-(1-nu)*P*r/E.
    a,b,e,nu,pressure=(p[k] for k in ('inner_radius_in','outer_radius_in','modulus_psi','poisson_ratio','internal_pressure_psi'))
    exact_energy=(1-nu)*pressure**2*(b*b-a*a)/e
    assert out['energy_over_pi_psi_in2']==pytest.approx(float(exact_energy),rel=1e-12)
    assert out['output']['inner_displacement']==pytest.approx(float(-(1-nu)*pressure*a/e),rel=1e-12)
    assert max(out['normalized_checks'].values())<1e-10
    zero=fields(params('zero_pressure'),64)
    assert all(x==0 for x in zero['output'].values())
    assert all(x==0 for x in zero['normalized_checks'].values())


@pytest.mark.parametrize('identity',['prior_153','prior_210'])
def test_minimal_counterexamples_and_independent_energy(identity):
    p=params(identity)
    out=fields(p,512)
    legacy,_=radial.solve(p,512)
    assert out['output']==pytest.approx(legacy,rel=1e-12,abs=1e-12)
    a,b,e,nu,pi,po=(p[k] for k in ('inner_radius_in','outer_radius_in','modulus_psi','poisson_ratio','internal_pressure_psi','external_pressure_psi'))
    # Analytically integrated strain energy, separate from sampled Simpson fields.
    A=(pi*a*a-po*b*b)/(b*b-a*a)
    B=(pi-po)*a*a*b*b/(b*b-a*a)
    exact=((1-nu)*A*A*(b*b-a*a)+(1+nu)*B*B*(1/a**2-1/b**2))/e
    assert out['energy_over_pi_psi_in2']==pytest.approx(float(exact),rel=1e-7)
    assert out['conditioning']['determinant']==pytest.approx(float(a/b),rel=1e-8)
    assert max(out['normalized_checks'].values())<float(F(MANIFEST['budget_relative']))


def test_resolution_gate_cannot_accept_without_balances_or_order():
    levels=[]
    for n in (32,64,128):
        levels.append({'output':{'u':2+1/n**4},'normalized_checks':{'energy':0}})
    decision=resolution_decision(levels,{'u':1})
    assert decision['accepted'] and decision['observed_order']==pytest.approx(4,abs=1e-6)
    levels[-1]['normalized_checks']['energy']=1e-5
    assert not resolution_decision(levels,{'u':1})['accepted']
    levels[-1]['normalized_checks']['energy']=0
    levels[-1]['output']['u']=3
    assert not resolution_decision(levels,{'u':1})['accepted']
    assert not resolution_decision(levels[:2],{'u':1})['accepted']


def test_decimal_truncation_and_end_conventions():
    p=params('prior_210')
    decimal=decimal_output(p)
    exact=reference.cylinder(p)
    binary,_=radial.solve(p,32)
    # 50-digit arithmetic retains the coarse-grid error; roundoff is much smaller.
    error=abs(float(decimal['inner_displacement'])-float(exact['inner_displacement']))
    arithmetic=abs(float(decimal['inner_displacement'])-binary['inner_displacement'])
    assert error>1e6*arithmetic and error>1e-8
    a,b,e,nu,pi,po=(p[k] for k in ('inner_radius_in','outer_radius_in','modulus_psi','poisson_ratio','internal_pressure_psi','external_pressure_psi'))
    A=(pi*a*a-po*b*b)/(b*b-a*a)
    B=(pi-po)*a*a*b*b/(b*b-a*a)
    plane_strain=(1+nu)*((1-2*nu)*A*a+B/a)/e
    closed=((1-2*nu)*A*a+(1+nu)*B/a)/e
    numerical=fields(p,512)['output']['inner_displacement']
    budget=float(a*max(pi,po)/e*F(MANIFEST['budget_relative']))
    assert abs(numerical-float(exact['inner_displacement']))<budget
    assert abs(numerical-float(plane_strain))>budget
    assert abs(numerical-float(closed))>budget


def test_truth_audit_cannot_retune_resolution(monkeypatch):
    from studies.cylinder_convergence.audit import investigate
    item=next(c for c in INPUTS['cases'] if c['id']=='prior_153')
    original=reference.cylinder
    monkeypatch.setattr(reference,'cylinder',lambda p:{k:v+F(100) for k,v in original(p).items()})
    result=investigate(item)
    assert result['selected_steps']==128
    assert not result['new_resolution_qualified']
    assert result['legacy_qualified'] is False


def test_executed_results_independent_energy_and_preservation():
    import json
    from studies.cylinder_convergence.audit import ROOT
    from studies.cylinder_convergence.run import provenance,summarize
    from scripts.report_cylinder_convergence import table
    result=json.loads((ROOT/'reports/cylinder-convergence/results.json').read_text())
    assert result['provenance']==provenance()
    assert result['summary']==summarize(result['cases'])
    assert len(result['cases'])==len({c['id'] for c in result['cases']})==99
    assert (ROOT/'reports/cylinder-convergence/matrix.md').read_text()==table(result)
    assert sum(not c['legacy_qualified'] for c in result['cases'])==96
    assert all(c['new_resolution_qualified'] for c in result['cases'])
    for c in result['cases']:
        p={k:F(v) for k,v in c['parameters'].items()}
        a,b,e,nu,pi,po=(p[k] for k in ('inner_radius_in','outer_radius_in','modulus_psi','poisson_ratio','internal_pressure_psi','external_pressure_psi'))
        A=(pi*a*a-po*b*b)/(b*b-a*a); B=(pi-po)*a*a*b*b/(b*b-a*a)
        integral=((1-nu)*A*A*(b*b-a*a)+(1+nu)*B*B*(1/a**2-1/b**2))/e
        scale=a*a*max(pi,po)**2/e
        fine=c['levels'][-1]
        if scale:
            assert abs(fine['energy_over_pi_psi_in2']-float(integral))/float(scale)<2.5e-7
        else:
            assert fine['energy_over_pi_psi_in2']==0
        assert max(fine['exact_error_normalized'].values())<=1e-6
        assert max(fine['normalized_checks'].values())<=2.5e-7
        assert fine['resolution_decision']['accepted']
    prior=json.loads((ROOT/'reports/development-compute/results.json').read_text())
    assert prior['sweeps']['vm25_pressure_only']['failed']==96
    assert result['coverage']['admitted_problems']==0
