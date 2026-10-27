# Great Scale — Descent CLXXVI: make the last connection executable

## Finding

The remaining producer-consumer gap was not just missing evidence; it was missing an executable release gate that checks the real producer from the consumer's perspective. Unit tests can prove that a validator rejects stale timestamps, but cannot prove that the deployed status endpoint and independently fetched schema actually implement the contract.

The control-plane now has a dedicated live gate:

`npm run verify:evidence-console:live`

It passes only when the configured live endpoint returns a valid v5.4.0 status/schema contract, with `status=ok`, `authority=public`, and `trustContractVerified=true`. It sets a nonzero process exit code for any degraded, malformed, stale, or locally-authorized response. The command is documented in `docs/evidence-contract-v5.4.0.md` and is exposed by the canonical package scripts. Version comments were also aligned from v5.3.1 to v5.4.0.

## Exact candidate

Control Plane PR #31:
- Latest inspected head: `2893c28830a5eaf43a20c08c83a965bdeddc178c`
- [PR #31](https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/31)
- New gate: `status/verify-public-evidence-console.mjs`
- Script: `verify:evidence-console:live`
- Contract documentation: `docs/evidence-contract-v5.4.0.md`

The code was re-fetched at the latest head. The package script exists, the release gate checks all three conditions, the script sets failure exit status when not accepted, and the stale v5.3.1 comments were removed from the two inspected files.

## Formal acceptance

Let (L) be the result of a live probe. The new release gate enforces:

[
\operatorname{LiveContractPass}(L)=
(L.status=\texttt{ok})
\land(L.authority=\texttt{public})
\land(L.trustContractVerified=\texttt{true})
]

The broader procurement acceptance remains:

[
\operatorname{ProcurementReady}=
\operatorname{CoreReady}
\land\operatorname{EvidenceAuthorized}
\land\operatorname{SupplyChainEvidenceAuthorized}
\land\operatorname{LiveContractPass}
\land\operatorname{RevisionBoundPassingCI}
]

This gate closes a missing executable check, but it does not prove the producer's authenticity or completeness. Fresh timestamps are not signatures; the public payload and schema are still not cryptographically authenticated by this new script. The producer may also need a live observation loop rather than timestamps frozen into a static build.

## Test and deployment status

The code has been committed and fetched back for source-level verification. The live gate itself was **not executed successfully** in this environment: attempts to retrieve the public production endpoints returned `SOURCE_NOT_AVAILABLE` / inaccessible results, which are not proof of endpoint outage. The latest candidate has no completed Actions run returned yet; Snyk is pending and Vercel reports a build-rate-limit failure. No full repository test pass can be claimed.

## Great Scale decision

[
\boxed{\text{HOLD}}
]

The last missing *consumer-side check* now exists as executable code. The last missing *runtime evidence* is still open. Run `npm run verify:evidence-console:live` from a trusted checkout with the production URL configured, run the complete canonical suite, and obtain a passing hosted CI result bound to the exact reviewed head. Separately verify source identity/signature and evidence completeness before enabling consequential procurement decisions.
