"""Prospective resolution selection using ODE fields and independent balances."""
from decimal import Decimal as D, localcontext
from fractions import Fraction as F
import json
import math
from pathlib import Path
import sys

from studies.reference_qualification import radial, reference

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MANIFEST = json.loads((HERE/'manifest.json').read_text())
INPUTS = json.loads((HERE/'inputs.json').read_text())


def simpson(values, h):
    if (len(values)-1) % 2:
        raise ValueError('Simpson requires an even number of intervals')
    return h/3 * math.fsum([values[0], values[-1],
                           4*math.fsum(values[1:-1:2]), 2*math.fsum(values[2:-1:2])])


def fields(p, n):
    a, b, e, nu, pi, po = (float(p[k]) for k in (
        'inner_radius_in', 'outer_radius_in', 'modulus_psi', 'poisson_ratio',
        'internal_pressure_psi', 'external_pressure_psi'))
    base = radial.integrate(p, n, 0.0, -pi)
    basis = radial.integrate(p, n, 1.0, 0.0)
    u0 = (-po-base[-1][1])/basis[-1][1]
    states = [(u+u0*v, s+u0*t) for (u,s),(v,t) in zip(base,basis)]
    h = (b-a)/n
    radius = [a+j*h for j in range(n+1)]
    hoop = [e*u/r+nu*s for r,(u,s) in zip(radius,states)]
    energy = [(s*s+t*t-2*nu*s*t)*r/e for r,(_,s),t in zip(radius,states,hoop)]
    force_integral = simpson(hoop,h)
    energy_integral = simpson(energy,h)
    work = a*pi*states[0][0]-b*po*states[-1][0]
    eq = b*states[-1][1]-a*states[0][1]-force_integral
    balance = work-energy_integral
    pressure = max(pi,po)
    eq_scale, energy_scale = a*pressure, a*a*pressure*pressure/e
    normalize = lambda v, scale: abs(v)/scale if scale else (0.0 if v == 0 else math.inf)
    # Dimensionless fundamental matrix, not a condition number mixing inches/psi.
    stress_basis = radial.integrate(p,n,0.0,1.0)[-1]
    m11, m21 = basis[-1][0], basis[-1][1]*a/e
    m12, m22 = stress_basis[0]*e/a, stress_basis[1]
    determinant = m11*m22-m12*m21
    condition = max(abs(m11)+abs(m12),abs(m21)+abs(m22))*max(abs(m22)+abs(m12),abs(m21)+abs(m11))/abs(determinant)
    numerator = -po-base[-1][1]
    cancellation = (abs(po)+abs(base[-1][1]))/abs(numerator) if numerator else None
    output = {'inner_displacement': states[0][0]}
    for label, index in [('inner',0),('mid',n//2),('outer',n)]:
        output[label+'_radial_stress'] = states[index][1]
        output[label+'_hoop_stress'] = hoop[index]
    return {'steps':n, 'output':output,
            'equilibrium_residual_psi_in':eq, 'energy_work_residual_psi_in2':balance,
            'work_over_2pi_psi_in2':work, 'energy_over_pi_psi_in2':energy_integral,
            'normalized_checks': {
                'equilibrium':normalize(eq,eq_scale), 'energy_work':normalize(balance,energy_scale),
                'equilibrium_quadrature_estimate':normalize(2*abs(force_integral-simpson(hoop[::2],2*h))/15,eq_scale),
                'energy_quadrature_estimate':normalize(2*abs(energy_integral-simpson(energy[::2],2*h))/15,energy_scale),
                'inner_traction':normalize(states[0][1]+pi,pressure),
                'outer_traction':normalize(states[-1][1]+po,pressure)},
            'conditioning':{'dimensionless_fundamental_matrix':[[m11,m12],[m21,m22]],
                            'determinant':determinant, 'expected_determinant_a_over_b':a/b,
                            'infinity_norm_condition':condition,
                            'inverse_shooting_sensitivity':1/abs(m21),
                            'shooting_numerator_cancellation':cancellation}}


def scales(p, keys):
    pressure = max(p['internal_pressure_psi'],p['external_pressure_psi'])
    return {k:float(pressure*p['inner_radius_in']/p['modulus_psi'] if k == 'inner_displacement' else pressure) for k in keys}


def distance(a,b,s):
    values = [abs(a[k]-b[k])/s[k] if s[k] else (0.0 if a[k]==b[k] else math.inf) for k in a]
    return max(values)


def resolution_decision(levels, s):
    allocation = float(F(MANIFEST['budget_relative'])*F(MANIFEST['new_resolution_gate']['allocation_fraction']))
    if len(levels) < MANIFEST['new_resolution_gate']['minimum_levels']:
        return {'accepted':False,'reason':'needs_three_levels'}
    coarse, middle, fine = [v['output'] for v in levels[-3:]]
    before, latest = distance(coarse,middle,s),distance(middle,fine,s)
    magnitude = max([1.0]+[abs(v)/s[k] for k,v in fine.items() if s[k]])
    floor = 128*sys.float_info.epsilon*magnitude
    negligible = before <= floor and latest <= floor
    order = math.log2(before/latest) if before > 0 and latest > 0 else None
    low,high = MANIFEST['new_resolution_gate']['order_interval']
    convergence = negligible or (order is not None and low <= order <= high)
    estimate = floor if negligible else 2*latest/15
    balances = all(math.isfinite(v) and v <= allocation for v in levels[-1]['normalized_checks'].values())
    return {'accepted':convergence and estimate <= allocation and balances,
            'difference_previous':before,'difference_latest':latest,'observed_order':None if negligible else order,
            'order_status':'roundoff_limited' if negligible else 'observed',
            'roundoff_floor':floor,'conditional_error_estimate':estimate,
            'allocation_relative':allocation,'balance_checks_pass':balances}


def decimal_output(p, n=32):
    """Same numerical ODE in dimensionless 50-digit arithmetic; no closed form."""
    with localcontext() as ctx:
        ctx.prec = 50
        q = {k:D(v.numerator)/D(v.denominator) for k,v in p.items()}
        a,b,e,nu,pi,po = (q[k] for k in ('inner_radius_in','outer_radius_in','modulus_psi','poisson_ratio','internal_pressure_psi','external_pressure_psi'))
        pressure = max(pi,po)
        step = (b/a-1)/n
        def derivative(r,y):
            v,s = y
            return ((1-nu*nu)*s-nu*v/r, v/r**2-(1-nu)*s/r)
        def integrate(initial):
            states=[initial]
            for j in range(n):
                r,y=D(1)+j*step,states[-1]
                k1=derivative(r,y)
                k2=derivative(r+step/2,[y[i]+step*k1[i]/2 for i in range(2)])
                k3=derivative(r+step/2,[y[i]+step*k2[i]/2 for i in range(2)])
                k4=derivative(r+step,[y[i]+step*k3[i] for i in range(2)])
                states.append(tuple(y[i]+step*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6 for i in range(2)))
            return states
        base,basis=integrate((D(0),-pi/pressure)),integrate((D(1),D(0)))
        v0=(-po/pressure-base[-1][1])/basis[-1][1]
        states=[(v+v0*w,s+v0*t) for (v,s),(w,t) in zip(base,basis)]
        out={'inner_displacement':states[0][0]*a*pressure/e}
        for label,index,r in [('inner',0,D(1)),('mid',n//2,(1+b/a)/2),('outer',n,b/a)]:
            v,s=states[index]
            out[label+'_radial_stress']=s*pressure
            out[label+'_hoop_stress']=(v/r+nu*s)*pressure
        return {k:str(v) for k,v in out.items()}


def investigate(item):
    p = {k:F(v) for k,v in item['parameters'].items()}
    cached = {v['steps']:v['output'] for v in item['retained_outputs']}
    levels=[]
    selected=None
    s=scales(p,next(iter(cached.values())))
    for n in MANIFEST['levels']:
        step=fields(p,n)
        if n in cached:
            step['retained_replay_difference_normalized']=distance(step['output'],cached[n],s)
            # Original outputs are observations; the new fields must reproduce them.
            if step['retained_replay_difference_normalized'] > 1e-10:
                raise ValueError(f'Retained numerical output replay mismatch: {item["id"]}, {n}')
        levels.append(step)
        step['resolution_decision']=resolution_decision(levels,s)
        if step['resolution_decision']['accepted']:
            selected=step
            break
    # Reference is deliberately consulted only after resolution selection stops.
    truth=reference.cylinder(p)
    for step in levels:
        step['exact_error_normalized']={k:abs(v-float(truth[k]))/s[k] if s[k] else (0.0 if v == float(truth[k]) else math.inf) for k,v in step['output'].items()}
    budget=float(F(MANIFEST['budget_relative']))
    truth_pass=selected is not None and all(v <= budget for v in selected['exact_error_normalized'].values())
    result={'id':item['id'],'purpose':item['purpose'],'parameters':item['parameters'],
            'legacy_qualified':item['legacy_qualified'], 'levels':levels,
            'selected_steps':selected['steps'] if selected else None,
            'new_resolution_qualified':truth_pass,
            'status':'qualified_at_new_resolution' if truth_pass else 'not_qualified',
            'truth_exact':{k:str(v) for k,v in truth.items()}}
    if item['id'] in MANIFEST['decimal_diagnostic_ids']:
        output=decimal_output(p)
        with localcontext() as ctx:
            ctx.prec=50
            fraction=lambda f:D(f.numerator)/D(f.denominator)
            difference={k:float(abs(D(v)-D.from_float(cached[32][k]))/D.from_float(s[k])) for k,v in output.items()}
            exact_error={k:float(abs(D(v)-fraction(truth[k]))/D.from_float(s[k])) for k,v in output.items()}
        result['arithmetic_diagnostic']={'steps':32,'precision_decimal_digits':50,'output_decimal':output,
                                          'binary64_difference_normalized':difference,
                                          'decimal_exact_error_normalized':exact_error}
    return result
