"""Execute the prospectively registered exact-restriction development audit."""
import hashlib
import json
import math
from pathlib import Path

from .reference import airy_cartesian, max_abs, polar, polar_cartesian, traction

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "studies/kirsch_reference/spec.json"
OUT = ROOT / "reports/kirsch-reference"


def first(f, h):
    return (-f(2*h)+8*f(h)-8*f(-h)+f(-2*h))/(12*h)


def second(f, h):
    return (-f(2*h)+16*f(h)-30*f(0)+16*f(-h)-f(-2*h))/(12*h*h)


def simpson(f, lo, hi, panels):
    h = (hi-lo)/panels
    values = [f(lo+i*h) for i in range(panels+1)]
    return h/3*(values[0]+values[-1]+4*math.fsum(values[1:-1:2])+2*math.fsum(values[2:-1:2]))


def body_balance(a, B, sigma, panels):
    """Integrate every oriented boundary traction per unit plate thickness."""
    boundaries = [
        (a, B, lambda t: (t, 0.0, 0.0, -1.0, 1.0)),
        (a, B, lambda t: (0.0, t, -1.0, 0.0, 1.0)),
        (0, B, lambda t: (B, t, 1.0, 0.0, 1.0)),
        (0, B, lambda t: (t, B, 0.0, 1.0, 1.0)),
        (0, math.pi/2, lambda t: (a*math.cos(t), a*math.sin(t),
                                 -math.cos(t), -math.sin(t), a)),
    ]
    totals = [0.0, 0.0, 0.0]
    for lo, hi, point in boundaries:
        def component(k):
            def at(t):
                x, y, nx, ny, ds = point(t)
                tx, ty = traction(airy_cartesian(x, y, a, sigma), nx, ny)
                return (tx*ds, ty*ds, (x*ty-y*tx)*ds)[k]
            return simpson(at, lo, hi, panels)
        totals = [v+component(i) for i,v in enumerate(totals)]
    return totals


def case_result(case, spec):
    a, B, sigma = (float(case[k]) for k in ("a_m", "B_m", "remote_sigma_MPa"))
    assert 0 < a < B and float(case["E_MPa"]) > 0 and -1 < float(case["nu"]) < 0.5
    scale = max(1, abs(sigma))
    samples = []
    for ratio in spec["samples"]["radius_over_a"]:
        for degrees in spec["samples"]["theta_degrees"]:
            theta = math.radians(degrees)
            x, y = a*ratio*math.cos(theta), a*ratio*math.sin(theta)
            p = polar_cartesian(x, y, a, sigma)
            airy = airy_cartesian(x, y, a, sigma)
            samples.append({"r_over_a": ratio, "theta_deg": degrees,
                            "max_route_difference_MPa": max_abs(u-v for u,v in zip(p,airy))})
    max_route = max(row["max_route_difference_MPa"] for row in samples)
    hole = max(max_abs(polar(a*math.cos(t), a*math.sin(t), a, sigma)[j] for j in (0,2))
               for t in [i*math.pi/16 for i in range(9)])
    symmetry = max(abs(airy_cartesian(0, a+(B-a)*i/8, a, sigma)[2]) for i in range(9))
    symmetry = max(symmetry, *(abs(airy_cartesian(a+(B-a)*i/8, 0, a, sigma)[2]) for i in range(9)))
    outer = 0.0
    shear = 0.0
    for i in range(9):
        t = B*i/8
        for x,y,nx,ny in ((B,t,1,0),(t,B,0,1)):
            expected = traction(polar_cartesian(x,y,a,sigma),nx,ny)
            actual = traction(airy_cartesian(x,y,a,sigma),nx,ny)
            outer = max(outer, max_abs(u-v for u,v in zip(expected,actual)))
            shear = max(shear,abs(actual[1] if nx else actual[0]))
    h = a*1e-4
    divergence = 0.0
    compatibility = 0.0
    for ratio in spec["samples"]["interior_equilibrium_radius_over_a"]:
        for degrees in (30,45,60):
            x,y = a*ratio*math.cos(math.radians(degrees)), a*ratio*math.sin(math.radians(degrees))
            stress = lambda X,Y: airy_cartesian(X,Y,a,sigma)
            dx = first(lambda d:stress(x+d,y)[0],h)+first(lambda d:stress(x,y+d)[2],h)
            dy = first(lambda d:stress(x+d,y)[2],h)+first(lambda d:stress(x,y+d)[1],h)
            divergence = max(divergence,abs(dx),abs(dy))
            trace = lambda X,Y: sum(stress(X,Y)[:2])
            lap = second(lambda d:trace(x+d,y),h)+second(lambda d:trace(x,y+d),h)
            compatibility = max(compatibility,abs(lap))
    balances = {str(n): body_balance(a,B,sigma,n) for n in spec["samples"]["boundary_quadrature_panels"]}
    force = max(abs(v) for row in balances.values() for v in row[:2])
    moment = max(abs(row[2]) for row in balances.values())
    claim = polar(a,0,a,sigma)[1]
    independent_claim = airy_cartesian(a,0,a,sigma)[1]
    far = airy_cartesian(100*a,0,a,sigma)
    checks = {
        "stress_routes": max_route <= 1e-9*scale,
        "hole_and_symmetry": max(hole,symmetry) <= 1e-9*scale,
        "outer_boundary": outer <= 1e-9*scale,
        "equilibrium": divergence <= 1e-6*scale/a,
        "compatibility": compatibility <= 1e-4*scale/a**2,
        "free_body_force": force <= 1e-7*scale*B,
        "free_body_moment": moment <= 1e-7*scale*B*B,
        "claim": abs(claim-3*sigma) <= 1e-9*scale and abs(independent_claim-claim) <= 1e-9*scale,
        "far_field_limit": max_abs((far[0],far[1]-sigma,far[2])) <= 1e-3*scale,
    }
    return {"id":case["id"], "claim_sigma_theta_MPa":claim,
            "independent_claim_sigma_yy_MPa":independent_claim,
            "max_route_difference_MPa":max_route,
            "max_hole_traction_MPa":hole,"max_symmetry_shear_MPa":symmetry,
            "max_outer_traction_difference_MPa":outer,
            "max_outer_shear_MPa":shear,
            "max_divergence_MPa_per_m":divergence,
            "max_compatibility_trace_laplacian_MPa_per_m2":compatibility,
            "free_body_by_panels_force_MPa_m_and_moment_MPa_m2":balances,
            "far_field_at_100a_MPa":far,
            "checks":checks}


def build():
    spec = json.loads(SPEC.read_text())
    rows = [case_result(c,spec) for c in spec["cases"]]
    assert all(all(c["checks"].values()) for c in rows)
    return {"status":"executed derived development reference awaiting scoped Claude technical review; no admission or labels",
            "spec_sha256":hashlib.sha256(SPEC.read_bytes()).hexdigest(),
            "cases":rows}


def main():
    result = build()
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"results.json").write_text(json.dumps(result,indent=2)+"\n")


if __name__ == "__main__":
    main()
