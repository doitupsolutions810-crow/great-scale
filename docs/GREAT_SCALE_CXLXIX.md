# Great Scale CXLXIX — Differential Quotient and Terminal-State Separation

## Analysis finding
The CXLXVIII API used `None` as the terminal-transition marker while the canonical encoder also supports `None` as a legitimate state label. This overloaded value made a transition to the state labelled `None` indistinguishable from a terminal edge. Typed identity was improved at the storage layer, but a sentinel collision remained at the transition-semantics layer.

## Correction
The model now exports a dedicated `TERMINAL` sentinel. A successor label of `None` resolves to the canonical state ID for `None`; `TERMINAL` represents termination. This keeps control-flow semantics separate from the state-label domain.

## Mathematics
Let (S) be the state-label set and (E) the canonical encoder. A transition target must be tagged as either a state reference or terminal:

`Target = State(E(s)) | Terminal`

This is a disjoint sum, not a shared untagged value. It prevents any valid state label from being confused with control-flow termination.

The quotient comparison obligation remains:

`Q_new(M) = Q_reference(M)`

where equality means equality of equivalence classes after canonical-ID normalization.

## Tests authored
- A valid state labelled `None` can be referenced by an edge.
- A distinct terminal sentinel represents termination.
- Differential partition refinement compares the implementation against an independently structured reference refinement on a small deterministic model.

## Validation status
Tests have been authored but not independently executed in this workflow. Vercel status and Python test execution are separate signals. The API is still additive and is not yet a drop-in replacement for every legacy certificate path.
