# Descent CLV — Workflow Identity Must Bind to Executed Dependencies

## Finding

The previous action-pin test only tested sample strings. It did not inspect the actual CI workflow. Therefore it could pass while `.github/workflows/ci.yml` still used mutable references such as `actions/checkout@v4` and `actions/setup-node@v4`.

This is a verification reachability gap: a test of the policy predicate is not evidence that the real workflow satisfies the policy.

## Change integrated

The CI workflow now pins checkout and setup-node to full commit SHAs, and the action-pin regression parses the actual workflow's `uses:` references and rejects any reference that is not a full lowercase 40-character SHA.

Pinned references:
- `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683` (verified commit exists in actions/checkout)
- `actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020` (verified commit exists in actions/setup-node)

The test uses a simple YAML-line regex, not a full YAML parser. It is adequate for the current simple workflow shape but should be upgraded if the workflow introduces aliases, reusable workflows, or more complex syntax.

## Formal model

Let (D) be the set of action dependencies actually referenced by the workflow and (P(d)) be the predicate that dependency (d) is pinned to an immutable commit SHA.

A sample-only test establishes at most:

`P(d_example)`

The real workflow invariant is:

`forall d in D, P(d)`

Therefore the regression must extract (D) from the checked-in workflow and validate every member, rather than merely passing example strings to the predicate.

## Great Scale mapping

- **State:** exact workflow blob/revision.
- **Dependency set:** all action `uses:` references in the workflow.
- **Invariant:** every external action reference resolves to a full immutable commit SHA.
- **Evidence:** test reads the actual workflow file and enumerates all references.
- **Invalidation:** a workflow change is rechecked by the canonical suite.

## Verification status

Both action SHAs were confirmed to exist as commits in their respective official repositories. The workflow and test changes were committed to the research branch. A clean-checkout run of `npm run all`, hosted CI, and build/deployment verification are still outstanding. Pinning action references improves reproducibility but does not by itself guarantee the actions are secure; review the pinned code and update deliberately when security fixes are released.
