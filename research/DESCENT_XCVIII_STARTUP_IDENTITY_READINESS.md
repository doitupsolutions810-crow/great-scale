# Descent XCVIII — Startup Identity Readiness and Non-Invertible Trust

## Finding

A fail-closed signing-key loader does not guarantee a fail-closed service. The production entrypoint must force the loader before readiness, and startup must not swallow validation errors. A service can have a correct local guard that is never invoked on the path that accepts work.

This is an engineering invariant and threat-model result, not an empirical claim that any deployed instance was exposed.

## Contract

Let:

- \(R\): the service is ready to accept production requests;
- \(K\): a stable, provisioned signing key is present and valid;
- \(P\): the effective authorization policy is valid and explicit;
- \(A\): the workload identity is attested by the expected identity source.

The intended contract is:

\[
R \Rightarrow K \land P \land A
\]

Equivalently, any missing prerequisite must force \(R=0\):

\[
\neg K \lor \neg P \lor \neg A \Rightarrow \neg R
\]

For signing-key continuity, absent an explicit, authorized rotation event:

\[
K_{t+1}=K_t
\]

A missing key is not a rotation instruction. Automatically generating a replacement silently changes the authority identity.

## Why this is a Great Scale finding

Great Scale repeatedly studies what information a scalar projection preserves and what it destroys. The same structure applies to trust evidence.

Let a complete authorization witness be:

\[
W=(K,\ issuer,\ audience,\ rights,\ method,\ policyVersion,\ evidenceID)
\]

A projection \(\pi(W)\) that drops fields is generally non-injective. There can exist \(W_1\ne W_2\) with \(\pi(W_1)=\pi(W_2)\). Once a method, policy version, or identity source is omitted from the signed or recorded witness, a downstream verifier cannot reconstruct it from the projection.

Therefore, the proof obligation is not merely “the signature verifies.” It is:

\[
\text{Verified}(W) \land \text{PolicyAdmits}(W) \land \text{IdentityAttested}(W)
\]

and the same structured action identity must survive authorization, execution, receipt signing, and evidence recording.

This connects three existing boundaries without conflating them:
1. Great Scale: non-injective scalarization and witness preservation.
2. Capability Authority: production key loading, exact rights/method checks, workload identity, signed receipts.
3. Living Intermediate Control Plane: request routing and startup guards must run before sensitive operations.

## Executable contract model

`test_startup_identity_invariant.py` enumerates all 16 Boolean combinations of key validity, policy validity, workload attestation, and production mode. In production, readiness is true if and only if all three prerequisites are true. In non-production mode, the model allows lab readiness, while making no claim that it is production-safe.

This is a finite state-space contract test, not proof that every repository entrypoint currently satisfies the contract. Integration tests must additionally demonstrate that the actual startup path invokes each validator and terminates before binding the listener on failure.

## Verification boundary

- Model-level exhaustive check: 16 combinations.
- Repository test suite / hosted Actions: not verified by this note.
- No live deployment, key store, SPIRE workload API, network exposure, or runtime listener was inspected.
- The companion Capability Authority change is tracked in [PR #9](https://github.com/doitupsolutions810-crow/capability-authority/pull/9), stacked on [PR #8](https://github.com/doitupsolutions810-crow/capability-authority/pull/8). Both remain unmerged at time of writing.

## Operational acceptance criteria

1. Missing or unsafe production key → startup exits non-zero before listener bind.
2. Invalid or absent production rights allowlist → startup exits non-zero.
3. Workload identity source is not the required attested source → startup exits non-zero.
4. A signed receipt carries the same structured action tuple that passed authorization.
5. Tests record the exact tested commit SHA, command, exit code, and actual executed steps.
6. An empty/absent CI job log is classified as **unverified**, never as pass or code-level failure.

## Conclusion

The deeper invariant is **readiness is a theorem with prerequisites, not a process state inferred from successful imports**. The system should only advertise production readiness after identity, policy, and attestation preconditions have been actively checked. The Great Scale analogy is precise at the level of information preservation and contract logic; it is not a claim that software trust invariants are physical laws.
