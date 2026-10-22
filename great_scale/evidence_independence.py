"""Diagnostics for declared common causes in evidence streams.

These helpers quantify an exchangeable-correlation model and report overlap in
declared provenance. They cannot prove real-world causal independence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class IndependenceAudit:
    shared_sources: tuple[str, ...]
    status: str
    note: str


def audit_declared_sources(evidence_sources: Iterable[Iterable[str]]) -> IndependenceAudit:
    """Audit declared source overlap across at least two evidence streams.

    An empty overlap means only that no common source was declared; it is not
    proof of independence.
    """
    streams = [set(stream) for stream in evidence_sources]
    if len(streams) < 2:
        raise ValueError("at least two evidence streams are required")
    shared = set.intersection(*streams)
    if shared:
        return IndependenceAudit(tuple(sorted(shared)), "SHARED_CAUSE_CANDIDATE",
            "Declared overlap exists; investigate dependence before combining evidence.")
    return IndependenceAudit((), "NO_DECLARED_OVERLAP",
        "No shared source was declared; causal independence remains unproven.")


def _validate_correlation(n: int, rho: float) -> None:
    if n < 1:
        raise ValueError("n must be at least 1")
    lower = -1.0 if n == 1 else -1.0 / (n - 1)
    if not lower <= rho <= 1.0:
        raise ValueError("rho is outside the admissible correlation range")


def mean_error_variance(variance: float, n: int, rho: float) -> float:
    """Variance of a mean under equal variance and exchangeable correlation."""
    if variance < 0:
        raise ValueError("variance must be non-negative")
    _validate_correlation(n, rho)
    return variance * (1 + (n - 1) * rho) / n


def effective_sample_size(n: int, rho: float) -> float:
    """Effective sample size for the exchangeable-correlation approximation."""
    _validate_correlation(n, rho)
    denominator = 1 + (n - 1) * rho
    if denominator <= 0:
        raise ValueError("correlation model gives a non-positive variance factor")
    return n / denominator
