# Great Scale CXLVII — Quotient Correctness and Property Preservation

## Question

After compressing a finite state space into behavioral-equivalence classes, which claims about original states can still be answered from the quotient alone?

## Mathematical criterion

Let S be the modeled state set and K:S→Q assign each state to a quotient class. A Boolean state property P:S→{0,1} is well-defined on the quotient if and only if

    K(s) = K(t) implies P(s) = P(t), for all s,t in S.

Equivalently, there exists P-hat:Q→{0,1} such that P = P-hat composed with K exactly when P is constant on every quotient block.

Proof. If P factors through K, equal keys imply equal property values. Conversely, if the property is constant on every block, define P-hat(q) as the common value of any state in class q; block-constancy makes this independent of the representative. QED.

## Minimal counterexample

Suppose states named safe and unsafe share one quotient class because their declared observations and modeled transitions do not distinguish them. Let P(s) mean “state is unsafe.” Then K(safe)=K(unsafe), but P(safe) differs from P(unsafe). The quotient cannot answer the safety question for that class. It must not guess a class label; reject the property projection or refine the state representation to retain the relevant distinction.

If a property is derived only from a preserved observation and that observation is constant within each class, the property passes this audit.

## Scope and limitations

- The audit checks state properties on a supplied finite partition; it does not prove arbitrary temporal/path properties.
- A temporal property is preserved only when its truth is determined by traces and labels retained by the quotient and the equivalence relation is adequate for that property.
- Passing establishes invariance for the supplied states, partition, and property function—not correctness of the real-world model, completeness of observations, or physical truth.
- This check complements, rather than replaces, CXLVI partition/transition validation.

## Great Scale mapping

| Rung | Object | Testable question |
|---|---|---|
| CXLIII | Optimization-preserving compression | Are feasibility and objective values invariant under the chosen key? |
| CXLIV | Transition-preserving state | Do equivalent states enable matching actions and lead to equivalent successors? |
| CXLV | Multi-step behavioral equivalence | Do distinctions emerge over bounded horizons? |
| CXLVI | Minimal behavioral quotient | What is the coarsest stable partition for declared observations and transitions? |
| **CXLVII** | **Property preservation** | **Which state-level claims remain well-defined after quotienting?** |

The descent moves from preserving the machine's behavior to preserving the questions asked of that behavior.
