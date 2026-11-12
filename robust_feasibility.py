"""Exact bounded-uncertainty checks for the probability-moment constraint.

Isolated research helper. It does not redefine Great Scale's existing
Psi = CONE + S convention and is not wired into the live state engine.

Constraint: 0 <= p <= 1, v >= 0, and v <= p(1-p).
Inputs are interpreted by their decimal string representation; Fraction
arithmetic makes interval bounds exact for those input representations.
"""
from dataclasses import dataclass
from fractions import Fraction
import math
from typing import Literal

Status = Literal["certified_feasible", "certified_infeasible", "unresolved"]


@dataclass(frozen=True)
class FeasibilityCertificate:
    status: Status
    lower_margin: Fraction
    upper_margin: Fraction
    p_interval: tuple[Fraction, Fraction]
    v_interval: tuple[Fraction, Fraction]


def _fraction(value: int | float | str | Fraction, name: str) -> Fraction:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite numeric value, not bool")
    try:
        if not math.isfinite(float(value)):
            raise ValueError(f"{name} must be finite")
        return Fraction(str(value))
    except (TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite numeric value") from exc


def certify_probability_moment(
    p: int | float | str | Fraction,
    v: int | float | str | Fraction,
    epsilon_p: int | float | str | Fraction = 0,
    epsilon_v: int | float | str | Fraction = 0,
) -> FeasibilityCertificate:
    """Classify bounded uncertainty for v <= p(1-p).

    The uncertainty box is intersected with the declared domain p in [0, 1],
    v >= 0. certified_feasible means every admissible point in that box
    satisfies the constraint. certified_infeasible means none does.
    Otherwise the result is unresolved.

    This is an exact box certificate for this specific scalar constraint, not
    a general-purpose proof engine or a statistical confidence interval.
    """
    p0 = _fraction(p, "p")
    v0 = _fraction(v, "v")
    ep = _fraction(epsilon_p, "epsilon_p")
    ev = _fraction(epsilon_v, "epsilon_v")

    if not 0 <= p0 <= 1:
        raise ValueError("p must lie in [0, 1]")
    if v0 < 0:
        raise ValueError("v must be nonnegative")
    if ep < 0 or ev < 0:
        raise ValueError("uncertainty bounds must be nonnegative")

    zero, one = Fraction(0), Fraction(1)
    p_lo = max(zero, p0 - ep)
    p_hi = min(one, p0 + ep)
    v_lo = max(zero, v0 - ev)
    v_hi = v0 + ev

    def heat(q: Fraction) -> Fraction:
        return q * (one - q)

    lower_margin = min(heat(p_lo), heat(p_hi)) - v_hi

    if p_lo <= Fraction(1, 2) <= p_hi:
        max_heat = Fraction(1, 4)
    else:
        max_heat = max(heat(p_lo), heat(p_hi))
    upper_margin = max_heat - v_lo

    if lower_margin >= 0:
        status: Status = "certified_feasible"
    elif upper_margin < 0:
        status = "certified_infeasible"
    else:
        status = "unresolved"

    return FeasibilityCertificate(
        status=status,
        lower_margin=lower_margin,
        upper_margin=upper_margin,
        p_interval=(p_lo, p_hi),
        v_interval=(v_lo, v_hi),
    )
