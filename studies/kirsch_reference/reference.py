"""Two independently evaluated routes for the y-loaded Kirsch field.

The polar route follows the cited infinite-plane stress equations. The Airy
route differentiates a separately derived scalar potential using second-order
Cartesian jets; it does not transform or import the polar stress formula.
"""
from dataclasses import dataclass
from math import atan2, cos, log, sin, sqrt


@dataclass(frozen=True)
class Jet:
    v: float
    x: float = 0.0
    y: float = 0.0
    xx: float = 0.0
    xy: float = 0.0
    yy: float = 0.0

    @staticmethod
    def of(value):
        return value if isinstance(value, Jet) else Jet(float(value))

    def __add__(self, other):
        other = Jet.of(other)
        return Jet(*(a+b for a,b in zip(vars(self).values(), vars(other).values())))

    __radd__ = __add__

    def __neg__(self):
        return Jet(*(-a for a in vars(self).values()))

    def __sub__(self, other):
        return self + -Jet.of(other)

    def __rsub__(self, other):
        return Jet.of(other) - self

    def __mul__(self, other):
        b = Jet.of(other)
        a = self
        return Jet(a.v*b.v,
                   a.x*b.v+a.v*b.x, a.y*b.v+a.v*b.y,
                   a.xx*b.v+2*a.x*b.x+a.v*b.xx,
                   a.xy*b.v+a.x*b.y+a.y*b.x+a.v*b.xy,
                   a.yy*b.v+2*a.y*b.y+a.v*b.yy)

    __rmul__ = __mul__

    def reciprocal(self):
        a = self
        if a.v == 0:
            raise ZeroDivisionError("zero jet")
        v = 1/a.v
        return Jet(v, -a.x*v*v, -a.y*v*v,
                   2*a.x*a.x*v**3-a.xx*v*v,
                   2*a.x*a.y*v**3-a.xy*v*v,
                   2*a.y*a.y*v**3-a.yy*v*v)

    def __truediv__(self, other):
        return self * Jet.of(other).reciprocal()

    def __rtruediv__(self, other):
        return Jet.of(other) * self.reciprocal()

    def log(self):
        a = self
        if a.v <= 0:
            raise ValueError("log domain")
        return Jet(log(a.v), a.x/a.v, a.y/a.v,
                   a.xx/a.v-a.x*a.x/a.v**2,
                   a.xy/a.v-a.x*a.y/a.v**2,
                   a.yy/a.v-a.y*a.y/a.v**2)


def polar(x, y, a, sigma):
    """(radial, hoop, shear) with theta from +x and remote y stress."""
    r = sqrt(x*x+y*y)
    if a <= 0 or r*r < a*a*(1-1e-14):
        raise ValueError("point must lie outside a positive-radius hole")
    theta = atan2(y, x)
    q = a*a/(r*r)
    c, s = cos(2*theta), sin(2*theta)
    return (sigma/2*((1-q)-(1-4*q+3*q*q)*c),
            sigma/2*((1+q)+(1+3*q*q)*c),
            sigma/2*(1+2*q-3*q*q)*s)


def polar_cartesian(x, y, a, sigma):
    sr, st, tr = polar(x, y, a, sigma)
    r = sqrt(x*x+y*y)
    c, s = x/r, y/r
    return (sr*c*c+st*s*s-2*tr*s*c,
            sr*s*s+st*c*c+2*tr*s*c,
            (sr-st)*s*c+tr*(c*c-s*s))


def airy_cartesian(x, y, a, sigma):
    """Cartesian Airy derivatives: sigma_xx=Phi_yy, sigma_yy=Phi_xx."""
    if a <= 0 or x*x+y*y < a*a*(1-1e-14):
        raise ValueError("point must lie outside a positive-radius hole")
    X, Y = Jet(x, x=1), Jet(y, y=1)
    r2 = X*X+Y*Y
    c2 = (X*X-Y*Y)/r2
    # Phi=(sigma/4)[r^2 - 2a^2 ln(r/a)
    #                 +(r^2-2a^2+a^4/r^2) cos(2theta)].
    # Adding a constant to Phi is immaterial. This potential is biharmonic.
    phi = sigma/4*(r2-a*a*(r2/(a*a)).log()
                   +(r2-2*a*a+a**4/r2)*c2)
    return (phi.yy, phi.xx, -phi.xy)


def traction(stress, nx, ny):
    xx, yy, xy = stress
    return (xx*nx+xy*ny, xy*nx+yy*ny)


def max_abs(values):
    return max((abs(v) for v in values), default=0.0)
