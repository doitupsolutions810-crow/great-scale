"""CXL: detect when count-only states lose unit-specific objective information."""
from itertools import product
from math import isclose


def audit_unit_specific_contributions(allowed, contributions, population, observed_sum=0.0):
    """Exhaustively compare count-only grouping with a sufficient richer signature.

    contributions[unit][stratum] = (lower_contribution, upper_contribution).
    Feasibility in this demonstrator is encoded by allowed choices; there are no
    additional global constraints. This is a finite audit/reference implementation.
    """
    if population <= 0:
        raise ValueError("population must be positive")
    if len(allowed) != len(contributions):
        raise ValueError("each unit needs a contribution map")
    for i, choices in enumerate(allowed):
        if not choices:
            raise ValueError("each unit needs at least one allowed stratum")
        if any(s not in contributions[i] for s in choices):
            raise ValueError("missing contribution for an allowed unit/stratum pair")
    rows = []
    for assignment in product(*allowed):
        counts = tuple(sum(s == h for s in assignment)
                       for h in sorted({x for choices in allowed for x in choices}))
        lower_sum = sum(contributions[i][s][0] for i, s in enumerate(assignment))
        upper_sum = sum(contributions[i][s][1] for i, s in enumerate(assignment))
        rows.append((assignment, counts, lower_sum, upper_sum))
    count_groups = {}
    refined_groups = {}
    for assignment, counts, lo, hi in rows:
        count_groups.setdefault(counts, []).append((lo, hi))
        refined_groups.setdefault((counts, lo, hi), []).append(assignment)
    count_only_is_sufficient = all(
        all(isclose(pair[0], group[0][0], abs_tol=1e-12) and
            isclose(pair[1], group[0][1], abs_tol=1e-12) for pair in group)
        for group in count_groups.values()
    )
    lower = (observed_sum + min(row[2] for row in rows)) / population
    upper = (observed_sum + max(row[3] for row in rows)) / population
    return {
        "assignment_count": len(rows),
        "count_state_count": len(count_groups),
        "refined_state_count": len(refined_groups),
        "count_only_sufficient": count_only_is_sufficient,
        "lower": lower,
        "upper": upper,
        "assignments": [
            {"assignment": list(a), "counts": list(c), "lower_sum": lo, "upper_sum": hi}
            for a, c, lo, hi in rows
        ],
    }
