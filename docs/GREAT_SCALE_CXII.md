# Great Scale CXII — Consistency Under Partial Observation

## Question
What can be concluded when some observers are unreachable or some checkpoint comparisons have not been performed?

## Formal model
Let (V={0,ldots,n-1}) be the supplied, signature-verified checkpoints and let (E_{obs}subseteq inom{V}{2}) be the observed comparisons. The complete pair set is (E_*=inom{V}{2}). Missing edges are (M=E_*setminus E_{obs}).

Classification is ordered by evidential strength:
1. **FORK** if any observed pair conflicts.
2. **PARTIAL_EVIDENCE** if no observed fork exists but (M
earnothing).
3. **INCOMPARABLE** if pair coverage is complete but at least one pair has no established ordering.
4. **CONSISTENT** only if pair coverage is complete and every pair is SAME or ORDERED.

A witnessed fork dominates missing edges because one conflict is enough to refute a global consistency claim. Missing edges, however, cannot be interpreted as agreement.

## Complexity
For (n) checkpoints, complete pair coverage requires (n(n-1)/2) comparisons. With (m) observed pairs, this implementation performs (O(n+m)) validation/metadata work plus (O(m)) pair comparisons; it stores the missing-pair list, whose size is (inom n2-m).

## Test
`python -m unittest tests/test_observer_partial_observation.py -v`

## Great Scale mapping
Observer state → signature validation → observed relation edges → missing-edge set → fork precedence → completeness gate → bounded conclusion.

## Profound finding
**Absence of contradiction is not evidence of consistency unless the observation boundary is known.** The system must report both its conclusion and the unobserved portion of the comparison graph.

## Limits
This is a policy classifier over supplied signed checkpoints. It does not provide a network discovery protocol, Merkle consistency proof, trusted time, or proof that the supplied observer set is complete. Signer identity and caller-supplied operational labels do not establish real-world independence.
