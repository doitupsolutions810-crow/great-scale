"""CXXXVII: independent exhaustive oracle for constrained classification bounds.

This intentionally uses a different enumeration path than the production reference
solver. It is suitable for small test cases and for checking future solver backends.
"""
from itertools import product
from math import isclose


def exhaustive_oracle(observed_sum, population, units, strata):
    if population <= 0:
        raise ValueError("population must be positive")
    choices = []
    for allowed in units:
        opts = tuple(s for s in allowed if s in strata)
        if not opts:
            raise ValueError("unit has no valid allowed stratum")
        choices.append(opts)
    feasible = []
    for assignment in product(*choices):
        counts = {name: assignment.count(name) for name in strata}
        if any(counts[n] < rule["min_missing"] or
               (rule["max_missing"] is not None and counts[n] > rule["max_missing"])
               for n, rule in strata.items()):
            continue
        lower = (observed_sum + sum(counts[n] * strata[n]["lower"] for n in strata)) / population
        upper = (observed_sum + sum(counts[n] * strata[n]["upper"] for n in strata)) / population
        feasible.append((lower, upper, assignment))
    if not feasible:
        raise ValueError("no feasible assignment")
    return {
        "lower": min(row[0] for row in feasible),
        "upper": max(row[1] for row in feasible),
        "feasible_assignments": len(feasible),
    }


def assert_matches(candidate, oracle, tolerance=1e-12):
    """Raise AssertionError if endpoints or feasible counts disagree."""
    if candidate.feasible_assignments != oracle["feasible_assignments"]:
        raise AssertionError("feasible assignment count mismatch")
    if not isclose(candidate.lower, oracle["lower"], rel_tol=0, abs_tol=tolerance):
        raise AssertionError("lower endpoint mismatch")
    if not isclose(candidate.upper, oracle["upper"], rel_tol=0, abs_tol=tolerance):
        raise AssertionError("upper endpoint mismatch")
    return True
