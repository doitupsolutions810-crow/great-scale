"""CXXXI: compare auxiliary-extrema intervals with sharp support-based bounds."""
import random
from statistics import mean


def support_bounds(observed, population_size, lower=0.0, upper=1.0):
    if population_size <= 0 or len(observed) > population_size or lower > upper:
        raise ValueError("invalid population size, sample, or support")
    if any(x < lower or x > upper for x in observed):
        raise ValueError("observed value outside support")
    missing = population_size - len(observed)
    total = sum(observed)
    return ((total + missing * lower) / population_size,
            (total + missing * upper) / population_size)


def auxiliary_margin_bounds(observed, auxiliary, population_size, margin,
                            support_lower=0.0, support_upper=1.0):
    if not auxiliary or margin < 0:
        raise ValueError("auxiliary sample must be nonempty and margin nonnegative")
    lo = max(support_lower, min(auxiliary) - margin)
    hi = min(support_upper, max(auxiliary) + margin)
    missing = population_size - len(observed)
    total = sum(observed)
    return ((total + missing * lo) / population_size,
            (total + missing * hi) / population_size)


def evaluate(population, repetitions=5000, seed=20261031, observed_count=120,
             auxiliary_count=12, margin=0.05):
    G = len(population)
    if G == 0 or observed_count < 0 or auxiliary_count < 1 or observed_count + auxiliary_count > G:
        raise ValueError("invalid population/sample sizes")
    if any(x < 0 or x > 1 for x in population):
        raise ValueError("population must be in [0,1]")
    if repetitions < 1 or margin < 0:
        raise ValueError("repetitions must be positive and margin nonnegative")
    target = mean(population)
    rng = random.Random(seed)
    aux_hits = support_hits = 0
    aux_widths, support_widths = [], []
    for _ in range(repetitions):
        draw = rng.sample(population, G)
        observed = draw[:observed_count]
        auxiliary = draw[observed_count:observed_count + auxiliary_count]
        a = auxiliary_margin_bounds(observed, auxiliary, G, margin)
        s = support_bounds(observed, G)
        aux_hits += int(a[0] <= target <= a[1])
        support_hits += int(s[0] <= target <= s[1])
        aux_widths.append(a[1] - a[0])
        support_widths.append(s[1] - s[0])
    return {
        "target_mean": target,
        "auxiliary_margin": margin,
        "auxiliary_empirical_containment": aux_hits / repetitions,
        "support_bound_empirical_containment": support_hits / repetitions,
        "auxiliary_mean_width": mean(aux_widths),
        "support_mean_width": mean(support_widths),
        "repetitions": repetitions,
    }


def run_experiment(repetitions=5000, seed=20261031):
    populations = {
        "original": [0.0] * 216 + [0.25] * 18 + [1.0] * 6,
        "heldout_spiky": [0.0] * 230 + [0.6] * 5 + [1.0] * 5,
        "heldout_skewed": [0.0] * 150 + [0.1] * 60 + [0.6] * 25 + [1.0] * 15,
    }
    results = {}
    for i, (name, pop) in enumerate(populations.items()):
        results[name] = evaluate(pop, repetitions=repetitions, seed=seed + i)
    return {
        "seed": seed, "margin": 0.05, "scenarios": results,
        "theorem": "If every unobserved value is known to lie in [0,1], support_bounds is sharp: both endpoints are attainable by setting all missing outcomes to 0 or 1.",
        "caveat": "Auxiliary sample extrema are not population limits without additional assumptions."
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment(), indent=2, sort_keys=True))
