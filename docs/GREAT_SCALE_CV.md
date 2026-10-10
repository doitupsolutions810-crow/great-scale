# Great Scale CV — External Anchor Witness

## Motivation
CIV's hash chain detects edits relative to a presented trace, but a party controlling the entire trace can rewrite and rehash it. CV adds an anchor signed by a separately controlled witness.

## Protocol
1. Canonicalize the trace and compute its SHA-256 commitment.
2. Construct a statement with schema, monotonic sequence number, previous anchor identifier, and trace commitment.
3. The external witness signs the canonical statement with Ed25519.
4. A verifier checks the signature, recomputes the trace commitment, and checks expected sequence/predecessor continuity.
5. The witness publishes or retains the signed statement independently of the system being audited.

## Mathematical and cryptographic claims
If the trace changes, its commitment will almost certainly change under SHA-256 collision-resistance assumptions. A valid Ed25519 signature establishes that the corresponding private key signed the statement, assuming key security and correct verification. Sequence and predecessor checks detect gaps or forks relative to a verifier's trusted checkpoint.

## Limits
A signature does not itself prove trustworthy time, that the witness is independent, that the trace came from actual execution, or that the statistical null is true. Operational assurance requires independent key custody, durable publication, checkpoint management, and ideally signed timestamps or multiple witnesses. This is not a blockchain or consensus service by itself.

## Testing
Tests use ephemeral Ed25519 keys to check valid verification and rejection of altered trace, signature, sequence, and predecessor. These tests establish local code behavior only; they do not test key custody or deployment operations.
