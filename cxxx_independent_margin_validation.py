"""CXXX: independent calibration/validation for auxiliary-bound margins."""
import random
from statistics import mean

SCENARIOS = {
    "original": [0.0] * 216 + [0.25] * 18 + [1.0] * 6,
    "rarer_extremes": [0.0] * 234 + [0.25] * 4 + [1.0] * 2,
    "more_midrange": [0.0] * 180 + [0.25] * 48 + [1.0] * 12,
    "shifted_high": [0.0] * 168 + [0.25] * 48 + [1.0] * 24,
    "heldout_skewed": [0.0] * 150 + [0.1] * 60 + [0.6] * 25 + [1.0] * 15,
    "heldout_spiky": [0.0] * 230 + [0.6] * 5 + [1.0] * 15,
}
MARGINS = (0.0, 0.025, 0.05, 0.1, 0.2, 0.5, 1.0)


def evaluate(population, margin, repetitions=5000, seed=20261030,
             observed_count=120, auxiliary_count=12):
    if repetitions < 1 or observed_count < 0 or auxiliary_count < 1:
        raise ValueError("invalid sample or repetition count")
    if observed_count + auxiliary_count > len(population):
        raise ValueError("sample counts exceed population")
    if not population or any(x < 0 or x > 1 for x in population):
        raise ValueError("population must be nonempty and lie in [0, 1]")
    if margin < 0:
        raise ValueError("margin must be nonnegative")
    rng = random.Random(seed)
    G = len(population)
    target = mean(population)
    hits, widths = 0, []
    for _ in range(repetitions):
        draw = rng.sample(population, G)
        observed = draw[:observed_count]
        auxiliary = draw[observed_count:observed_count + auxiliary_count]
        lo = max(0.0, min(auxiliary) - margin)
        hi = min(1.0, max(auxiliary) + margin)
        missing, total = G - len(observed), sum(observed)
        left = (total + missing * lo) / G
        right = (total + missing * hi) / G
        hits += int(left <= target <= right)
        widths.append(right - left)
    rate = hits / repetitions
    # Approximate Monte Carlo standard error; descriptive, not a formal interval.
    mcse = (rate * (1.0 - rate) / repetitions) ** 0.5
    return {"population_mean": target, "containment_rate": rate,
            "monte_carlo_se": mcse, "mean_interval_width": mean(widths)}


def run_experiment(repetitions=5000, seed=20261030):
    # Choose the margin on the calibration population only; then freeze it.
    calibration = SCENARIOS["original"]
    calibration_scores = {
        str(d): evaluate(calibration, d, repetitions, seed + int(d * 10000))
        for d in MARGINS
    }
    selected = min(MARGINS, key=lambda d: (
        calibration_scores[str(d)]["mean_interval_width"]
        if calibration_scores[str(d)]["containment_rate"] >= 0.95 else float("inf")
    ))
    if calibration_scores[str(selected)]["containment_rate"] < 0.95:
        selected = 1.0
    # Validation populations use independent seed streams, and do not change selected margin.
    validation = {}
    for i, name in enumerate(("rarer_extremes", "more_midrange", "shifted_high",
                              "heldout_skewed", "heldout_spiky")):
        validation[name] = evaluate(SCENARIOS[name], selected, repetitions,
                                     seed + 100000 + i * 1000)
    return {
        "seed": seed, "repetitions": repetitions, "selected_margin": selected,
        "selection_rule": "smallest tested margin with calibration empirical containment >= 0.95; fallback 1.0",
        "calibration": calibration_scores, "validation": validation,
        "caveat": "Empirical selection and Monte Carlo SE do not provide a universal or formal coverage guarantee."
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_experiment(), indent=2, sort_keys=True))
