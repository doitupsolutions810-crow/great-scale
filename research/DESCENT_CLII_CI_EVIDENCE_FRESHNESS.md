# Descent CLI — Freshness is part of correctness

## Observation

A CI run can be authentic and successful for commit H1 against base B1 with workflow W1 and candidate M1, yet no longer justify accepting the current PR after its head, base, workflow, or tested candidate changes. Authenticity alone does not imply applicability to the present state.

## Contract

Let current state be S=(H,B,W,M) and run evidence be E=(H_r,B_r,W_r,M_r,R,C).

`Accept(S,E) = (H_r=H) AND (B_r=B) AND (W_r=W) AND (M_r=M)`
`             AND (R is present) AND (C=success)`

Any mutation to the state tuple invalidates the prior run for this acceptance decision. This is a conservative freshness contract; providers may define additional reusable-check semantics, but those semantics must be explicit and independently verified.

## Regression

`test_great_scale_cli_ci_freshness.py` accepts an exact matching snapshot and rejects stale evidence after changes to head, base, workflow, or candidate, as well as missing run ID and failed conclusion.

The test is an abstract contract test. It does not call GitHub APIs, authenticate run metadata, prove that a candidate was built from its asserted parents, or run the repository's full suite.

## Great Scale mapping

- **State:** immutable tuple (head, base, workflow, candidate).
- **Observation:** CI evidence binds to the tuple at run time.
- **Invalidation:** any relevant tuple change expires evidence for the new state.
- **Acceptance:** only a successful run with matching identifiers can satisfy the contract.
- **External trust:** tuple and run fields must be fetched from authoritative APIs; a model cannot make self-supplied fields authentic.

## Synthesis

Verification is not just a predicate over evidence. It is a predicate over evidence *and the exact state to which the evidence applies*. The robust unit is therefore not “green branch,” but “green run bound to an immutable candidate and current review snapshot.”

No full-suite run, hosted CI success, merge, build, deployment, or production verification is claimed.
