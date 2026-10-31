# Great Scale CX — Observer Checkpoint Consistency

## Descent question
CVIX links signed registry transitions, but a signed chain shown to one observer does not prove that all observers see the same history. CX introduces signed checkpoints and comparison rules for detecting obvious conflicting views.

## Checkpoint
A checkpoint binds a log identifier, positive size, head hash, and previous-checkpoint hash. A configured signer signs the canonical body. Observers can retain the exact checkpoint ID and later compare independently received checkpoints.

## Comparison
For two valid checkpoints of the same log:
- same size and same head hash => SAME;
- same size and different head hash => FORK;
- different sizes with a direct predecessor checkpoint link => ORDERED;
- otherwise => INCOMPARABLE.

A FORK result is concrete evidence of incompatible signed views, assuming signer keys and canonicalization are sound. INCOMPARABLE is not proof of a fork; it means the supplied records do not establish ordering.

## Limits
This is not a Merkle transparency log and does not implement general inclusion or consistency proofs. The direct predecessor link is a simple checkpoint chain. It cannot detect a fork if no observer ever compares the conflicting checkpoints, and it does not establish trusted time, global publication, or statistical validity.

## Tests
Tests cover valid signatures, same checkpoint, same-size conflicting heads, linked ordering, missing links, different logs, tampering, untrusted signers, invalid size, and schema mismatch. Run:
`python -m unittest tests/test_observer_checkpoint_consistency.py`

## Great Scale placement
CVIII: signed registry snapshot.
CVIX: signed, hash-linked registry transitions.
**CX: observer-held signed checkpoints and cross-observer fork detection.**

The scientific boundary is now explicit: integrity of a presented history is weaker than evidence that observers share one consistent history.
