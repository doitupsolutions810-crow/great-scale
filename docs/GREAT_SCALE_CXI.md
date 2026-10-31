# Great Scale CXI — Independent Witness Gossip

## Question
CX detects conflicting signed checkpoints only when they are compared. CXI formalizes independently signed observer receipts and a small analyzer that compares the checkpoints those observers report.

## Protocol
An observer signs a receipt binding its identity to the exact checkpoint ID and checkpoint bytes. The analyzer validates both the log checkpoint signature and the observer receipt signature, counts unique trusted observer identities, and groups reports by (log_id, size). Multiple distinct head hashes for the same log and size yield FORK_DETECTED.

## Status meanings
- FORK_DETECTED: verified observers supplied incompatible heads at the same log size.
- NO_CONFLICT_OBSERVED: enough unique verified observers were supplied, and no conflict was found in this evidence set.
- INSUFFICIENT_OBSERVERS: fewer than the configured minimum unique verified observers were supplied, and no fork was established.

## Mathematics
Let O be the set of unique trusted observers with valid receipts. For log identifier l and size n, let H(l,n) be the set of distinct reported head hashes. A conflict exists when |H(l,n)| > 1. Evidence coverage passes the configured floor only when |O| >= k.

This is a finite-evidence detector, not a proof of global consistency. The observations may be correlated, observers may share infrastructure, and unobserved or withheld views remain invisible.

## Tests
Tests cover receipt validation, tampering, untrusted observers, same-view agreement, conflict detection, duplicate observer identities, and insufficient witness count. Run:
`python -m unittest tests/test_cxi_independent_witness_gossip.py`

## Great Scale mapping
CVIII binds a registry snapshot; CVIX links transitions; CX compares signed checkpoints; CXI compares checkpoint reports from independently identified observers.

## Limits / next rung
A minimum observer count does not prove independence. The next question is how to quantify correlated failure domains and guarantee meaningful witness diversity without treating declared labels as proof of real-world independence.
