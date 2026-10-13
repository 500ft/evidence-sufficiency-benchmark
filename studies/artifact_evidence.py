"""Claim decisions from declared artifact and reference value intervals.

Intervals describe what a reported value permits. They are not physical error
bars, and an unknown rounding convention must not be guessed by this module.
"""

from dataclasses import dataclass
from fractions import Fraction as F


@dataclass(frozen=True)
class Interval:
    low: F
    high: F
    low_closed: bool = True
    high_closed: bool = True

    def __post_init__(self):
        if self.low > self.high or (self.low == self.high and
                                       not (self.low_closed and self.high_closed)):
            raise ValueError("empty value interval")

    def contains(self, value):
        value = F(value)
        return ((value > self.low or value == self.low and self.low_closed) and
                (value < self.high or value == self.high and self.high_closed))

    def intersects(self, other):
        if self.high < other.low or other.high < self.low:
            return False
        if self.high == other.low:
            return self.high_closed and other.low_closed
        if other.high == self.low:
            return other.high_closed and self.low_closed
        return True


def exact(value):
    """Exact-arithmetic artifact or exact reference."""
    value = F(value)
    return Interval(value, value)


def bounded(value, error):
    """Numerical-solver output or numerical reference with a declared bound."""
    value, error = F(value), F(error)
    if error < 0:
        raise ValueError("error bound must be nonnegative")
    return Interval(value - error, value + error)


def displayed(value, unit, convention):
    """Values that print as `value` under a stated whole-unit convention.

    Half ties round away from zero in nearest mode. Truncation is toward zero.
    The open ends matter at ties and integer display boundaries.
    """
    value, unit = F(value), F(unit)
    if unit <= 0 or value % unit:
        raise ValueError("display unit must be positive and divide the display")
    if convention == "nearest_half_away_from_zero":
        return Interval(value - unit / 2, value + unit / 2,
                        value > 0, value < 0)
    if convention == "truncate_toward_zero":
        if value > 0:
            return Interval(value, value + unit, True, False)
        if value < 0:
            return Interval(value - unit, value, False, True)
        return Interval(-unit, unit, False, False)
    raise ValueError("rounding convention must be declared")


def claim_decision(artifact: Interval, reference: Interval, acceptance_error):
    """Accept/reject only when every permitted pair gives that decision."""
    acceptance_error = F(acceptance_error)
    if acceptance_error < 0:
        raise ValueError("claim acceptance error must be nonnegative")
    largest_error = max(abs(artifact.low - reference.high),
                        abs(artifact.high - reference.low))
    if largest_error <= acceptance_error:
        return "accept"
    acceptance_band = Interval(reference.low - acceptance_error,
                               reference.high + acceptance_error,
                               reference.low_closed, reference.high_closed)
    if not artifact.intersects(acceptance_band):
        return "reject"
    return "ambiguous"
