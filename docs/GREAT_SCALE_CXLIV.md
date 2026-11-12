# Great Scale CXLIV — Transition-Preserving State

## Finding

Compression that preserves current outcomes can still be invalid for sequential planning. A compressed state is dynamically well-defined only when every pair merged into the same key has matching observations, matching action availability, matching terminal behavior, and successors in the same compressed key under every shared enabled action.

For deterministic finite systems, let K:S→Q be the compression key, E(s,a) action availability, T(s,a) transition, and O(s) observation. The checked conditions are:

- K(s)=K(t) implies O(s)=O(t).
- K(s)=K(t) implies E(s,a)=E(t,a) for every audited action.
- For every enabled shared action, K(s)=K(t) implies K(T(s,a))=K(T(t,a)).
- Terminal/undefined transitions must agree.

These conditions make the quotient transition function independent of which representative was chosen. The implementation checks a supplied finite domain; it does not prove properties outside that domain and does not claim probabilistic bisimulation.

## Counterexample

Let left and right have the same compressed key and same current observation. Under action go, left transitions to doneA and right to doneB, whose keys differ. The compression passes a present-state comparison but fails transition congruence. A planner operating only on the shared key cannot know which future state it will reach.

## Test plan

Five unit tests cover a safe quotient, divergent successor keys, differing action availability, terminal mismatch, and pairs that are not merged. Tests are authored but must be executed in CI or locally before being reported as passing.
