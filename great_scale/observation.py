"""Great Scale LXXX: bounded-error certificates for observed side detection.

Model: x is the unknown true target, y is its observation, and |y-x| <= eps.
A side is certified only if the entire admissible interval lies strictly on
one side of reference r. This deterministic bound is not a statistical confidence.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
import math

@dataclass(frozen=True)
class SideCertificate:
    observed: float
    reference: float
    error_bound: float
    observed_gap: float
    certified: bool
    certified_side: int  # +1 above, -1 below, 0 unresolved
    margin: float

def certify_side(observed: float, reference: float, error_bound: float) -> SideCertificate:
    """Certify sign(x-reference), assuming |observed-x| <= error_bound."""
    if error_bound < 0:
        raise ValueError("error_bound must be nonnegative")
    if not all(math.isfinite(v) for v in (observed, reference, error_bound)):
        raise ValueError("inputs must be finite")
    gap = observed - reference
    margin = abs(gap) - error_bound
    certified = abs(gap) > error_bound
    side = (1 if gap > 0 else -1) if certified else 0
    return SideCertificate(observed, reference, error_bound, abs(gap),
                           certified, side, max(0.0, margin))

def as_record(certificate: SideCertificate) -> dict:
    """Return a JSON-friendly record for Great Scale telemetry."""
    return asdict(certificate)
