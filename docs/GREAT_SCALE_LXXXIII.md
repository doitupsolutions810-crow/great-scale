# Great Scale LXXXIII — Provenance Closure and Dependency Revocation

## Pinned finding
A conclusion's authority depends on its evidence and on upstream certificates it relies upon. If an upstream certificate fails, all transitive descendants must be marked stale or invalidated; unrelated branches should remain intact. Recovery is bottom-up: validate the root, then revalidate descendants against the restored dependency chain.

## Graph model
Represent certificates as a directed acyclic graph G=(V,E), where u→v means v depends on u. Let D(u) be all nodes reachable by a directed path from u. If root u is invalidated, set S(u)=INVALID and mark every v in D(u) as STALE pending revalidation. Nodes outside {u}∪D(u) are not automatically changed.

A node v may be revalidated only when its required direct dependencies are valid and fresh evidence supports v. A practical system should record evidence hashes, time, evaluator, calibration version, method version, and reason for each status transition.

## Implementation boundary
The included pure-Python graph enforces insertion of dependencies before dependents, rejects duplicate IDs and missing dependencies, propagates revocation transitively, and requires dependencies to be valid before revalidation. This insertion rule prevents cycles in this simple model. It stores in-memory state only; it is not a tamper-proof ledger or production provenance database.

## Mathematics versus science
The descendant-closure behavior follows from graph reachability. Whether a dependency list is complete, a certificate is empirically justified, or a purportedly independent branch is truly independent requires domain-specific evidence. Unit tests test code paths, not the truth of real-world claims.

## Great Scale progression
- LXXX: bounded-error observation certificates.
- LXXXI: bias floor and adaptive stopping.
- LXXXII: calibration validity and assumption drift.
- LXXXIII: provenance closure and selective revocation.
- Proposed next: LXXXIV — Evidence Independence and Common-Cause Failure: determine whether apparently separate evidence paths share a hidden failure source.
