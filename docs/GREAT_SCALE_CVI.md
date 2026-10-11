# Great Scale CVI — Threshold Witness Checkpoints

## Question
CV added an externally signed anchor, but one signing authority can remain a single point of trust or failure. CVI asks whether a checkpoint should be accepted only when enough distinct configured witnesses sign the same statement.

## Mathematical rule
For statement S and trusted registry W, accept iff
A(S) = sum over i in W of 1{Verify(public_key_i, S, signature_i) = valid} >= k.
Require unique witness IDs and exact agreement with the expected trace commitment, sequence, and predecessor anchor. Unknown IDs and invalid signatures contribute zero.

The implementation signs canonical JSON with Ed25519 and commits to the trace using SHA-256.

## What this establishes
- At least k distinct configured keys signed the same canonical statement.
- The checkpoint binds to the expected trace representation.
- Changed trace, sequence, predecessor, or insufficient signatures are rejected.

## What it does not establish
- That witness operators are truly independent or uncompromised.
- Key custody, identity vetting, trusted time, publication, or availability.
- Byzantine consensus or protection if at least k keys collude.
- Statistical validity of the underlying scientific claim.

Nominally separate keys may share an operator, host, cloud account, or upstream data source. Threshold policy must match a stated threat model.

## Test plan
Unit tests cover threshold success/failure, trace tampering, sequence and predecessor mismatch, signature tampering, duplicate identities, unknown witnesses, and invalid thresholds. Run: python -m unittest tests/test_threshold_witness_checkpoint.py

## Great Scale placement
- C–CIII: statistical evidence and predictable/sequential validity.
- CIV: hash-chained trace integrity.
- CV: externally signed trace anchor.
- CVI: threshold-witness agreement on one anchored statement.

The descent shifts from “who signed?” to “how many distinct trusted keys signed the same statement under a declared trust policy?” This remains conditional on registry quality and witness independence.
