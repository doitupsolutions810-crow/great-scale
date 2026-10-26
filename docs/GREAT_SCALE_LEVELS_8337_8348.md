# Great Scale — Levels 8337–8348: a log link must identify the evidence it claims to support

## Finding

The promotion gate required a nonempty HTTPS GitHub-looking job-log URL, but its regular expression only checked that the string contained a path resembling `/actions/runs/<something>/job/<something>`. It did not bind the path's repository, run ID, or job ID to the candidate and platform records in the same evidence envelope.

That means a structurally valid evidence bundle could point reviewers to a different repository's job, or to another run/job in the same repository, while the remaining fields referred to the candidate under review. This is a **referential-integrity gap** in the evidence graph. It does not demonstrate a malicious deployment or a live exploit; the gate still depends on an authenticated collector and returns review eligibility only.

## Integration

Updated `promotion_gate.js` to validate the job-log URL with the URL parser and require all of the following:

- HTTPS and the exact `github.com` hostname.
- No URL username/password, port, query string, or fragment.
- Repository path equal to the candidate's exact `owner/repository`.
- Run path segment equal to the evidence envelope's positive workflow run ID.
- Job path segment equal to the evidence envelope's positive job ID.
- Candidate repository names must use a strict `owner/repository` form.

Added regression cases to `test_promotion_gate.js` for a mismatched run ID, mismatched job ID, mismatched repository, lookalike host, query decoration, and URL user information. The existing valid fixture continues to use the exact repository/run/job path.

## Mathematics

Let the evidence envelope contain candidate repository (P), workflow run (R), job (J), and log URL (U). URL syntax validity alone is:

[
\operatorname{LooksLikeLogURL}(U).
]

The stronger referential-integrity condition is:

[
\operatorname{BoundLogURL}(U,P,R,J)
= (\operatorname{scheme}(U)=\mathrm{https})
\land (\operatorname{host}(U)=\texttt{github.com})
\land (\operatorname{path}(U)=
\texttt{/}P\texttt{/actions/runs/}R\texttt{/job/}J).
]

The required implication is:

[
\operatorname{Eligible}(P,R,J,\ldots)
\Rightarrow \operatorname{BoundLogURL}(U,P,R,J).
]

A syntactically valid link that points elsewhere does not satisfy the evidence claim. This is the same general distinction as referential integrity in a database: a well-formed foreign key is insufficient unless it resolves to the intended record.

## Great Scale mapping

| Level | Mathematics | Science / engineering interpretation | Status |
|---|---|---|---|
| 8337 | Separate URL syntax from URL-to-record identity. | A plausible link is not proof that the linked record belongs to this claim. | Gap identified by source inspection. |
| 8338 | Require `path(U)=path(P,R,J)`. | Repository, run, and job identities must agree across the evidence graph. | Guard integrated. |
| 8339 | Require HTTPS, exact host, and no credentials, port, query, or fragment. | Prevent lookalike hosts and URL decorations from obscuring the target. | Guard integrated. |
| 8340 | Validate `owner/repository` before constructing the expected path. | Avoid ambiguous path composition from malformed repository identifiers. | Guard integrated. |
| 8341–8344 | Mutate one identity edge at a time and require rejection. | Run, job, and repository substitutions must fail closed. | Regression cases added to source. |
| 8345–8346 | Reject lookalike hosts and decorated URLs. | Authority and target must be explicit, not inferred from a substring. | Regression cases added to source. |
| 8347 | `URLValid` does not imply `EvidenceAuthentic`. | Exact binding improves consistency but cannot authenticate the collector or log contents. | Trust boundary unchanged and documented. |
| 8348 | Promotion remains a conjunction over independently checked evidence edges. | Any unresolved provenance edge blocks review eligibility. | New guard is source-integrated; repository test execution remains unverified. |

## Test / verify / run / build

- Source changes committed to `research/kernel-hardening-4401-4500`.
- The new named regression cases are present in `test_promotion_gate.js`, and that file remains included in `npm test`.
- The available GitHub connector returned **no workflow run** for the exact new test commit `8024f35b8f4051b4cdfeb81bb369085dcdd62ded`.
- The previously inspected exact-head run `39779783800` failed with `runner_id=0`, empty runner name, no steps/logs, and no artifact. That failure is a runner-start failure signature, not proof of a test assertion failure.
- The container can execute Node.js, but it cannot resolve `github.com`, so it cannot clone the current branch. The newly committed repository test file, full `npm test`, `python3 test_descent.py`, and build have **not** been executed here.
- Branch divergence was already substantial before this patch (180 commits ahead / 97 behind `main`); reconcile before promotion. Keep PR #89 draft and unmerged until exact-head hosted execution produces inspectable logs and a same-run receipt.

## Profound finding

**Evidence is not only a set of true-looking fields; it is a graph of references that must resolve to the same underlying event.** A green status, a valid receipt, and a well-formed log URL can each be individually plausible yet jointly misleading if the link points to a different run or job. Assurance requires both value checks and referential checks, followed by authenticated collection and real execution evidence.

This is a software-assurance result. It does not establish a new physical law or empirical claim about quantum geometry.
