"""CXXVIII: empirical coverage-width frontier for auxiliary-bound margins."""
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


def run_margin_sweep(repetitions=5000, seed=20261010, observed_count=120,
                     auxiliary_count=12, margins=(0, 0.025, 0.05, 0.1, 0.2, 0.5, 1.0)):
    if repetitions <= 0 or observed_count < 0 or auxiliary_count < 1:
        raise ValueError("invalid repetition or sample counts")
    margins = tuple(float(d) for d in margins)
    if not margins or any(d < 0 for d in margins):
        raise ValueError("margins must be nonempty and nonnegative")
    population = [0.0] * 216 + [0.25] * 18 + [1.0] * 6
    size = len(population)
    if observed_count + auxiliary_count > size:
        raise ValueError("sample counts exceed population")
    target = mean(population)
    rng = random.Random(seed)
    cover = {d: 0 for d in margins}
    widths = {d: [] for d in margins}
    for _ in range(repetitions):
        draw = rng.sample(population, size)
        observed = draw[:observed_count]
        auxiliary = draw[observed_count:observed_count + auxiliary_count]
        lo, hi = min(auxiliary), max(auxiliary)
        for d in margins:
            lower, upper = max(0.0, lo - d), min(1.0, hi + d)
            left, right = finite_population_bounds(observed, size, lower, upper)
            cover[d] += int(left <= target <= right)
            widths[d].append(right - left)
    return {
        "seed": seed, "repetitions": repetitions, "population_size": size,
        "observed_count": observed_count, "auxiliary_count": auxiliary_count,
        "true_mean": target,
        "results": [{"margin": d, "empirical_containment_rate": cover[d] / repetitions,
                     "mean_interval_width": mean(widths[d])} for d in margins],
        "interpretation": (
            "Empirical results for this finite synthetic population only. "
            "No margin is a universal coverage guarantee absent justified assumptions."
        ),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_margin_sweep(), indent=2, sort_keys=True))
