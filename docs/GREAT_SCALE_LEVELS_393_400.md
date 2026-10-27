# Great Scale — Levels 393–400: Identity Separation Is a State-Space Invariant

**Status:** deterministic source-level collision plus a proposed cross-repository invariant and migration/test contract. Reviewed CycleKernal backend/simulation_core.py on main; related to TrainLLM issue #2. This is an application identity result, not a physical claim.

## Level 393 — Trace identity through the key transformation

CycleKernal's ChatMemoryBridge uses the full user_id as a key in chat_to_civ_map, but creates the civilization record ID from only user_id[:6]. Those are two different equivalence relations: full-string equality for the map and six-character-prefix equality for the state record.

## Level 394 — Construct a deterministic collision

Let u1 = alice123 and u2 = alice199. They are distinct strings, but both have the prefix alice1. The source mapping therefore yields:

key(u1) = user_alice1 = key(u2)

This is a deterministic counterexample; it does not depend on random chance or a birthday-bound approximation.

## Level 395 — Derive state aliasing

The full-ID dictionary can contain both u1 -> user_alice1 and u2 -> user_alice1. Since the universe stores civilizations by civ_id and add_civilization returns an existing record for an existing key, both callers can mutate the same civilization object. Authentication can correctly distinguish u1 and u2 while the storage layer still aliases their private state.

## Level 396 — Formal identity-separation invariant

**Required invariant:** for principals p1 and p2 without an explicit shared-resource grant:

p1 != p2 implies PrivateRecord(p1) != PrivateRecord(p2)

More precisely, internal record assignment must be injective over the admissible principal set, or collisions must be detected and resolved before any private state is shared. A short prefix is not an acceptable uniqueness proof.

## Level 397 — Cross-repository common mode

TrainLLM has a separately tracked six-character user-ID truncation pattern in issue #2. The recurrence in two repositories suggests a shared design smell: presentation-scale identifiers are being reused as storage identity. Fixing only the HTTP authorization boundary does not repair state aliasing underneath it.

## Level 398 — Test identity as a property, not a naming convention

Deterministic regression: create two authenticated principals with the same six-character prefix and different suffixes; mutate one; assert distinct record IDs, disjoint private state, no cross-user reads, and no cross-user WebSocket delivery. Include Unicode normalization, case handling, empty IDs, malformed IDs, and migration collision fixtures where those inputs are permitted by the identity contract.

These are proposed tests; they have not been run against the repository in this review.

## Level 399 — Migration and provenance

Replace prefix keys with server-controlled opaque record IDs and enforce a uniqueness constraint. Build a migration report mapping each legacy key to all source principals; where one legacy record has been shared by multiple identities, do not silently assign the entire record to one principal. Preserve an auditable provenance trail and require an explicit reconciliation policy for ambiguous ownership.

## Level 400 — Falsification gate

**Falsifier:** two distinct principals without a sharing grant resolve to the same mutable private record, or one principal's mutation changes another principal's private view.

**Acceptance gate:** deterministic collision tests pass against the actual application; record IDs are unique under the enforced schema; HTTP and WebSocket isolation tests pass; and migration behavior for pre-existing collisions is reviewed. A successful authentication check alone is not sufficient.

**Profound finding:** principal identity, storage identity, and observation-channel identity must commute consistently through the system. If any mapping collapses two principals, every downstream authorization check can be locally correct yet still protect the wrong shared record.