"""Reviewer-authored independent check of the SDLV302 first flexural frequency.

Imports nothing from the repository. Physical inputs are typed from the official
Code_Aster v17 v2.04.302 problem page, not read from spec.json. The repository
results.json is read (JSON only) for comparison. Usage:

    python3 -I independent_check.py <repo>/reports/sdlv302-modal/results.json

Routes:
  D  Euler-Lagrange equations of U=1/2 int[EI phi'^2 + k'GA (w'-phi)^2],
     T=1/2 int[rhoA wdot^2 + rhoI phidot^2]; w=W sin kx, phi=P cos kx satisfies
     w=0 and EI phi'=0 at both ends; 2x2 determinant solved in 60-digit Decimal.
  S  Source's printed dimensionless "minus" root, evaluated naively.
  F  Ansatz-free Galerkin FE: cubic Lagrange w and phi, w=0 at both ends only,
     consistent mass with rotary inertia, generalized symmetric eigenproblem.
"""
import json
import sys
from decimal import Decimal as D, getcontext

import numpy as np

getcontext().prec = 60


def dpi():  # Python decimal-module documentation recipe
    getcontext().prec += 2
    lasts, t, s, n, na, d, da = 0, D(3), D(3), 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n + na, na + 8
        d, da = d + da, da + 32
        t = (t * n) / d
        s += t
    getcontext().prec -= 2
    return +s


PI = dpi()
# Official problem page, section 1.1-1.2 (h along Y, b along Z; bending in XY).
L, h, b = D(2), D("0.2"), D("0.1")
E, nu, rho, kp = D("2.1e11"), D("0.3"), D(7800), D(5) / D(6)
A = b * h
I_Z = b * h**3 / 12          # strong axis, bending in XY
I_Y = h * b**3 / 12          # weak axis, bending in XZ
G = E / (2 * (1 + nu))
I_PRINTED, G_PRINTED = D("1.66e-5"), D("8.076e10")


def omega2(n, I=I_Z, A=A, E=E, G=G, rho=rho, kp=kp, L=L):
    """Lower and upper omega^2 roots of det(K - w^2 M) = 0 for wavenumber n*pi/L."""
    k = n * PI / L
    S = kp * G * A
    a = rho * A * rho * I
    bb = S * rho * I * k**2 + rho * A * E * I * k**2 + rho * A * S
    c = S * E * I * k**4
    disc = (bb * bb - 4 * a * c).sqrt()
    return 2 * c / (bb + disc), (bb + disc) / (2 * a), (k, S, a, bb, c)


def hz(w2):
    return w2.sqrt() / (2 * PI)


def strong_form_residual(n, I=I_Z):
    """Plug the lower root and its eigenvector back into both Euler-Lagrange equations."""
    w2, _, (k, S, *_ ) = omega2(n, I)
    W, P = S * k, S * k * k - rho * A * w2      # from equation 1
    eq1 = (S * k * k - rho * A * w2) * W - S * k * P
    eq2 = -S * k * W + (E * I * k * k + S - rho * I * w2) * P
    scale = max(abs(S * k * W), abs(E * I * k * k * P), abs(S * P))
    return float(abs(eq1) / scale), float(abs(eq2) / scale), float(P / W)


def source_naive_hz(n):
    """Source formula exactly as printed (minus root, /2gj), float64."""
    f = lambda x: float(x)
    Lf, Af, If, Ef, Gf, rf, kf = map(f, (L, A, I_Z, E, G, rho, kp))
    j, g, lam = If / (Af * Lf**2), Ef * If / (kf * Af * Gf * Lf**2), n * float(PI)
    Om = ((g + j) * lam**2 + 1 - ((g - j)**2 * lam**4 + 2 * (g + j) * lam**2 + 1) ** 0.5) / (2 * g * j)
    return (Om * Ef * If / (rf * Af * Lf**4)) ** 0.5 / (2 * float(PI))


def fe_modes(ne, nmodes=8):
    """Cubic-Lagrange Timoshenko FE in float64; returns Hz, w-shapes and first-mode residual."""
    Lf, Af, If, Ef, Gf, rf, kf = (float(x) for x in (L, A, I_Z, E, G, rho, kp))
    xi = np.array([-1, -1 / 3, 1 / 3, 1.0])
    gp, gw = np.polynomial.legendre.leggauss(5)
    V = np.vander(xi, 4, increasing=True)
    coef = np.linalg.inv(V)                         # Lagrange basis coefficients
    N = np.array([[np.polyval(coef[::-1, i], s) for i in range(4)] for s in gp])
    dN = np.array([[np.polyval(np.polyder(coef[::-1, i]), s) for i in range(4)] for s in gp])
    nn = 3 * ne + 1
    K = np.zeros((2 * nn, 2 * nn)); M = np.zeros_like(K)
    he = Lf / ne; J = he / 2
    for e in range(ne):
        nodes = 3 * e + np.arange(4)
        wdof, pdof = 2 * nodes, 2 * nodes + 1
        for q in range(len(gp)):
            Nw, dw = N[q], dN[q] / J
            Bb = np.zeros(2 * nn); Bb[pdof] = dw                  # phi'
            Bs = np.zeros(2 * nn); Bs[wdof] = dw; Bs[pdof] -= Nw   # w' - phi
            Nm = np.zeros(2 * nn); Nm[wdof] = Nw
            Nr = np.zeros(2 * nn); Nr[pdof] = Nw
            K += gw[q] * J * (Ef * If * np.outer(Bb, Bb) + kf * Gf * Af * np.outer(Bs, Bs))
            M += gw[q] * J * (rf * Af * np.outer(Nm, Nm) + rf * If * np.outer(Nr, Nr))
    free = np.setdiff1d(np.arange(2 * nn), [0, 2 * (nn - 1)])      # w(0)=w(L)=0 only
    Kf, Mf = K[np.ix_(free, free)], M[np.ix_(free, free)]
    C = np.linalg.cholesky(Mf); Ci = np.linalg.inv(C)
    lam, Y = np.linalg.eigh(Ci @ Kf @ Ci.T)
    X = Ci.T @ Y
    v, l1 = X[:, 0], lam[0]
    res = np.linalg.norm(Kf @ v - l1 * Mf @ v) / (np.linalg.norm(Kf, 2) * np.linalg.norm(v))
    x = np.linspace(0, Lf, nn)
    full = np.zeros((2 * nn, nmodes)); full[free] = X[:, :nmodes]
    wfull = full[0::2]
    # identify wavenumber: largest projection onto sin(m pi x/L), m=1..6
    tags = []
    for i in range(nmodes):
        proj = [abs(np.dot(wfull[:, i], np.sin(m * np.pi * x / Lf))) for m in range(1, 7)]
        tags.append(int(np.argmax(proj)) + 1)
    return np.sqrt(lam[:nmodes]) / (2 * np.pi), tags, float(res)


def shown(v, rule):
    """Interval [lo, hi) of exact values that display as printed value v under a rule."""
    if rule == "nearest_tenth":
        q = D("0.05")
    else:  # four significant figures
        q = D(5) * D(10) ** (D(v).adjusted() - 4)
    return D(v) - q, D(v) + q


def main(results_path):
    out = {}
    # --- route D: exact-arithmetic modal roots -------------------------------------
    flex = []
    for n in range(1, 5):
        lo, hi, _ = omega2(n)
        r1, r2, ratio = strong_form_residual(n)
        flex.append({"n": n, "lower_Hz": hz(lo), "upper_branch_Hz": hz(hi),
                     "omega_rad_s": lo.sqrt(), "strong_form_residuals": [r1, r2],
                     "P_over_W_per_m": ratio})
    f1 = flex[0]["lower_Hz"]
    axial = [(2 * m - 1) * (E / rho).sqrt() / (4 * L) for m in (1, 2)]   # fixed-free bar
    eb1 = (PI / L) ** 2 * (E * I_Z / (rho * A)).sqrt() / (2 * PI)
    rayleigh1 = hz(omega2(1, kp=D(10) ** 30)[0])                           # shear-rigid, rotary kept
    out["route_D_exact"] = {
        "first_flexural_Hz": str(f1), "first_flexural_rad_s": str(flex[0]["omega_rad_s"]),
        "flexural": [{"n": r["n"], "lower_Hz": str(r["lower_Hz"]),
                      "upper_branch_Hz": str(r["upper_branch_Hz"]),
                      "strong_form_residuals": r["strong_form_residuals"]} for r in flex],
        "axial_fixed_free_Hz": [str(x) for x in axial],
        "euler_bernoulli_n1_Hz": str(eb1), "rayleigh_shear_rigid_n1_Hz": str(rayleigh1),
        "inputs": {"A_m2": str(A), "I_z_m4": str(I_Z), "I_y_m4": str(I_Y), "G_Pa": str(G)},
    }
    assert max(max(r["strong_form_residuals"]) for r in flex) < 1e-50
    assert f1 < rayleigh1 < eb1

    # --- route S: source formula as printed, float64 ---------------------------------
    naive = [source_naive_hz(n) for n in range(1, 5)]
    out["route_S_source_naive_float64"] = {
        "Hz": naive, "abs_diff_from_D_Hz": [abs(naive[i] - float(flex[i]["lower_Hz"])) for i in range(4)]}
    assert max(out["route_S_source_naive_float64"]["abs_diff_from_D_Hz"]) < 1e-8

    # --- route F: ansatz-free FE ------------------------------------------------------
    fe = {}
    for ne in (2, 4, 8, 16, 32, 64):
        f, tags, res = fe_modes(ne)
        fe[ne] = {"Hz_first8": f.tolist(), "w_wavenumber_tags": tags,
                  "first_mode_abs_err_Hz": abs(f[0] - float(f1)), "first_mode_matrix_residual": res}
    orders = [float(np.log2(fe[m]["first_mode_abs_err_Hz"] / fe[2 * m]["first_mode_abs_err_Hz"])) for m in (4, 8, 16)]
    out["route_F_fe_cubic"] = {"meshes": fe, "observed_order_first_mode_4_8_16_to_next": orders,
                               "note": "p=3 elements: expected eigenvalue order 2p=6; N=64 is at the float64 floor"}
    assert fe[32]["first_mode_abs_err_Hz"] < 1e-7 and fe[32]["w_wavenumber_tags"][:5] == [1, 2, 3, 4, 5]
    assert all(5.5 < o < 6.5 for o in orders) and fe[32]["first_mode_matrix_residual"] < 1e-11

    # --- matrix residual comparable to the repository's (float64 2x2) ---------------
    k = np.pi / float(L); S = float(kp * G * A)
    k11, k12, k22 = S * k * k, -S * k, float(E * I_Z) * k * k + S
    m11, m22 = float(rho * A), float(rho * I_Z)
    w2 = float(omega2(1)[0])
    Km, Mm = np.array([[k11, k12], [k12, k22]]), np.diag([m11, m22])
    vec = np.array([-k12, k11 - w2 * m11])
    out["first_mode_2x2_float64"] = {
        "det_residual_over_max_product": abs(np.linalg.det(Km - w2 * Mm)) / max(k11 * k22, k12 * k12),
        "pencil_residual": float(np.linalg.norm((Km - w2 * Mm) @ vec) / (np.linalg.norm(Km, 2) * np.linalg.norm(vec))),
        "det_cancellation_ratio_c_over_k11k22": (k11 * k22 - k12 * k12) / (k11 * k22)}

    # --- printed displays ------------------------------------------------------------
    order = sorted([(float(r["lower_Hz"]), f"flexion n={r['n']}") for r in flex] +
                   [(float(axial[0]), "extension m=1"), (float(axial[1]), "extension m=2")])
    printed = [("1", "flexion", "115.7", flex[0]["lower_Hz"]), ("2", "flexion", "442.2", flex[1]["lower_Hz"]),
               ("3", "extension", "648.6", axial[0]), ("4", "flexion", "931.6", flex[2]["lower_Hz"]),
               ("5", "flexion", "1534.0", flex[3]["lower_Hz"])]
    disp = []
    for mode, form, p, val in printed:
        row = {"source_mode": mode, "form": form, "printed": p, "derived_Hz": str(val)}
        for rule in ("nearest_tenth", "four_sig_fig"):
            lo, hi = shown(p, rule)
            row[rule] = {"interval": [str(lo), str(hi)], "inside": bool(lo <= val < hi)}
        disp.append(row)
    lo, hi = D("115.65"), D("115.75")
    out["display_comparison"] = {
        "first_mode_in_[115.65,115.75)": bool(lo <= f1 < hi),
        "margin_to_lower_Hz": str(f1 - lo), "margin_to_upper_Hz": str(hi - f1),
        "all_modes": disp, "derived_global_order_first5": [t for _, t in order[:5]],
        "source_table_order": [f"{m} {fm}" for m, fm, _, _ in printed]}
    assert out["display_comparison"]["first_mode_in_[115.65,115.75)"]

    # --- printed inertia diagnostic ----------------------------------------------------
    out["printed_inertia"] = {
        "printed_numeric": str(I_PRINTED), "b_h3_over_12": str(I_Z), "h_b3_over_12": str(I_Y),
        "ratio_bh3_over_printed": str(I_Z / I_PRINTED),
        "printed_equals_h_b3_over_12_truncated_3sf": int(I_Y * D(10) ** 7) * D("1e-7") == I_PRINTED,
        "h_b3_over_12_rounded_3sf": f"{float(I_Y):.2e}",
        "f1_timoshenko_with_printed_I_Hz": str(hz(omega2(1, I=I_PRINTED)[0])),
        "f1_timoshenko_with_weak_axis_I_Hz": str(hz(omega2(1, I=I_Y)[0])),
        "f1_euler_bernoulli_with_printed_I_Hz": str((PI / L) ** 2 * (E * I_PRINTED / (rho * A)).sqrt() / (2 * PI)),
        "printed_G_vs_exact_G": [str(G_PRINTED), str(G)],
        "f1_with_printed_G_Hz": str(hz(omega2(1, G=G_PRINTED)[0])),
    }

    # --- higher-mode diagnostic: what single shear factor would print 1534.0 to 0.1 Hz? -
    target = D("1533.95")
    lo_k, hi_k = D("0.5"), D(5)
    for _ in range(200):
        mid = (lo_k + hi_k) / 2
        (lo_k, hi_k) = (mid, hi_k) if hz(omega2(4, kp=mid)[0]) < target else (lo_k, mid)
    out["fourth_flexural_shear_factor_to_reach_1533.95"] = {
        "k_prime": str(hi_k), "f1_at_that_k_prime_Hz": str(hz(omega2(1, kp=hi_k)[0])),
        "f4_with_printed_G_Hz": str(hz(omega2(4, G=G_PRINTED)[0]))}

    # --- physical/model-form context (not tolerances) -----------------------------------
    cowper = 10 * (1 + nu) / (12 + 11 * nu)
    deck_3d = {"1": "115.658988327", "2": "441.494604203", "3": "648.518713026",
               "4": "928.856946531", "5": "1526.95217"}   # astest/sdlv302a.comm VALE_CALC, GPL deck, src head 56f6e2be
    derived = [flex[0]["lower_Hz"], flex[1]["lower_Hz"], axial[0], flex[2]["lower_Hz"], flex[3]["lower_Hz"]]
    out["model_form_context"] = {
        "display_half_width_relative": str(D("0.05") / f1),
        "cowper_k_prime": str(cowper), "f1_cowper_Hz": str(hz(omega2(1, kp=cowper)[0])),
        "f1_cowper_minus_5_6_Hz": str(hz(omega2(1, kp=cowper)[0]) - f1),
        "f4_cowper_Hz": str(hz(omega2(4, kp=cowper)[0])),
        "euler_bernoulli_minus_timoshenko_Hz": str(eb1 - f1),
        "deck_3d_hexa20_vale_calc_relative_to_1d": {m: str((D(v) - derived[i]) / derived[i]) for i, (m, v) in enumerate(deck_3d.items())},
        "deck_3d_mode1_in_display_interval": bool(lo <= D(deck_3d["1"]) < hi),
    }

    # --- scaling limits (registered by the repository, not executed there) -------------
    s = D(4)
    out["scaling"] = {
        "rho_x4_ratio_minus_half": float(hz(omega2(1, rho=rho * s)[0]) / f1 - 1 / s.sqrt()),
        "E_and_G_x4_ratio_minus_2": float(hz(omega2(1, E=E * s, G=G * s)[0]) / f1 - s.sqrt()),
        "geometry_x4_ratio_minus_quarter": float(hz(omega2(1, I=I_Z * s**4, A=A * s**2, L=L * s)[0]) / f1 - 1 / s),
    }
    assert all(abs(v) < 1e-40 for v in out["scaling"].values())

    # --- comparison with repository output (JSON only) ----------------------------------
    if results_path:
        r = json.load(open(results_path))
        out["repo_comparison_abs_Hz"] = {
            **{f"flexural_n{m['flexural_n']}": abs(m["independent_energy_matrix_Hz"] - float(flex[m["flexural_n"] - 1]["lower_Hz"]))
               for m in r["flexural_modes"]},
            "axial": abs(r["axial_control_Hz"] - float(axial[0])),
            "euler_bernoulli": abs(r["euler_bernoulli_first_mode_limit_Hz"] - float(eb1)),
            "printed_I_first_mode": abs(r["source_display_inertia_diagnostic"]["first_mode_from_printed_numeric_value_Hz"]
                                        - float(out["printed_inertia"]["f1_timoshenko_with_printed_I_Hz"])),
        }
        assert max(out["repo_comparison_abs_Hz"].values()) < 1e-9
    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
