"""Two independently constructed routes to the simply supported beam modes.

The first evaluates the dimensionless expression printed by Code_Aster. The
second builds a modal stiffness and mass matrix from Timoshenko strain and
kinetic energies. Neither route imports a Code_Aster deck or solver result.
"""

import math


def source_formula_hz(n: int, L: float, A: float, I: float, E: float,
                      G: float, rho: float, shear_factor: float) -> float:
    j = I / (A * L * L)
    g = E * I / (shear_factor * A * G * L * L)
    lam = n * math.pi
    # Rationalization avoids cancellation in the source's smaller root.
    radicand = 1 + 2 * (g + j) * lam**2 + (g - j)**2 * lam**4
    omega_dimensionless = 2 * lam**4 / (1 + (g + j) * lam**2 + math.sqrt(radicand))
    return math.sqrt(omega_dimensionless * E * I / (rho * A * L**4)) / (2 * math.pi)


def energy_matrix_hz(n: int, L: float, A: float, I: float, E: float,
                     G: float, rho: float, shear_factor: float) -> tuple[float, float]:
    """Return lower modal frequency and dimensionless determinant residual.

    With w=W sin(kx), phi=P cos(kx), U=(L/4)[EI k² P² +
    k'GA(kW-P)²], and T=(L/4)omega²[rho A W²+rho I P²].
    The common L/2 factor cancels from K and M.
    """
    k = n * math.pi / L
    shear = shear_factor * G * A
    k11, k12, k22 = shear * k*k, -shear * k, E * I * k*k + shear
    m11, m22 = rho * A, rho * I
    a = m11 * m22
    b = k11 * m22 + k22 * m11
    c = k11 * k22 - k12*k12
    omega2 = 2*c / (b + math.sqrt(b*b - 4*a*c))
    residual = abs((k11 - omega2*m11)*(k22 - omega2*m22) - k12*k12)
    return math.sqrt(omega2) / (2*math.pi), residual / max(k11*k22, k12*k12)


def axial_control_hz(L: float, E: float, rho: float) -> float:
    return math.sqrt(E/rho) / (4*L)


def euler_bernoulli_limit_hz(L: float, A: float, I: float,
                             E: float, rho: float) -> float:
    return (math.pi/L)**2 * math.sqrt(E*I/(rho*A)) / (2*math.pi)
