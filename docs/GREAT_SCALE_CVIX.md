# Great Scale CVIX — Registry Transition Chain

## Descent question
CVIII binds a checkpoint to a signed registry version, but versioning alone does not prove how one registry succeeded another. CVIX makes each registry update an explicit signed transition linked to its predecessor.

## Transition
For current registry payload R_v and next payload R_(v+1), define h_v = SHA256(canonical_json(R_v)). A transition body contains schema, parent_registry_hash=h_v, next registry payload, and its digest. The authority signs the complete body.

Verification requires a valid authority signature, matching payload digest, the expected parent hash, and exactly monotonic version advancement. Genesis uses a fixed all-zero parent hash and version 1.

## What it establishes
- A configured authority signed each transition body.
- The next registry is linked to the expected previous registry hash.
- Version skipping, stale replay against the wrong parent, and body tampering are rejected.
- A supplied transition sequence can be replayed deterministically to reconstruct the latest registry.

## Limits
A signed chain is not automatically an independently published append-only log. The authority can create a competing fork, and a verifier cannot detect a withheld history without an external checkpoint/gossip mechanism. This does not prove the authority's policy is legitimate, domain labels are true, or evidence is statistically valid.

## Tests
Covers genesis, valid successor, deterministic reconstruction, wrong parent, skipped version, payload tampering, signature tampering, wrong authority, and replay. Run:
`python -m unittest tests/test_registry_transition_chain.py`

## Great Scale placement
CVII: fault-domain-aware quorum.
CVIII: signed registry provenance bound to checkpoints.
**CVIX: monotonic, hash-linked registry transitions.**

Next open issue: fork detection. Hash links establish ancestry inside a presented chain, not that every observer sees the same chain.
