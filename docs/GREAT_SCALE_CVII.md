# Great Scale CVII — Fault-Domain-Aware Quorums

## Descent question
CVI counts valid signatures from distinct configured keys. But different keys may share a cloud account, administrator, operator, region, or evidence feed. A key quorum can therefore hide a common failure domain.

## Acceptance rule
Let V be the set of trusted witnesses whose signatures verify over the expected canonical checkpoint. Let d(i) be the configured fault-domain label for witness i. Accept only if

\[
|V|\ge k \quad\text{and}\quad |\{d(i):i\in V\}|\ge d.
\]

Here k is the signature threshold and d is the minimum number of represented fault domains, with 1 <= d <= k. The verifier also checks the trace commitment, sequence, predecessor anchor, unique witness IDs, and complete domain registry.

## Implementation
`fault_domain_quorum.py` builds on the CVI checkpoint statement and canonical signature bytes. It counts valid trusted signatures and the number of distinct configured domains represented by those valid signers.

## What it establishes
- At least k trusted unique witness keys signed the same expected statement.
- Those signers span at least d domain labels in the configured registry.
- Misconfigured missing/blank domain assignments and duplicate identities are rejected.

## What it does not establish
Domain labels are declarations, not cryptographic facts. This cannot independently verify common ownership, shared infrastructure, correlated upstream data, or true operational independence. The model may understate correlated failures if its domain registry is incomplete. It also does not establish statistical validity of the evidence trace.

## Tests
Tests cover quorum pass/fail, same-domain concentration, tampered signatures, missing domain mappings, impossible policy, duplicate identities, trace mismatch, and empty labels. Run:
`python -m unittest tests/test_fault_domain_quorum.py`

## Great Scale placement
- CV: external signature anchor.
- CVI: k-of-n distinct key signatures.
- **CVII: k signatures plus d declared fault domains.**

The new scientific distinction is between cryptographic multiplicity and fault diversity. A quorum is only as robust as its threat model and domain classification.
