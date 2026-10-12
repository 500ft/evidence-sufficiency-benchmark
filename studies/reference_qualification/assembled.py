"""Separate exact stiffness and local conservation routes; no closed-form import."""
from fractions import Fraction as F


def linear_solve(matrix, rhs):
    """Small rational Gaussian elimination, avoiding a floating-point error budget."""
    a = [list(row) + [value] for row, value in zip(matrix, rhs)]
    n = len(a)
    for col in range(n):
        pivot = next((i for i in range(col, n) if a[i][col]), None)
        if pivot is None:
            raise ValueError("singular constrained system")
        a[col], a[pivot] = a[pivot], a[col]
        scale = a[col][col]
        a[col] = [v / scale for v in a[col]]
        for row in range(n):
            if row == col:
                continue
            scale = a[row][col]
            a[row] = [v - scale * w for v, w in zip(a[row], a[col])]
    return [row[-1] for row in a]


def constrained(matrix, rhs, prescribed):
    free = [i for i in range(len(rhs)) if i not in prescribed]
    reduced = [[matrix[i][j] for j in free] for i in free]
    load = [rhs[i] - sum(matrix[i][j] * value for j, value in prescribed.items()) for i in free]
    solution = [F(0)] * len(rhs)
    for i, value in prescribed.items():
        solution[i] = value
    for i, value in zip(free, linear_solve(reduced, load)):
        solution[i] = value
    reactions = [sum(a * b for a, b in zip(row, solution)) - value for row, value in zip(matrix, rhs)]
    assert all(reactions[i] == 0 for i in free)
    return solution, reactions


def beam(p, nodes):
    n = len(nodes)
    k = [[F(0)] * (2*n) for _ in range(2*n)]
    f = [F(0)] * (2*n)
    # Section integral of y^2 dA, evaluated directly over the rectangular limits.
    half = p["height_m"] / 2
    inertia = p["width_m"] * (half**3 - (-half)**3) / 3
    rigidity = p["modulus_Pa"] * inertia
    for e, (a, b) in enumerate(zip(nodes, nodes[1:])):
        h = (b - a) * p["length_m"]
        # Cubic Hermite element: integral EI N''_i N''_j dx and integral q N_i dx.
        local = [[12, 6*h, -12, 6*h], [6*h, 4*h*h, -6*h, 2*h*h],
                 [-12, -6*h, 12, -6*h], [6*h, 2*h*h, -6*h, 4*h*h]]
        load = [h/2, h*h/12, h/2, -h*h/12]
        for i in range(4):
            f[2*e+i] += p["line_load_N_per_m"] * load[i]
            for j in range(4):
                k[2*e+i][2*e+j] += rigidity / h**3 * local[i][j]
    u, r = constrained(k, f, {0: F(0), 1: F(0)})
    output = {"tip_deflection": u[-2], "root_stress": abs(r[1]) * half / inertia,
              "support_force": r[0], "support_moment": r[1]}
    return output, {"nodal_deflections_m": [str(v) for v in u[::2]],
                    "nodal_slopes": [str(v) for v in u[1::2]],
                    "free_equilibrium_residual": "0"}


def slab(p, nodes):
    n = len(nodes)
    k = [[F(0)] * n for _ in range(n)]
    conductances = []
    for e, (a, b) in enumerate(zip(nodes, nodes[1:])):
        g = p["conductivity_W_per_m_K"] / ((b-a) * p["length_m"])
        conductances.append(g)
        k[e][e] += g
        k[e+1][e+1] += g
        k[e][e+1] -= g
        k[e+1][e] -= g
    t, _ = constrained(k, [F(0)] * n, {0: p["left_temperature_K"], n-1: p["right_temperature_K"]})
    fluxes = [g * (a-b) for g, a, b in zip(conductances, t, t[1:])]
    assert len(set(fluxes)) == 1
    output = {"midpoint_temperature": t[nodes.index(F(1, 2))], "heat_flux": fluxes[0]}
    return output, {"nodal_temperatures_K": [str(v) for v in t],
                    "segment_fluxes_W_per_m2": [str(v) for v in fluxes],
                    "internal_heat_balance_residual": "0"}


def layered_wall(p, nodes):
    # Independent local balances including convection edges and a material interface.
    # Each layer is partitioned separately; nodes are local fractions of each layer.
    area = p["area_ft2"]
    conductances = [p["inner_h_Btu_per_hr_ft2_F"]*area]
    for layer in (1, 2):
        for a,b in zip(nodes,nodes[1:]):
            conductances.append(p[f"k{layer}_Btu_per_hr_ft_F"]*area/(p[f"layer{layer}_ft"]*(b-a)))
    conductances.append(p["outer_h_Btu_per_hr_ft2_F"]*area)
    n = len(conductances)+1
    k = [[F(0)]*n for _ in range(n)]
    for i,g in enumerate(conductances):
        k[i][i] += g
        k[i+1][i+1] += g
        k[i][i+1] -= g
        k[i+1][i] -= g
    t,_ = constrained(k, [F(0)]*n, {0:p["hot_temperature_F"], n-1:p["ambient_temperature_F"]})
    flows = [g*(a-b) for g,a,b in zip(conductances,t,t[1:])]
    assert len(set(flows)) == 1
    return {"heat_rate": flows[0], "inner_surface_temperature": t[1],
            "interface_temperature": t[len(nodes)], "outer_surface_temperature": t[-2]}, {
            "nodal_temperatures_F": list(map(str,t)), "edge_heat_rates_Btu_per_hr": list(map(str,flows)),
            "internal_heat_balance_residual": "0"}


def solve(case, partition):
    p = {key: F(value) for key, value in case["parameters"].items()}
    nodes = [F(x) for x in partition]
    if nodes[0] != 0 or nodes[-1] != 1 or any(b <= a for a, b in zip(nodes, nodes[1:])):
        raise ValueError("partition must increase from zero to one")
    return {"beam_bending": beam, "steady_heat_conduction": slab,
            "layered_wall": layered_wall}[case.get("model",case["family"])](p, nodes)
