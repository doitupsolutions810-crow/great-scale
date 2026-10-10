# Great Scale LXXXVI — Residual Risk Under Uncertainty

## Finding
Reliability is conditional on both a failure model and its dependency map. A precise probability computed from an incomplete map is not a complete risk assessment.

## Formal model
Let F be the finite set of modeled failure sources, S subset F a realized failed-source set, and D_i the declared dependencies of pathway i. Path i survives iff D_i intersect S is empty. With k required surviving paths, success is R(S) >= k.

If source failures are mutually independent with probabilities p_j, then P(S) = product(j in S, p_j) product(j not in S, 1-p_j), and P_model(success) = sum over S subset F of P(S) * 1[R(S) >= k].

Enumeration is exact for the declared finite model and costs O(2^m * path_count) in this straightforward implementation, where m is the number of sources. It is not automatically a real-world reliability guarantee.

## Uncertain probabilities
For fixed dependencies and independent source failures with p_j in [p_j-, p_j+], success is monotone non-increasing in each failure probability. Evaluating all upper endpoints gives a lower reliability bound; evaluating all lower endpoints gives an upper reliability bound.

## Incomplete dependency map
Let q be probability mass assigned to an unmodeled scenario, with 0 <= q <= eta. Let p_M be modeled reliability and unknown-scenario reliability p_U lie in [0,1]. Under p = (1-q)p_M + q*p_U, conservative bounds are [(1-eta)p_M, (1-eta)p_M + eta]. This is a sensitivity model, not a universal law: eta must be justified externally. If no defensible bound on omitted-model probability exists, the calculation cannot certify a nontrivial real-world lower bound.

## Limits
- Overlapping dependencies are represented through shared source labels and can induce correlated pathway failures.
- If source failures are dependent, the product formula is invalid; use a joint distribution or conservative dependence bounds.
- Missing dependency edges can bias results optimistically.
- Probability intervals depend on data, elicitation, and operating conditions.
- Exact enumeration scales exponentially; larger systems need structure-aware algorithms or reliability methods tailored to the graph.

## Integration
Module residual_risk.py implements state enumeration, interval reliability bounds, and an explicit incompleteness sensitivity interval. Tests are in tests/test_residual_risk.py. Tests must be executed in the target environment before validation is claimed.
