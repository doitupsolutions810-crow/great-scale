"""CXXVII: repeated-sampling diagnostic for auxiliary-derived bounds.

The experiment contrasts empirical auxiliary extrema, a fixed margin, and
known domain support. Monte Carlo coverage is diagnostic for this specific
synthetic population; it is not a universal coverage guarantee.
"""
import random
from statistics import mean


def finite_population_bounds(observed, population_size, lower, upper):
    if population_size <= 0 or len(observed) > population_size:
        raise ValueError("invalid population size")
    if lower > upper:
        raise ValueError("lower must not exceed upper")
    if any(x < lower or x > upper for x in observed):
        raise ValueError("observed value outside limits")
    missing = population_size - len(observed)
    total = sum(observed)
    return ((total + missing * lower) / population_size,
            (total + missing * upper) / population_size)


def run_coverage_experiment(repetitions=5000, seed=20261010,
                            observed_count=120, auxiliary_count=12,
                            margin=0.1):
    if repetitions <= 0 or observed_count < 0 or auxiliary_count < 1:
        raise ValueError("invalid repetition or sample counts")
    population = [0.0] * 216 + [0.25] * 18 + [1.0] * 6
    size = len(population)
    if observed_count + auxiliary_count > size:
        raise ValueError("sample counts exceed population")
    target = mean(population)
    rng = random.Random(seed)
    cover = {"sample_extrema": 0, "fixed_margin": 0, "known_support": 0}
    widths = {key: [] for key in cover}
    for _ in range(repetitions):
        draw = rng.sample(population, size)
        observed = draw[:observed_count]
        auxiliary = draw[observed_count:observed_count + auxiliary_count]
        lo, hi = min(auxiliary), max(auxiliary)
        limits = {
            "sample_extrema": (lo, hi),
            "fixed_margin": (max(0.0, lo - margin), min(1.0, hi + margin)),
            "known_support": (0.0, 1.0),
        }
        for key, (lower, upper) in limits.items():
            interval = finite_population_bounds(observed, size, lower, upper)
            cover[key] += int(interval[0] <= target <= interval[1])
            widths[key].append(interval[1] - interval[0])
    return {
        "seed": seed, "repetitions": repetitions, "population_size": size,
        "observed_count": observed_count, "auxiliary_count": auxiliary_count,
        "true_mean": target, "margin": margin,
        "coverage_rate": {key: cover[key] / repetitions for key in cover},
        "mean_interval_width": {key: mean(values) for key, values in widths.items()},
        "interpretation": (
            "Monte Carlo diagnostics for this synthetic population only. "
            "Known support [0,1] is guaranteed here by construction; observed "
            "extrema and fixed margins have no universal guarantee."
        ),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_coverage_experiment(), indent=2, sort_keys=True))
