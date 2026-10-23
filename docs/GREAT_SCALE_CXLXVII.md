# Great Scale CXLXVII — Typed Identity Meets Runtime Equality

## Question
Does a canonical typed encoder guarantee that a model can represent two labels as distinct states?

## Finding
No. The encoder can distinguish `True` from `1`, but Python's equality and hashing treat them as equal: `True == 1` and `hash(True) == hash(1)`. Consequently, ordinary sets and dictionaries collapse these labels before the certificate layer can preserve them. Canonical serialization alone cannot repair a collision in the host-language data model.

## Invariant
For every pair of submitted state labels (a,b), require either:
- (a=b) and their canonical encodings agree; or
- their canonical encodings differ and the host model can represent them as distinct keys.

This implementation fails closed when (a == b) but their canonical encodings differ, before constructing the state-domain set. Callers needing such values should use distinct external canonical IDs as model states.

## Scope and limits
This guard detects equality-colliding labels in the supplied state sequence. It does not make Python mappings capable of expressing colliding action keys; callers must not construct action maps that rely on distinctions Python has already erased. A future model API could use canonical IDs as primary keys end-to-end.

## Tests
Regression tests cover encoder distinction, early rejection of `[True, 1]`, a valid `[1, "1"]` certificate, and the mapping-domain collapse hazard. The tests are authored; execution status must be reported separately from CI status.

## Great Scale interpretation
The descent moves from representation-level identity (CXLXIV), through certificate integration and differential testing (CXLXV), and independent verification (CXLXVI), to the boundary between encoded identity and runtime identity (CXLXVII). The result is a concrete engineering constraint, not a claim about physical reality.
