# Great Scale — Descent CLXIX: A valid evidence chain can still omit a committed event

## Finding

Capability Authority’s PR #12 exposed a separate integrity boundary from hash-chain validity. At the pre-fix head `7ce3dba1532173781030ee60f6a1f17f8dbf6815`, each `EvidenceIndex` instance loaded the JSON projection once and protected it only with its own `threading.RLock`. Ingest appended to SQLite, then wrote `[*self._docs, event]`. Two processes sharing the same SQLite ledger and projection path could therefore begin with the same stale snapshot and overwrite each other’s JSON update. [1] [2]

This was reproduced against the production classes with temporary files. Two writer processes committed `evt-A` and `evt-B`; SQLite reported a valid chain of length two, but the projection contained only one event. The failing regression identified the missing `evt-A`. This establishes a code-level race when writers share the ledger and projection filesystem. It does not establish that a deployed service lost evidence.

The deeper result is that **chain integrity does not imply query completeness**. A correct digest chain can contain every event while the materialized query surface silently omits one. Source authenticity is a third independent property: a valid digest also does not prove who supplied the event.

## Contract

Let:

- \(L_t\) be the ordered SQLite ledger rows in a consistent snapshot at time \(t\);
- \(V(L_t)\) mean every predecessor link, normalized event identity, and event digest verifies;
- \(M(L_t)\) be the JSON projection materialized from those verified rows, preserving their payloads, order, and stored digest;
- \(P_t\) be the actual JSON projection after a synchronization;
- \(A(e)\) mean the producer of event \(e\) is authenticated under the system’s source policy.

For every successful synchronization, require

\[
V(L_t)=1 \quad\land\quad P_{t^+}=M(L_t).
\]

A query must filter the synchronized ledger snapshot, not a process-local cache that may predate committed rows. If the ledger cannot be verified, the query must fail closed rather than present a stale projection as current.

These predicates do different work:

\[
\text{ChainValid}(e) \not\Rightarrow \text{ProjectionComplete}(e)
\quad\text{and}\quad
\text{ChainValid}(e) \not\Rightarrow A(e).
\]

The system-level Great Scale acceptance contract is therefore a vector, not a single green scalar:

\[
\operatorname{MayPromote}(e)=
C \land T \land V(L) \land [P=M(L)] \land A(e) \land G,
\]

where \(C\) binds the current candidate and base, \(T\) proves the named test step completed successfully, \(V(L)\) verifies the ledger, \(P=M(L)\) proves query-projection completeness, \(A(e)\) binds the event to an authenticated source, and \(G\) is independent server-side enforcement. The existing Great Scale science scalar \(\Psi=\mathrm{CONE}+S\) remains separate; its value cannot substitute for any evidence, execution, provenance, or enforcement predicate. This equation is a proposed acceptance contract, not a claim that all terms are already enforced by Great Scale.

## Cross-repository evidence

The Capability Authority mitigation adds `read_verified_events()`, which reads one SQLite snapshot and verifies predecessor links, stored event IDs, and digests before returning rows. `EvidenceIndex.ingest`, `query`, and `stats` refresh the materialized JSON view under a persistent inter-process path lock. The regression covers stale-view repair, two spawned writer processes, and fail-closed behavior on a corrupted ledger. The change is on Capability Authority PR #12 at commit `00b691dc847108a6df1a6850f0434d35f78175be`. [3] [4] [5] [6]

This closes the observed lost-update path for processes sharing the same ledger, projection path, and filesystem lock semantics. It does not make SQLite and JSON a single cross-store transaction. A committed ledger event can exist briefly before its projection is refreshed; the next query re-verifies and materializes the ledger. The full-chain read is \(O(n)\) in ledger length and memory, so a future scale-up may replace per-query rebuilding with a transactional database read model or a verified incremental cursor.

The other repository audits show why the predicates must remain independent:

- Great Scale’s CLXIV force/evidence test defines a truth-table predicate in the test module; it is a model of the policy, not a call into the Living Control Plane implementation. The CLXVIII CI evidence classifier is likewise a model, not an authenticated GitHub collector. Model results must be labeled as model results. [7] [8]
- The full Great Scale aggregate also exposed a CLXV reachability-audit false positive: the AST checker recognized direct test calls but missed a literal registry dispatched by `for test in tests: test()`. We added a positive dispatched-registry fixture and negative unexecuted-registry fixture while preserving rejection of bare references. This is still static syntax evidence, not runtime coverage.
- Living Intermediate Control Plane PR #28 does import and test its new production authorization helper. However, the exact PR tree still contains a TypeScript-only `export type` in the JavaScript evidence-console module. Its canonical self-test imports that module and stops during parsing; the parser correction is in separate open PR #27. The hosted PR #28 job observed in the audit had zero steps, so its tests were not demonstrated as executed. [9] [10] [11]
- CycleKernal PR #9 builds an internally consistent fitness witness from supplied symbolic inputs. Its `metric_source="relay"` label is assigned by the caller and is not authenticated producer evidence. The bridge also contains a Python syntax error in its parser path at the inspected head, while the fusion model tests can pass without importing that bridge. No live relay execution or external origin attestation is claimed. [12] [13] [14]

## Test, verify, run

The pre-fix reproduction had a valid SQLite chain of length two and a JSON projection missing one committed ID. The new test first failed on that original source tree, with `evt-A` absent from the projection. After the fix, the tested Capability Authority tree was `1caf047fd17b7e157b21f5300cb9f9ba84a55f4c`:

- `python3 tests/test_evidence_index_projection_consistency.py` — **3/3 passed**, including stale projection repair, simultaneous spawned writers, and rejection of an invalid chain.
- `python3 tests/test_evidence_index_fail_closed.py` — **5/5 passed** against the production SQLite warehouse.
- `make test` — **exit 0**; all seven wired test modules passed.
- `bash scripts/run_ci_local.sh` — **exit 0**, printed `ALL GREEN`; it ran the same test set as the hosted Lab workflow, followed by the repository demos.
- `make -n test` and `git diff --check` — **exit 0**.
- `python3 test_great_scale_clviii_test_manifest_completeness.py` — **10/10 passed**, exit code **0**, including executed- and unexecuted-registry cases.
- Great Scale `npm run all` — **exit 0** after correcting the registry-dispatch false positive; all physics, geometry, topology, and evidence/CI contract tests in the canonical aggregate completed.

The Capability Authority fix was committed and pushed to PR #12 as `00b691dc847108a6df1a6850f0434d35f78175be`; the PR head is `00b691dc…` and its base is `0b22ec32…`. Exact-head `pull_request` run `40414560305` completed with both `test` and `slim-probe` jobs failing before runner assignment, with zero steps. GitHub’s annotations on both jobs state that the account is locked due to a billing issue. This is **BLOCKED**, not an application-test failure; local passes do not clear the provider block. No hosted pass, merge enforcement, or deployment is claimed. [6] [14] [15]

## Great Scale interpretation

The new measurable quantity is projection completeness, not another contribution to \(\Psi\). For a verified ledger snapshot, let \(\delta(e)\) be its stored receipt digest (`_digest` in the projection); this digest, not the optional caller idempotency key, identifies a committed row for comparison. Define

\[
\kappa_t=\frac{|\{\delta(p):p\in P_{t^+}\}\cap\{\delta(l):l\in L_t\}|}{|\{\delta(l):l\in L_t\}|},
\]

with \(\kappa_t=1\) for an empty ledger by convention. The acceptance boundary requires both \(V(L_t)=1\) and \(P_{t^+}=M(L_t)\); consequently \(\kappa_t=1\) and the ordered digest sequences match. A valid chain with \(\kappa_t<1\) is incomplete evidence, not a partial pass. This ratio is only a diagnostic. It cannot authenticate event origin or prove that a test step ran.

The decisive test is falsifiable: create two index instances before either writer commits, let independent processes append different event IDs to one SQLite ledger, then assert that the verified chain, persisted projection, and query result contain the same ordered event set. The pre-fix code fails that test; the integrated production-path regression now passes it.

## References

[1]: https://github.com/doitupsolutions810-crow/capability-authority/blob/7ce3dba1532173781030ee60f6a1f17f8dbf6815/evidence/index.py "Capability Authority pre-fix evidence index"
[2]: https://github.com/doitupsolutions810-crow/capability-authority/blob/7ce3dba1532173781030ee60f6a1f17f8dbf6815/evidence/warehouse.py "Capability Authority pre-fix evidence warehouse"
[3]: https://github.com/doitupsolutions810-crow/capability-authority/blob/00b691dc847108a6df1a6850f0434d35f78175be/evidence/index.py "Capability Authority reconciled evidence projection"
[4]: https://github.com/doitupsolutions810-crow/capability-authority/blob/00b691dc847108a6df1a6850f0434d35f78175be/evidence/warehouse.py "Capability Authority verified ledger snapshot"
[5]: https://github.com/doitupsolutions810-crow/capability-authority/blob/00b691dc847108a6df1a6850f0434d35f78175be/tests/test_evidence_index_projection_consistency.py "Projection consistency regressions"
[6]: https://github.com/doitupsolutions810-crow/capability-authority/pull/12 "Capability Authority PR 12"
[7]: https://github.com/doitupsolutions810-crow/great-scale/blob/11e2ac6b96532cb14d2cd71ff134b5c774a3dcdf/test_great_scale_clxiv_evidence_authorization_independence.py "Great Scale CLXIV policy model"
[8]: https://github.com/doitupsolutions810-crow/great-scale/blob/11e2ac6b96532cb14d2cd71ff134b5c774a3dcdf/test_great_scale_clviii_three_valued_ci_evidence.py "Great Scale CLXVIII CI evidence model"
[9]: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/28 "Living Intermediate Control Plane PR 28"
[10]: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/blob/bc32730353be965a9844d51c20f498c2daa0d1b4/lib/procurement-evidence-policy.mjs "Living Control Plane evidence authorization helper"
[11]: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/27 "Living Control Plane parser correction PR 27"
[12]: https://github.com/doitupsolutions810-crow/CycleKernal/pull/9 "CycleKernal PR 9"
[13]: https://github.com/doitupsolutions810-crow/CycleKernal/blob/d82f381f6ab1408f40aa11e8268ee6c8fc0238c8/src/bridge/main.py "CycleKernal relay bridge at audited head"
[14]: https://github.com/doitupsolutions810-crow/capability-authority/actions/runs/40414560305 "Capability Authority exact-head workflow run"
[15]: https://api.github.com/repos/doitupsolutions810-crow/capability-authority/check-runs/121893492172/annotations "Billing-lock annotation on the exact-head test check"
