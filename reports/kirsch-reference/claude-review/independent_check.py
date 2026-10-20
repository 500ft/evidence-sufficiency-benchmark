"""Reviewer-authored Kirsch checks. Stdlib only; imports no repository code.
Routes: (K) Kolosov-Muskhelishvili potentials, (P) reviewer polar formulas evaluated
exactly in Fractions, (A) hand gradient of the Airy potential for closed-form resultants.
Usage: python3 -I kirsch_independent_check.py <results.json> <pilot-failures.json>"""
import json, math, sys
from fractions import Fraction as F

def km(x, y, a, S):  # phi=S/4 z - S/2 a^2/z ; psi=S/2 z - S/2 a^2/z - S/2 a^4/z^3
    z = complex(x, y)
    p1 = S/4 + S/2*a*a/z**2; p2 = -S*a*a/z**3; s1 = S/2 + S/2*a*a/z**2 + 1.5*S*a**4/z**4
    tr = 4*p1.real; d = 2*(z.conjugate()*p2 + s1)
    return ((tr-d.real)/2, (tr+d.real)/2, d.imag/2)

def km_disp(x, y, a, S, E, nu, kappa=None):
    G = E/(2*(1+nu)); k = (3-nu)/(1+nu) if kappa is None else kappa
    z = complex(x, y)
    phi = S/4*z - S/2*a*a/z; p1 = S/4 + S/2*a*a/z**2; psi = S/2*z - S/2*a*a/z - S/2*a**4/z**3
    u = (k*phi - z*p1.conjugate() - psi.conjugate())/(2*G)
    return u.real, u.imag

def polar_cart(x, y, a, S):  # rational Cartesian form; works on Fraction and T
    rho = x*x + y*y; q = a*a/rho
    c2 = (x*x - y*y)/rho; s2 = 2*x*y/rho; cc = x*x/rho; ss = y*y/rho; sc = x*y/rho
    srr = S/2*((1-q) - (1-4*q+3*q*q)*c2); stt = S/2*((1+q) + (1+3*q*q)*c2); srt = S/2*(1+2*q-3*q*q)*s2
    return (srr*cc + stt*ss - 2*srt*sc, srr*ss + stt*cc + 2*srt*sc, (srr-stt)*sc + srt*(cc-ss))

class T:  # truncated Taylor c0 + c1 t + c2 t^2 over Fractions
    def __init__(s, c0, c1=0, c2=0): s.c = (F(c0), F(c1), F(c2))
    @staticmethod
    def of(v): return v if isinstance(v, T) else T(v)
    def __add__(s, o): o = T.of(o); return T(*(p+q for p, q in zip(s.c, o.c)))
    __radd__ = __add__
    def __neg__(s): return T(*(-p for p in s.c))
    def __sub__(s, o): return s + -T.of(o)
    def __rsub__(s, o): return T.of(o) - s
    def __mul__(s, o):
        o = T.of(o); a, b = s.c, o.c
        return T(a[0]*b[0], a[0]*b[1]+a[1]*b[0], a[0]*b[2]+a[1]*b[1]+a[2]*b[0])
    __rmul__ = __mul__
    def __truediv__(s, o):
        b = T.of(o).c; r0 = 1/b[0]
        return s * T(r0, -b[1]*r0*r0, (b[1]*b[1]*r0 - b[2])*r0*r0)
    def __rtruediv__(s, o): return T.of(o) / s

def exact_field_residuals(x, y, a, S):
    sx = polar_cart(T(x, 1), T(y), a, S); sy = polar_cart(T(x), T(y, 1), a, S)
    return (sx[0].c[1] + sy[2].c[1], sx[2].c[1] + sy[1].c[1],
            2*(sx[0].c[2] + sx[1].c[2]) + 2*(sy[0].c[2] + sy[1].c[2]))

def airy(x, y, a, S):  # Phi=S/4[2x^2 - a^2 ln(rho/a^2) - 2a^2 D/rho + a^4 D/rho^2], hand gradient
    rho = x*x + y*y; D = x*x - y*y
    P = S/4*(2*x*x - a*a*math.log(rho/(a*a)) - 2*a*a*D/rho + a**4*D/rho**2)
    Px = S/4*(4*x - 2*a*a*x/rho - 8*a*a*x*y*y/rho**2 + 2*a**4*x*(3*y*y - x*x)/rho**3)
    Py = S/4*(-2*a*a*y/rho + 8*a*a*x*x*y/rho**2 - 2*a**4*y*(3*x*x - y*y)/rho**3)
    return P, Px, Py

def segments(a, B):  # CCW: start, end, point(t), outward normal(t), ds/dt, t-range
    return {"bottom": ((a, 0), (B, 0), lambda t: (t, 0.0), lambda t: (0.0, -1.0), 1.0, (a, B)),
            "right": ((B, 0), (B, B), lambda t: (B, t), lambda t: (1.0, 0.0), 1.0, (0, B)),
            "top": ((B, B), (0, B), lambda t: (t, B), lambda t: (0.0, 1.0), 1.0, (0, B)),
            "left": ((0, B), (0, a), lambda t: (0.0, t), lambda t: (-1.0, 0.0), 1.0, (a, B)),
            "hole": ((0, a), (a, 0), lambda t: (a*math.cos(t), a*math.sin(t)),
                     lambda t: (-math.cos(t), -math.sin(t)), a, (0, math.pi/2))}

def closed_form_resultant(a, B, S, seg):
    (x0, y0), (x1, y1) = seg[0], seg[1]
    P0, Px0, Py0 = airy(x0, y0, a, S); P1, Px1, Py1 = airy(x1, y1, a, S)
    return (Py1-Py0, -(Px1-Px0), (P1-x1*Px1-y1*Py1) - (P0-x0*Px0-y0*Py0))

def gauss_legendre(n):
    out = []
    for i in range(1, n+1):
        x = math.cos(math.pi*(i-0.25)/(n+0.5))
        for _ in range(100):
            p0, p1 = 1.0, x
            for k in range(2, n+1): p0, p1 = p1, ((2*k-1)*x*p1 - (k-1)*p0)/k
            dp = n*(x*p1 - p0)/(x*x - 1); dx = p1/dp; x -= dx
            if abs(dx) < 1e-16: break
        out.append((x, 2/((1-x*x)*dp*dp)))
    return out

def quad_resultant(a, B, S, seg, rule):
    pt, nrm, ds, (lo, hi) = seg[2], seg[3], seg[4], seg[5]
    def f(t):
        x, y = pt(t); nx, ny = nrm(t); sxx, syy, sxy = km(x, y, a, S)
        tx, ty = sxx*nx + sxy*ny, sxy*nx + syy*ny
        return (tx*ds, ty*ds, (x*ty - y*tx)*ds)
    return rule(f, lo, hi)

def gl_rule(nodes, sub=8):
    def rule(f, lo, hi):
        tot = [0.0]*3; h = (hi-lo)/sub
        for j in range(sub):
            m, w = lo + (j+0.5)*h, h/2
            for x, wt in nodes: tot = [s + wt*w*c for s, c in zip(tot, f(m + w*x))]
        return tot
    return rule

def simpson_rule(n):
    def rule(f, lo, hi):
        h = (hi-lo)/n; v = [f(lo+i*h) for i in range(n+1)]
        return [h/3*(v[0][k] + v[-1][k] + 4*math.fsum(w[k] for w in v[1:-1:2]) + 2*math.fsum(w[k] for w in v[2:-1:2])) for k in range(3)]
    return rule

CASES = [("nominal", 1, 5, 10), ("scaled_geometry", 2, 20, 10), ("reversed_load", 1, 5, -7), ("zero_load", 1, 5, 0)]
E, NU = 200000.0, 0.3
PYTH = [(3, 5, 4), (4, 5, 3), (5, 13, 12), (12, 13, 5), (8, 17, 15), (20, 29, 21), (1, 1, 0), (0, 1, 1)]

def run(results_path, pilot_path):
    repo = {c["id"]: c for c in json.load(open(results_path))["cases"]}
    pilot = {c["id"]: c for c in json.load(open(pilot_path))["cases"]}
    nodes = gauss_legendre(20); out = {}
    for cid, a, B, S in CASES:
        r = {}; aF, SF = F(a), F(S); scale = max(1, abs(S))
        r["exact_claim_equals_(0,3S,0)"] = polar_cart(aF, F(0), aF, SF) == (0, 3*SF, 0)
        r["exact_claim_syy"] = str(polar_cart(aF, F(0), aF, SF)[1])
        hole = []
        for p, h, q in PYTH:
            x, y = aF*p/h, aF*q/h; sxx, syy, sxy = polar_cart(x, y, aF, SF)
            hole.append((sxx*x + sxy*y, sxy*x + syy*y))
        r["exact_hole_traction_all_zero_8pts"] = all(t == (0, 0) for t in hole)
        sym = [polar_cart(F(0), aF + F(k, 3), aF, SF)[2] for k in range(1, 7)] + [polar_cart(aF + F(k, 3), F(0), aF, SF)[2] for k in range(1, 7)]
        r["exact_symmetry_shear_all_zero_12pts"] = all(v == 0 for v in sym)
        r["max_abs_ux_on_x0_m"] = max(abs(km_disp(0.0, a + (B-a)*k/16, a, S, E, NU)[0]) for k in range(17))
        r["max_abs_uy_on_y0_m"] = max(abs(km_disp(a + (B-a)*k/16, 0.0, a, S, E, NU)[1]) for k in range(17))
        r["ux_at_(a,0)_m"] = km_disp(a, 0.0, a, S, E, NU)[0]
        pts = [(aF*F(24, 25), aF*F(18, 25)), (aF*F(10, 13), aF*F(24, 13)), (aF*F(3, 2), aF*F(7, 4)), (aF*3, aF*F(1, 2))]
        r["exact_divergence_and_trace_laplacian_all_zero_4pts"] = all(v == 0 for p in pts for v in exact_field_residuals(*p, aF, SF))
        dmax = 0.0; n = 40
        for i in range(n+1):
            for j in range(n+1):
                x, y = B*i/n, B*j/n
                if x*x + y*y < a*a: continue
                dmax = max(dmax, max(abs(u-v) for u, v in zip(km(x, y, a, S), polar_cart(x, y, a, S))))
        r["max_K_vs_P_binary64_grid_MPa"] = dmax
        hh = {}
        for d in (0, 30, 45, 60, 90):
            t = math.radians(d); v = km(a*math.cos(t), a*math.sin(t), a, S)
            hh[d] = v[0]*math.sin(t)**2 + v[1]*math.cos(t)**2 - 2*v[2]*math.sin(t)*math.cos(t)
        r["hole_hoop_K_MPa"] = hh
        r["outer_shear_9pt_max_MPa"] = max(max(abs(km(B, B*i/8, a, S)[2]), abs(km(B*i/8, B, a, S)[2])) for i in range(9))
        r["repo_max_outer_shear_MPa"] = repo[cid]["max_outer_shear_MPa"]
        r["right_edge_shear_dense_max_MPa"] = max(abs(km(B, B*i/400, a, S)[2]) for i in range(401))
        r["top_edge_syy_range_MPa"] = [min(km(B*i/400, B, a, S)[1] for i in range(401)), max(km(B*i/400, B, a, S)[1] for i in range(401))]
        r["right_edge_sxx_range_MPa"] = [min(km(B, B*i/400, a, S)[0] for i in range(401)), max(km(B, B*i/400, a, S)[0] for i in range(401))]
        def hooke(kappa):
            worst = 0.0
            for x, y in ((1.5*a, 0.7*a), (0.4*a, 2.2*a), (3.0*a, 3.0*a)):
                h = 1e-5*a; u = lambda X, Y: km_disp(X, Y, a, S, E, NU, kappa)
                exx = (u(x+h, y)[0]-u(x-h, y)[0])/(2*h); eyy = (u(x, y+h)[1]-u(x, y-h)[1])/(2*h)
                gxy = (u(x, y+h)[0]-u(x, y-h)[0])/(2*h) + (u(x+h, y)[1]-u(x-h, y)[1])/(2*h)
                sxx, syy, sxy = km(x, y, a, S)
                worst = max(worst, abs(exx-(sxx-NU*syy)/E), abs(eyy-(syy-NU*sxx)/E), abs(gxy-2*(1+NU)*sxy/E))
            return worst
        r["hooke_plane_stress_residual"] = hooke(None); r["hooke_residual_plane_strain_kappa_mutant"] = hooke(3-4*NU)
        r["strain_scale_S_over_E"] = abs(S)/E
        segs = segments(a, B); so = {}; tc = [0.0]*3; tg = [0.0]*3
        for name, seg in segs.items():
            cf = closed_form_resultant(a, B, S, seg); gl = quad_resultant(a, B, S, seg, gl_rule(nodes))
            so[name] = {"closed_form": cf, "gauss_legendre": gl, "max_abs_diff": max(abs(u-v) for u, v in zip(cf, gl))}
            tc = [s+c for s, c in zip(tc, cf)]; tg = [s+c for s, c in zip(tg, gl)]
        r["segments"] = so; r["free_body_closed_form_total"] = tc; r["free_body_gauss_legendre_total"] = tg
        simp = {}
        for n in (64, 128, 256, 512, 1024):
            tot = [0.0]*3
            for seg in segs.values(): tot = [s+c for s, c in zip(tot, quad_resultant(a, B, S, seg, simpson_rule(n)))]
            rep = repo[cid]["free_body_by_panels_force_MPa_m_and_moment_MPa_m2"][str(n)]
            simp[n] = {"reviewer": tot, "repo": rep, "max_abs_diff": max(abs(u-v) for u, v in zip(tot, rep)),
                       "force_pass": max(abs(tot[0]), abs(tot[1])) <= 1e-7*scale*B, "moment_pass": abs(tot[2]) <= 1e-7*scale*B*B,
                       "repo_gate": repo[cid]["free_body_gate_by_panels"][str(n)]}
            if n <= 256: simp[n]["pilot_equal_to_results"] = pilot[cid]["free_body_by_panels_force_MPa_m_and_moment_MPa_m2"][str(n)] == rep
        r["simpson"] = simp
        r["force_ratio_256_over_512"] = max(map(abs, simp[256]["reviewer"][:2]))/max(map(abs, simp[512]["reviewer"][:2])) if S else None
        r["original_all_levels_rule_would_pass_with_512_1024"] = all(simp[n]["force_pass"] and simp[n]["moment_pass"] for n in simp)
        r["budgets"] = {"force_MPa_m": 1e-7*scale*B, "moment_MPa_m2": 1e-7*scale*B*B}
        out[cid] = r
    z = polar_cart(F(1), F(0), F(1), F(0))
    out["mutants"] = {"unrotated_x_loaded_formula_claim_nominal_MPa": 10*(1-2),
                      "factor_2_error_detectable_at_zero_load": 2*z[1] != z[1],
                      "sign_flip_error_detectable_at_zero_load": -z[1] != z[1]}
    return out

if __name__ == "__main__":
    print(json.dumps(run(sys.argv[1], sys.argv[2]), indent=1, default=str))
