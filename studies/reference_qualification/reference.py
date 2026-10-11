"""Exact closed forms from continuum equilibrium and constitutive laws.

This route never imports the assembled solver or a selection policy.
Inputs and outputs use each explicit case unit system with rational arithmetic.
"""
from fractions import Fraction as F


def parameters(case):
    p = {key: F(value) for key, value in case["parameters"].items()}
    positive = [k for k in p if not k.endswith(("temperature_K", "temperature_F", "pressure_psi"))
                and k not in {"line_load_N_per_m", "poisson_ratio"}]
    if any(p[k] <= 0 for k in positive):
        raise ValueError("geometry and material coefficients must be positive")
    if any(v < 0 for k, v in p.items() if k.endswith("temperature_K")):
        raise ValueError("absolute temperatures must be nonnegative")
    if "poisson_ratio" in p and not -1 < p["poisson_ratio"] < F(1, 2):
        raise ValueError("isotropic Poisson ratio outside stable elastic range")
    if "inner_radius_in" in p and p["inner_radius_in"] >= p["outer_radius_in"]:
        raise ValueError("inner radius must be smaller than outer radius")
    if any(v < 0 for k,v in p.items() if k.endswith("pressure_psi")):
        raise ValueError("pressure magnitudes must be nonnegative")
    if any(v < F("-459.67") for k,v in p.items() if k.endswith("temperature_F")):
        raise ValueError("Fahrenheit temperature below absolute zero")
    return p


def beam(p):
    length, width, height = p["length_m"], p["width_m"], p["height_m"]
    inertia = width * height**3 / 12
    q, rigidity = p["line_load_N_per_m"], p["modulus_Pa"] * inertia
    return {"tip_deflection": q * length**4 / (8 * rigidity),
            "root_stress": abs(q) * length**2 * height / (4 * inertia),
            "support_force": -q * length,
            "support_moment": -q * length**2 / 2}


def slab(p):
    left, right = p["left_temperature_K"], p["right_temperature_K"]
    return {"midpoint_temperature": (left + right) / 2,
            "heat_flux": p["conductivity_W_per_m_K"] * (left - right) / p["length_m"]}


def cylinder(p):
    a, b = p["inner_radius_in"], p["outer_radius_in"]
    pi, po = p["internal_pressure_psi"], p["external_pressure_psi"]
    c = (pi*a*a-po*b*b)/(b*b-a*a)
    d = (pi-po)*a*a*b*b/(b*b-a*a)
    nu, modulus = p["poisson_ratio"], p["modulus_psi"]
    out = {"inner_displacement": ((1-nu)*c*a+(1+nu)*d/a)/modulus}
    for label, r in [("inner",a),("mid",(a+b)/2),("outer",b)]:
        out[f"{label}_radial_stress"] = c-d/r**2
        out[f"{label}_hoop_stress"] = c+d/r**2
    return out


def layered_wall(p):
    area = p["area_ft2"]
    resistance = (1/p["inner_h_Btu_per_hr_ft2_F"] + p["layer1_ft"]/p["k1_Btu_per_hr_ft_F"]
                  + p["layer2_ft"]/p["k2_Btu_per_hr_ft_F"] + 1/p["outer_h_Btu_per_hr_ft2_F"])/area
    q = (p["hot_temperature_F"]-p["ambient_temperature_F"])/resistance
    inner = p["hot_temperature_F"]-q/(area*p["inner_h_Btu_per_hr_ft2_F"])
    return {"heat_rate": q, "inner_surface_temperature": inner,
            "interface_temperature": inner-q*p["layer1_ft"]/(area*p["k1_Btu_per_hr_ft_F"]),
            "outer_surface_temperature": p["ambient_temperature_F"]+q/(area*p["outer_h_Btu_per_hr_ft2_F"])}


def solve(case):
    return {"beam_bending": beam, "steady_heat_conduction": slab,
            "thick_cylinder": cylinder, "layered_wall": layered_wall}[case.get("model",case["family"])](parameters(case))
