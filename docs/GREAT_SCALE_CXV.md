# Great Scale CXV — State Equality Is Not Lineage Equality

## Finding

Two signed checkpoints can describe the same log state while making different claims about the checkpoint from which that state descended. Equal state summaries are not sufficient evidence of equal checkpoint lineage.

## Formal statement

For checkpoint C, define the state projection:

    sigma(C) = (logID(C), size(C), head(C))

and its immediate lineage pointer p(C) = previousCheckpointHash(C).

If sigma(A) = sigma(B) but p(A) != p(B), then the records agree on the declared state summary but disagree on the immediate predecessor claim. Under this direct-link evidence model:

    sigma(A) = sigma(B) AND p(A) != p(B)
      => relation(A,B) = INCOMPARABLE

This is not classified as a content FORK because the declared head hashes match. It is also not SAME, because the available evidence does not establish the same lineage. The distinction preserves both facts rather than collapsing one into the other.

## Why it matters

The earlier comparator returned SAME whenever size and head hash matched, without checking the predecessor pointer. That erased a lineage discrepancy from the relation graph. Since CXI and CXII treat only SAME and ORDERED as evidence for a consistent supplied set, the corrected classification fails closed: an equal-state/different-lineage pair prevents a consistency certification.

## Great Scale map

| Layer | Object | Check | Safe conclusion |
|---|---|---|---|
| State | sigma(C) | log ID, size, head hash | Declared state summaries match |
| Lineage | p(C) | immediate predecessor pointer | Lineage claims match or differ |
| Relation | Pair (A,B) | state + lineage | SAME, FORK, ORDERED, or INCOMPARABLE |
| Aggregate | Pairwise relation graph | Only SAME/ORDERED accepted | Unresolved lineage blocks consistency |
| Scope | Supplied checkpoint set | CXIV population boundary | No claim about unseen checkpoints |

## Cross-repository integration boundary

The control-plane repositories describe evidence consoles, attestation, federation digests, and governance. This CXV rule is an appropriate upstream adapter invariant: consumers should preserve INCOMPARABLE as unresolved evidence and must not silently convert it into an accepted attestation. This change is integrated into Great Scale's checkpoint comparator; direct changes to other repositories are deferred until their concrete ingestion paths and schemas are reviewed.

## Test and run

Regression: test_same_size_same_state_different_lineage_is_incomparable.

Run from the repository root:
- PYTHONPATH=. python tests/test_observer_checkpoint_consistency.py -v
- PYTHONPATH=. python tests/test_observer_view_comparison.py -v
- PYTHONPATH=. python tests/test_observer_partial_observation.py -v

## Limits

The predecessor pointer is a direct link, not a general Merkle consistency proof. Equal head hashes are only as meaningful as the head-hash construction and trust assumptions. This is a conservative evidence classification, not proof of a real-world fork or of global completeness.
