# Descent CLIV — Workflow identity must include immutable action dependencies

## Finding

CLIII bound a successful result to a snapshot at the merge boundary. The next hidden assumption is that the workflow executed at that snapshot has a reproducible definition. A workflow file SHA alone does not freeze the code fetched by steps such as `uses: actions/checkout@v4`: the `v4` tag is a movable reference. Thus two executions with the same repository workflow blob can resolve a dependency name to different action commits over time.

This is a supply-chain identity gap, not evidence that either action is malicious or that the current workflow has been compromised.

## Formal contract

Let workflow identity be:

\[
W=(w, A_1, A_2, \ldots, A_n)
\]

where (w) is the workflow-file blob identity and each (A_i=(repository_i, ref_i, resolvedSHA_i)) is an action dependency. Reproducible verification requires each dependency's resolved SHA to be explicit and recorded. A strict policy is:

\[
\operatorname{Immutable}(W)=\bigwedge_{i=1}^{n}
\operatorname{SHA40}(ref_i)
\]

A mutable tag may be convenient, but it is a name, not an immutable dependency identity. The stronger evidence tuple therefore includes the workflow blob and action dependency SHAs, in addition to the tested candidate, run ID, and conclusion.

## Repository observation

The current Great Scale workflow references `actions/checkout@v4` and `actions/setup-node@v4`. These are mutable major-version tags, not 40-character commit pins. The workflow also has no reported PR-triggered GitHub Actions run for observed head `06dc8f20c5b013eef78473fdcec2b3fc31a95fe5`; the combined status currently shows Vercel and CodeRabbit successes, which do not establish that the declared GitHub Actions test job passed.

## Regression model

Added `test_great_scale_cliv_action_pin_contract.py`. It verifies that a strict reference classifier accepts full 40-character lowercase commit SHAs and rejects tags, branches, malformed hashes, and uppercase lookalikes. This is a contract unit test; it does not yet parse/enforce the repository workflow itself or verify an action SHA against upstream.

## Great Scale mapping

- **State:** workflow blob plus resolved action dependency commits.
- **Observation:** hosted run ID, tested candidate SHA, and conclusion.
- **Invariant:** identical workflow-file bytes do not imply identical execution if dependencies resolve through movable refs.
- **Test obligation:** enforce and record immutable action pins, then run the aggregate suite against the exact candidate.
- **Operational consequence:** until action refs are pinned or resolved dependency SHAs are captured, call the workflow identity partially specified rather than fully reproducible.

## Verification boundary

The contract test is intended to be integrated into `npm run all`. No clean-checkout aggregate run, hosted GitHub Actions success on the current head, branch-protection inspection, merge, build, or deployment is claimed. The immediate follow-up is to pin each action to an upstream-verified full commit SHA, document the corresponding release, and enforce the policy against the actual workflow YAML.
