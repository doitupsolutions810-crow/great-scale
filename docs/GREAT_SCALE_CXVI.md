# Great Scale CXVI — Scoped Evidence Certificate

## Finding

A single "verified" bit loses information needed to distinguish agreement about a state, agreement about ancestry, completeness of the observed population, and trust in the evidence. These are independent axes and must remain independently represented.

## Formal object

For an evidence bundle (E), define the certificate

\[
\mathcal{C}(E) = (S, L, O, N, K, T, A)
\]

where:
- (S \in \{MATCH, MISMATCH, UNKNOWN\}) is state-summary equivalence;
- (L \in \{SAME, ORDERED, FORK, INCOMPARABLE, NOT\_ASSESSED\}) is the lineage relation;
- (O) is the number of observed records and (N) the declared population size, if known;
- (K) states whether the declared population is complete;
- (T) records the upstream authenticity-verification status and signer threshold evidence;
- (A) records explicit assumptions and evidence identifiers.

The classifier emits one of four dispositions:
1. `CONFLICT_WITHIN_OBSERVED_EVIDENCE` if the state summaries mismatch or a fork is observed;
2. `UNRESOLVED` if state, lineage, or authenticity is unknown/unverified;
3. `PARTIAL_EVIDENCE` if the evidence is internally consistent but the declared population is incomplete;
4. `CONSISTENT_WITHIN_DECLARED_SCOPE` only when the state matches, lineage is SAME/ORDERED, the population is complete, and the caller reports authenticity verified under an explicit trust basis.

A fork in observed evidence dominates missing population coverage, preserving CXII's conservative aggregation rule. "Consistent within declared scope" is intentionally narrower than universal truth.

## Derived invariant: certification is non-promotable by loss of evidence

Let (D(E)) be the certificate disposition. If any required positive predicate is weakened—state MATCH to UNKNOWN, lineage SAME/ORDERED to unresolved, population-complete to incomplete, or authenticity VERIFIED to unverified—then the result must not remain `CONSISTENT_WITHIN_DECLARED_SCOPE).

This is a safety invariant, not a probability estimate: evidence loss cannot manufacture a stronger certification. CXVII adds an optional content-addressed `scope_manifest`; when supplied, the certificate records the manifest binding and refuses consistency on an invalid or mismatched manifest. The regression test `test_downgrading_any_positive_axis_never_retains_consistency` checks all four downgrade paths.

## Key mathematical distinction

\[
D(E)=CONSISTENT \Rightarrow S=MATCH \land L\in\{SAME,ORDERED\}
\land K=1 \land T=VERIFIED.
\]

The converse is only as sound as the correctness of the upstream checks and declared population. This module classifies caller-provided facts; it does **not** verify signatures, prove population completeness, validate a Merkle proof, or establish the trust basis itself.

## Cross-repository inspection result

- Great Scale provides the checkpoint comparator and observer aggregation rules.
- Living Intermediate Control Plane's `probeEvidenceConsole()` reports endpoint availability and an operational source choice. Its `authority` field is not cryptographic trust and must not be mapped directly to `authenticity_status=VERIFIED`.
- TrainLLM documents proposals, approvals, simulation, and rollback, but no concrete shared evidence-ingestion schema was identified in this targeted review.
- CycleKernal documents simulation, monitoring, and audit/event infrastructure; no compatible evidence adapter was established in the inspected README.

Therefore this rung is added to Great Scale as a standalone, tested contract. Cross-repository adapters are deliberately deferred until their actual payload schemas and trust boundaries can be traced end to end.

## Test

Run from repository root:

```bash
PYTHONPATH=. python tests/test_scoped_evidence_certificate.py -v
```

The eleven focused unit tests cover complete scoped consistency, unresolved lineage, fork-over-missing-evidence precedence, incomplete populations, authenticity gating, mismatch handling, population count validation, signer threshold validation, unique evidence identifiers, unassessed lineage, and the no-promotion-under-evidence-loss invariant.

## Limits

This is a mathematical/engineering classification rule, not proof of a production conflict or physical law. The local 11-test run is not a full repository suite, CI run, or deployment verification.
