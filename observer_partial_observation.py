"""CXII: conservative consistency classification under partial observation.

A missing pairwise comparison is not evidence of agreement. A witnessed fork
is actionable even if other comparisons are missing; consistency requires
complete pair coverage and every pair classified SAME or ORDERED.
"""
from __future__ import annotations

from itertools import combinations
from typing import Any, Mapping, Sequence
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from observer_checkpoint_consistency import compare_checkpoints, verify_checkpoint


def compare_partial_observer_views(
    checkpoints: Sequence[Mapping[str, Any]],
    trusted_signers: Mapping[str, Ed25519PublicKey],
    observed_pairs: Sequence[Sequence[int]],
    *,
    minimum_distinct_signers: int = 2,
) -> dict[str, Any]:
    """Compare only observed index-pairs and report the evidence boundary.

    observed_pairs contains pairs of zero-based checkpoint indices. Duplicate
    pairs, self-pairs, invalid indices, invalid signatures, duplicate signer
    identities, or an unmet signer quorum raise ValueError.
    """
    if isinstance(minimum_distinct_signers, bool) or not isinstance(minimum_distinct_signers, int) or minimum_distinct_signers < 1:
        raise ValueError("minimum_distinct_signers must be a positive integer")
    if not checkpoints:
        raise ValueError("at least one checkpoint is required")

    signer_ids = []
    for checkpoint in checkpoints:
        if not verify_checkpoint(checkpoint, trusted_signers):
            raise ValueError("all checkpoints must have valid signatures from trusted signers")
        signer_id = checkpoint.get("signer_id")
        if not isinstance(signer_id, str) or not signer_id:
            raise ValueError("checkpoint signer_id must be non-empty")
        signer_ids.append(signer_id)

    if len(set(signer_ids)) != len(signer_ids):
        raise ValueError("each observer view must come from a distinct signer")
    if len(set(signer_ids)) < minimum_distinct_signers:
        raise ValueError("insufficient distinct signer quorum")

    expected = {tuple(pair) for pair in combinations(range(len(checkpoints)), 2)}
    observed: set[tuple[int, int]] = set()
    for pair in observed_pairs:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("each observed pair must contain two indices")
        i, j = pair
        if isinstance(i, bool) or isinstance(j, bool) or not isinstance(i, int) or not isinstance(j, int):
            raise ValueError("pair indices must be integers")
        if i < 0 or j < 0 or i >= len(checkpoints) or j >= len(checkpoints) or i == j:
            raise ValueError("observed pair indices must be distinct valid checkpoint indices")
        key = (min(i, j), max(i, j))
        if key in observed:
            raise ValueError("duplicate observed pair")
        observed.add(key)

    pair_results = []
    for i, j in sorted(observed):
        relation = compare_checkpoints(checkpoints[i], checkpoints[j], trusted_signers)
        pair_results.append({"left_index": i, "right_index": j,
                             "left_signer": signer_ids[i], "right_signer": signer_ids[j],
                             "relation": relation})

    missing = sorted(expected - observed)
    relations = [item["relation"] for item in pair_results]
    if "FORK" in relations:
        classification = "FORK"
    elif missing:
        classification = "PARTIAL_EVIDENCE"
    elif "INCOMPARABLE" in relations:
        classification = "INCOMPARABLE"
    else:
        classification = "CONSISTENT"

    return {
        "schema": "great-scale-partial-observation-v1",
        "classification": classification,
        "observer_count": len(checkpoints),
        "expected_pair_count": len(expected),
        "observed_pair_count": len(observed),
        "missing_pairs": [{"left_index": i, "right_index": j,
                           "left_signer": signer_ids[i], "right_signer": signer_ids[j]}
                          for i, j in missing],
        "pairwise_results": pair_results,
        "consistency_established_for_supplied_set": classification == "CONSISTENT",
        "limitations": [
            "a missing comparison is unknown, not agreement",
            "FORK means a conflicting pair was observed; it does not enumerate all forks",
            "CONSISTENT applies only to the supplied checkpoints and complete pair coverage",
            "distinct signer IDs do not prove independent operators, keys, or infrastructure",
            "no trusted time, global publication completeness, or scientific validity is established",
        ],
    }
