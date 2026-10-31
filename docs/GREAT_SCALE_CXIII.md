# Great Scale CXIII — Directional Evidence and Causal Order

## Repository finding
The CX comparator previously returned `ORDERED` if either checkpoint named the other as its predecessor, even when the checkpoint with the smaller size pointed to the larger checkpoint. That made the predecessor relation effectively symmetric and could report an impossible reverse ordering as valid.

## Correction
For checkpoints with different sizes, only the later checkpoint may directly name the earlier checkpoint's checkpoint ID as its predecessor. A backward-pointing link is classified as `INCOMPARABLE`, not `ORDERED` or `FORK`.

\[s(C_a)<s(C_b) \land parent(C_b)=id(C_a) \Rightarrow ORDERED\]

\[s(C_a)<s(C_b) \land parent(C_a)=id(C_b) \Rightarrow INCOMPARABLE\]

This is a local consistency rule, not a complete append-only log proof.

## Additional input hardening
CXI quorum thresholds now require positive integers, rejecting booleans and floats instead of allowing values such as `2.5` to pass a numeric comparison.

## Great Scale mapping
Signed state → size order → directional predecessor edge → relation classification → aggregate evidence → bounded conclusion.

## Profound finding
**A relation that encodes causality must preserve direction.** If the evidence edge is treated as symmetric, the classifier can manufacture an ordering that the underlying structure does not support.

## Verification
Targeted regression added: `test_reverse_predecessor_does_not_reverse_causality`. Run:
`PYTHONPATH=. python tests/test_observer_checkpoint_consistency.py -v`

CI has not yet been confirmed green. The GitHub job-log endpoint has returned missing-log errors, and multiple pre-existing workflows also fail on this branch. Do not treat the repository as fully verified until the test workflows complete successfully.
