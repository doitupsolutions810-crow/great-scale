# Great Scale CXI — Relational Observer Consistency

## Descent question
CX can classify two signed checkpoints. CXI asks what a *set* of observers establishes when their views are compared, while avoiding the mistake of treating multiple labels as independent witnesses.

## Formal rule
Let the supplied checkpoints be (C_1,\ldots,C_n), each with trusted signature and signer identity (s_i). Require:
- valid signature for every checkpoint;
- pairwise-distinct signer IDs;
- (n \ge q_s), the configured signer quorum;
- optionally, at least (q_d) distinct caller-configured fault domains.

For every pair, run the CX relation classifier. Overall classification is:
- **FORK** if any pair reports FORK;
- **INCOMPARABLE** if no pair reports FORK and at least one pair is incomparable;
- **CONSISTENT** only if every pair is SAME or ORDERED.

This is deliberately conservative: one conflict dominates; missing ordering is not silently converted into consistency.

## Test command
`python -m unittest tests/test_observer_view_comparison.py -v`

## Great Scale mapping
Observer identity → signature validity → distinct-signer quorum → optional fault-domain diversity → pairwise relations → aggregate classification → evidence boundary.

## Profound finding
**Agreement is not a count; it is a relation constrained by independence assumptions.** Two matching records from one signer are not two independent observations. Distinct signer IDs improve bookkeeping, but actual independence requires operational evidence about key custody, deployment, ownership, and failure domains.

## Limits
This is a set-comparison policy over supplied signed checkpoints, not a transparency log. It cannot establish that no unobserved fork exists, prove true operational independence, supply trusted time, guarantee global publication, or validate the underlying scientific claim.
