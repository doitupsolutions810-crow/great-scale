"""CXXXIX: audit whether count-state compression preserves an objective.

Count-only compression is valid when (1) future unit choices depend only on the
remaining units and current counts, and (2) feasibility and objective endpoints
are functions of the final stratum-count vector. This module supplies an explicit
finite-state audit for the current additive, stratum-homogeneous bound model.
"""
from dataclasses import dataclass
from itertools import product
from math import isclose


@dataclass(frozen=True)
class BoundRule:
    lower: float
    upper: float
    min_count: int = 0
    max_count: int | None = None


def enumerate_assignments(allowed, rules):
    names = tuple(rules)
    assignments = []
    for assignment in product(*allowed):
        if any(name not in rules for name in assignment):
            continue
        counts = {name: assignment.count(name) for name in names}
        if any(counts[n] < rules[n].min_count for n in names):
            continue
        if any(rules[n].max_count is not None and counts[n] > rules[n].max_count for n in names):
            continue
        assignments.append((assignment, tuple(counts[n] for n in names)))
    return names, assignments


def audit_count_sufficiency(observed_sum, population, allowed, rules):
    """Compare assignment-space and count-state extrema; return audit evidence."""
    if population <= 0:
        raise ValueError("population must be positive")
    if any(not choices for choices in allowed):
        raise ValueError("every unit must have at least one allowed stratum")
    if any(rule.lower > rule.upper for rule in rules.values()):
        raise ValueError("support lower bound exceeds upper bound")
    names, assignments = enumerate_assignments(allowed, rules)
    if not assignments:
        raise ValueError("no feasible assignment")
    def endpoint(counts, upper=False):
        return (observed_sum + sum(counts[i] * (rules[n].upper if upper else rules[n].lower)
                                   for i, n in enumerate(names))) / population
    unique_counts = sorted({counts for _, counts in assignments})
    exact_lower = min(endpoint(counts) for _, counts in assignments)
    exact_upper = max(endpoint(counts, True) for _, counts in assignments)
    compressed_lower = min(endpoint(counts) for counts in unique_counts)
    compressed_upper = max(endpoint(counts, True) for counts in unique_counts)
    return {
        "assignment_count": len(assignments),
        "distinct_count_states": len(unique_counts),
        "lower": compressed_lower,
        "upper": compressed_upper,
        "exact_lower": exact_lower,
        "exact_upper": exact_upper,
        "equivalent": isclose(exact_lower, compressed_lower, abs_tol=1e-12)
                      and isclose(exact_upper, compressed_upper, abs_tol=1e-12),
        "states": [list(counts) for counts in unique_counts],
        "strata_order": list(names),
    }
