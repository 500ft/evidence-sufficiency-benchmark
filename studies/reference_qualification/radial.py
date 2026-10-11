"""Independent plane-stress radial BVP via RK4 shooting, without Lame coefficients."""
import math


def integrate(p, steps, u0, sr0):
    a, b = float(p["inner_radius_in"]), float(p["outer_radius_in"])
    modulus, nu = float(p["modulus_psi"]), float(p["poisson_ratio"])
    h = (b-a) / steps

    def derivative(r, state):
        u, sr = state
        # epsilon_theta=u/r; plane-stress compliance; radial equilibrium.
        return ((1-nu*nu)*sr/modulus - nu*u/r,
                modulus*u/r**2 - (1-nu)*sr/r)

    values = [(u0, sr0)]
    for j in range(steps):
        r, v = a+j*h, values[-1]
        k1 = derivative(r, v)
        k2 = derivative(r+h/2, [v[i]+h*k1[i]/2 for i in range(2)])
        k3 = derivative(r+h/2, [v[i]+h*k2[i]/2 for i in range(2)])
        k4 = derivative(r+h, [v[i]+h*k3[i] for i in range(2)])
        values.append(tuple(v[i]+h*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6 for i in range(2)))
    return values


def solve(p, steps):
    if steps < 2 or steps % 2:
        raise ValueError("even radial step count required for the midpoint claim")
    base = integrate(p, steps, 0.0, -float(p["internal_pressure_psi"]))
    basis = integrate(p, steps, 1.0, 0.0)
    u_inner = (-float(p["external_pressure_psi"])-base[-1][1]) / basis[-1][1]
    states = [(u+u_inner*v, sr+u_inner*t) for (u,sr),(v,t) in zip(base,basis)]
    a, b = float(p["inner_radius_in"]), float(p["outer_radius_in"])
    modulus, nu = float(p["modulus_psi"]), float(p["poisson_ratio"])
    output = {"inner_displacement": states[0][0]}
    for label, index, radius in [("inner",0,a),("mid",steps//2,(a+b)/2),("outer",steps,b)]:
        u, sr = states[index]
        output[f"{label}_radial_stress"] = sr
        output[f"{label}_hoop_stress"] = modulus*u/radius + nu*sr
    # Integral balance: [r*sigma_r]_a^b = integral sigma_theta dr.
    # Trapezoid recovery is intentionally separate from the RK4 update.
    hoop = [modulus*u/(a+j*(b-a)/steps)+nu*sr for j,(u,sr) in enumerate(states)]
    integral = (b-a)/steps * (math.fsum(hoop)-0.5*(hoop[0]+hoop[-1]))
    residual = b*states[-1][1]-a*states[0][1]-integral
    return output, {"steps": steps,
                    "inner_traction_error_psi": states[0][1]+float(p["internal_pressure_psi"]),
                    "outer_traction_error_psi": states[-1][1]+float(p["external_pressure_psi"]),
                    "integrated_equilibrium_residual_psi_in": residual,
                    "finite": all(math.isfinite(v) for v in output.values())}
