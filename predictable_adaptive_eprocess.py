"""Anytime-valid e-processes with predictable history-adaptive bets.

Under H0, E[X_t | F_(t-1)] <= q0 and X_t is binary. Each strategy receives
only the tuple of past observations and must return lambda in [0, 1/q0].
Strategy callbacks are trusted: Python cannot prove they avoid hidden state.
"""
from __future__ import annotations
import math
from collections.abc import Callable, Iterable, Sequence
BetStrategy = Callable[[tuple[int, ...]], float]

def predictable_adaptive_e_process(observations: Iterable[int], null_upper_bound: float, strategies: Sequence[BetStrategy], weights: Sequence[float]) -> list[float]:
    xs = list(observations)
    q0 = float(null_upper_bound)
    if not math.isfinite(q0) or not 0.0 < q0 < 1.0:
        raise ValueError("null_upper_bound must be finite and strictly between 0 and 1")
    if not strategies or len(strategies) != len(weights):
        raise ValueError("strategies and weights must have equal nonzero length")
    ws = [float(w) for w in weights]
    if any(not math.isfinite(w) or w < 0 for w in ws) or not math.isclose(sum(ws), 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("weights must be finite, nonnegative, and sum to 1")
    if any(isinstance(x, bool) or x not in (0, 1) for x in xs):
        raise ValueError("observations must contain only integer 0 or 1 values")
    wealth = [1.0] * len(strategies)
    result = [1.0]
    history: tuple[int, ...] = ()
    for x in xs:
        # Every strategy is called before the current outcome is applied.
        lambdas = [float(strategy(history)) for strategy in strategies]
        if any(not math.isfinite(lam) or not 0.0 <= lam <= 1.0 / q0 for lam in lambdas):
            raise ValueError("each predictable bet must be finite and in [0, 1/q0]")
        for i, lam in enumerate(lambdas):
            wealth[i] *= 1.0 + lam * (x - q0)
        result.append(sum(w * e for w, e in zip(ws, wealth)))
        history = history + (x,)
    return result
