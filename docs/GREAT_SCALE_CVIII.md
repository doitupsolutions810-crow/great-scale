# Great Scale CVIII — Versioned Registry Provenance

## Descent question
CVII requires signatures across configured fault domains, but the domain registry itself could be silently edited. CVIII binds each checkpoint to a signed, versioned registry.

## Construction
A registry payload is canonical JSON containing schema, positive version, and sorted witness-to-domain assignments. Its SHA-256 digest is signed by a configured registry authority. A checkpoint statement includes trace commitment, sequence, predecessor anchor, registry version, and registry hash. Witness signatures cover this entire statement.

Verification requires a valid registry-authority signature, matching registry hash, expected registry version when supplied, exact checkpoint fields, and the configured threshold of unique trusted witness signatures.

## Mathematical binding
Let R_v be the canonical registry payload at version v and H its SHA-256 function. The checkpoint binds to h_v = H(R_v). Acceptance requires both Verify(authority, R_v, sig_R)=1 and at least k valid witness signatures over S=(H(trace), sequence, predecessor, v, h_v).

## What it establishes
- The registry payload matches its digest and has a valid signature from a configured registry authority.
- The checkpoint is tied to one exact registry version and hash.
- Witnesses not listed in the signed registry do not count.

## Limits
This does not prove the registry authority is honest, the domain assignments reflect real infrastructure, or registry updates were authorized under an external governance process. A valid signature gives authenticity relative to a trusted key, not truth. This also does not provide trusted timestamps, append-only publication, revocation history, or statistical validity.

## Tests
Tests cover valid verification, registry tampering, version mismatch, checkpoint hash substitution, trace changes, unregistered signers, invalid versions, duplicate signers, and empty domains. Run:
`python -m unittest tests/test_registry_provenance.py`

## Great Scale placement
CV: signed trace anchor.
CVI: threshold signatures.
CVII: fault-domain-aware quorum.
**CVIII: checkpoint-bound, signed registry provenance.**

The next open question is how to establish registry update authorization, revocation, and chronology without trusting one mutable registry service.
