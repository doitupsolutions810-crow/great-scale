"""CXXIX: test whether a margin's empirical behavior transfers across populations."""
import random
from statistics import mean

SCENARIOS = {
    "original": [0.0] * 216 + [0.25] * 18 + [1.0] * 6,
    "rarer_extremes": [0.0] * 234 + [0.25] * 4 + [1.0] * 2,
    "more_midrange": [0.0] * 180 + [0.25] * 48 + [1.0] * 12,
    "shifted_high": [0.0] * 168 + [0.25] * 48 + [1.0] * 24,
}


def evaluate(population, margins=(0, 0.025, 0.05, 0.1, 0.2, 0.5, 1.0),
             repetitions=5000, observed_count=120, auxiliary_count=12, seed=20261029):
    if repetitions < 1 or observed_count < 0 or auxiliary_count < 1:
        raise ValueError("invalid sample or repetition count")
    if observed_count + auxiliary_count > len(population):
        raise ValueError("sample counts exceed population")
    if any(x < 0 or x > 1 for x in population):
        raise ValueError("population values must be within [0, 1]")
    margins = tuple(float(d) for d in margins)
    if not margins or any(d < 0 for d in margins):
        raise ValueError("margins must be nonempty and nonnegative")
    G, target = len(population), mean(population)
    coverage = {d: 0 for d in margins}
    widths = {d: [] for d in margins}
    rng = random.Random(seed)
    for _ in range(repetitions):
        draw = rng.sample(population, G)
        observed = draw[:observed_count]
        auxiliary = draw[observed_count:observed_count + auxiliary_count]
        lo, hi = min(auxiliary), max(auxiliary)
        missing, total = G - len(observed), sum(observed)
        for d in margins:
            L, U = max(0.0, lo - d), min(1.0, hi + d)
            left, right = (total + missing * L) / G, (total + missing * U) / G
            coverage[d] += int(left <= target <= right)
            widths[d].append(right - left)
    return {
        "population_mean": target, "population_size": G,
        "results": [{"margin": d, "empirical_containment_rate": coverage[d] / repetitions,
                     "mean_interval_width": mean(widths[d])} for d in margins],
    }


def run_transfer_experiment(repetitions=5000, seed=20261029):
    out = {}
    for index, (name, population) in enumerate(SCENARIOS.items()):
        out[name] = evaluate(population, repetitions=repetitions, seed=seed + index)
    return {
        "seed": seed, "repetitions_per_scenario": repetitions,
        "observed_count": 120, "auxiliary_count": 12,
        "scenarios": out,
        "warning": "Scenario-specific empirical containment is not a universal guarantee or a confidence interval.",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_transfer_experiment(), indent=2, sort_keys=True))
