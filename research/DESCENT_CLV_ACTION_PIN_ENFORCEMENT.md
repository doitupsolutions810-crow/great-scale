# Descent CLV — Turn the action-pin rule into an enforced invariant

## Finding

CLIV introduced a classifier for immutable action references, but a classifier test alone does not protect the real workflow. If the test never reads `.github/workflows/ci.yml`, mutable references can remain in production configuration while the model test stays green.

CLV closes that reachability gap: the regression test parses each `uses: repository@ref` line in the actual CI workflow and rejects any ref that is not a full 40-character lowercase commit SHA. It also has positive and negative fixtures so the policy itself is exercised.

## Formal contract

Let (U(W)) be the set of action references parsed from workflow (W). Let (SHA_{40}(r)) mean that (r) is exactly 40 lowercase hexadecimal characters.

\[
\operatorname{Pinned}(W)=\forall (a,r)\in U(W),\; SHA_{40}(r)
\]

The build must enforce:

\[
\operatorname{CIAllowed}(W)=\operatorname{Pinned}(W)
\]

This is a syntactic immutability gate. It does not, by itself, establish that a SHA belongs to the intended upstream release; provenance and version-to-SHA review remain separate obligations.

## Integration

- Added `test_great_scale_clv_action_pin_enforcement.py`.
- Wired it into the canonical `npm run all` command.
- Pinned the CI workflow's checkout and setup-node actions to full commit SHAs, with intended upstream release identities recorded in the workflow comments.

## Test and verification boundaries

The regression has two obligations: a fixture with full SHA references passes; a fixture with a mutable tag fails; and the real workflow is scanned for unpinned action references. Run the exact script with:

```sh
python3 test_great_scale_clv_action_pin_enforcement.py
npm run all
```

A local script pass is not a hosted CI pass. A successful aggregate command, exact hosted run on the PR candidate, and branch-protection enforcement must still be observed before claiming merge readiness. This check does not query GitHub branch protection or attest upstream action provenance.
