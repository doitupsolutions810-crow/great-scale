# Descent CLXXIX — Producer–Consumer Contract Divergence Across Control Plane PRs

## Finding

The two open Control Plane candidates implement materially different evidence-console contracts. They are not presently interchangeable and should not be merged or treated as one validated design without an explicit contract decision and cross-repository conformance tests.

## Evidence inspected

- Control Plane PR #29: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/29
- Control Plane PR #31: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/31
- PR #29 changes `lib/evidence-console.mjs`, `lib/evidence-authorization.mjs`, `integrate.mjs`, `package.json`, and evidence-console tests.
- PR #31 changes the same core paths and adds supply-chain evidence/attestation gates.

## Concrete incompatibilities

| Contract dimension | PR #29 candidate | PR #31 candidate | Consequence |
|---|---|---|---|
| Contract runtime | `read-only-dynamic` | `static` | A producer conforming to one candidate can be rejected by the other. |
| Gate identifiers | E0–E6, explicitly described as console-contract checks | G0–G6, used as production readiness gates | The same field name/shape does not establish equivalent semantics. |
| Source authenticity | Requires source identity, key ID, digest, and Ed25519 signature verified against a configured public key | Shown patch validates status/schema and timestamps but does not establish the same signature-verification contract | Contract validity and source authenticity are not equivalent. |
| Status contract | 5.4.0 with dynamic runtime | 5.4.0 with static runtime | Matching version string is insufficient to establish compatibility. |
| Test manifest | `node --test test/evidence-authorization.test.mjs test/evidence-console.test.mjs test/runtime-contract.test.mjs` | `node --test test/evidence-console.test.mjs` | PR #31's aggregate test script does not directly run the authorization and runtime-contract suites added in PR #29. |
| Procurement integration | Public contract authorization plus explicit local fallback policy | Adds supply-chain evidence authorization to the procurement path | The combined candidate needs tests proving both gates are mandatory at every procurement entry point. |

## Deeper result

The trust chain has at least three separate predicates:

1. **Conformance:** payload and independently fetched schema satisfy one pinned contract.
2. **Authenticity:** the source is cryptographically bound to an independently trusted key and the exact canonical payload/revision.
3. **Operational authorization:** the conformed, authentic, fresh evidence supports the specific production decision and supply-chain artifact.

A pass on conformance does not prove authenticity; a valid signature does not prove freshness or operational readiness; and an operational readiness claim does not prove the image digest or report is bound to the exact source revision. The release gate must not collapse these into a single `ok` flag.

## CI evidence

The latest inspected Control Plane workflow run was run #426 (ID `40436939846`), concluded failure. Its primary verification job failed and the downstream Docker/container-scan/policy/registry/Cosign job was skipped. The available job record did not expose step-level conclusions, so the root cause remains unclassified. This is a failed release gate, not proof of a particular code defect.

## Required resolution

1. Choose and version one canonical contract: runtime mode, required fields, gate namespace/semantics, timestamp rules, schema URI, canonicalization, signature algorithm, key ID/pinning/rotation, and endpoint/redirect policy.
2. Make producer and consumer fixtures derive from that same contract definition; add cross-repository positive and negative contract tests.
3. Keep source-authenticity verification independent from schema validation and freshness.
4. Make the root aggregate test command execute authorization, evidence-console, runtime-manifest, supply-chain, and platform suites.
5. Reconcile PR #29 and #31 by diff and shared entry-point audit; do not merge them independently.
6. Re-run CI on the exact consolidated commit and obtain actionable logs for each failed step.
7. Verify the live signed status and schema from the deployed producer, with independently pinned public key and exact revision-bound supply-chain report, before release.

## Great Scale mapping

For the Great Scale invariant
`S = M ∧ R ∧ E ∧ P ∧ A ∧ F ∧ C ∧ L`:

- **M (manifest/contract): HOLD** — two candidates disagree on contract fields and semantics.
- **R (reachability): UNKNOWN** — a workflow run exists, but its step-level execution evidence is incomplete.
- **E (execution): FAIL/HOLD** — latest observed CI conclusion is failure; root cause is not established.
- **P (provenance/authenticity): HOLD** — PR #29 proposes signature binding; deployed producer/key pinning has not been verified.
- **A (authorization): PARTIAL/HOLD** — force bypass is removed in the candidate logic, but consolidated entry-point proof is pending.
- **F (freshness): CANDIDATE ONLY** — source-issued timestamps are checked in proposed code; live producer behavior is unverified.
- **C (completeness): HOLD** — PR #31's test script omits PR #29's authorization and runtime-contract test files.
- **L (live contract): UNKNOWN/HOLD** — production status/schema pair has not been verified from the live deployment.

Overall: `S = false` on available evidence. Procurement remains HOLD; production release remains NO-GO. These are evidence-state conclusions, not a claim that the system is permanently broken.
