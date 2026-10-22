# Great Scale CXLIX — Joint Behavioral–Property Fixed Point

## Question

Can a finite deterministic state model be compressed while preserving both its
observable behavior and a declared collection of Boolean state properties?

## Model

Let S be finite. Each state s has an observation O(s), a finite set of enabled
actions A(s), and for each enabled action a a successor T(s,a) in S. Let required
properties be P_1,...,P_m.

Initialize a partition by the joint signature
\[
\sigma_0(s)=(O(s),P_1(s),\ldots,P_m(s)).
\]
Then repeatedly refine blocks by enabled-action sets and successor block IDs:
\[
\sigma_{n+1}(s)=\big(\sigma_0(s),A(s),([T(s,a)])_{a\in A(s)}\big).
\]
Stop when the induced partition no longer changes.

## Guarantees under assumptions

For a finite deterministic transition system, this monotone refinement terminates
because each strict iteration increases the number of blocks and at most |S|
blocks exist. At the fixed point, states in a block share observations, required
property values, enabled actions, and successor quotient classes for each action.
The implementation checks these conditions after convergence.

The output is the coarsest stable refinement of the initial observation/property
partition under this signature rule. It does not claim to model nondeterminism,
probabilistic transitions, infinite-state systems, or temporal properties not
encoded by the preserved observations and state properties.

## Scientific interpretation

This is a formal finite-model guarantee, not empirical proof that the model
faithfully represents a real system. The property list is part of the scientific
specification: adding a required property may split the quotient.

## Tests

Six authored unit tests cover hidden safety distinctions, propagation of a
successor distinction, valid merging, enabled-action differences, invalid
successors, and incomplete maps. Tests must be run in CI or locally before
claiming execution success.
