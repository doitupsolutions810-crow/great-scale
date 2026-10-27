# Descent CLXVI — A local policy gate is not a merge gate

## Finding

The Great Scale policy model correctly says that an unverified or disabled server-side policy blocks promotion. The new live check closes the evidence gap left by the earlier model-only descents: the GitHub branch-protection API reports **“Branch not protected”** for every inspected default and active integration target branch, and the repository rulesets API returns an empty list for all four repositories.

Therefore, required CI checks are not currently enforced at these merge targets. A passing local test, a failed hosted run, or a source-level `PolicyState` predicate can describe evidence, but it does not force GitHub to reject an unapproved merge. GitHub’s documentation distinguishes this explicitly: when required status checks are disabled, the branch has no merge restrictions; an active branch-protection rule or ruleset is what makes selected checks mandatory.[1] [2]

## Live observations

On 2026-10-26, the authenticated GitHub CLI returned `404 Branch not protected` for the Great Scale PR #128 base `research/descent-civ-effect-evidence-boundary`; the Great Scale default branch `main` is also unprotected. The repository rulesets endpoint, including parent rulesets, returned `[]`.

The same branch-protection response and empty-ruleset result were observed for Living Intermediate Control Plane `main`, Capability Authority `main` and `integration/evidence-chain-and-index`, and CycleKernal `main` and `feature/gs-lvi-closed-loop-evidence`. The branch targets, not only repository defaults, were checked because the active integration branch may be different from `main`.

This explains an important operational distinction in current PR state. LICP PR #27 is open, non-draft, and reported mergeable even though its `Plane CI` run failed with zero steps. With no protection rule or applicable ruleset requiring that check, the failure is visible status, not a server-side merge veto. Great Scale PR #128 has separate current blockers (draft/conflicting/stale merge metadata), but its base branch also has no required-check protection. Those blockers should not be misattributed to a configured CI gate.

## Formal contract

For a target branch \(b\), define \(P(b)=1\) only when an active rule applies to \(b\) and the intended CI status is required for merging. Let \(C\) mean the tested candidate is current and bound to the intended base/head, and \(T\) mean the qualifying test workflow passed on that candidate.

\[
\operatorname{MayMerge}(b)=C\land T\land P(b).
\]

Equivalently, for binary gates:

\[
G_{\mathrm{merge}}=C\cdot T\cdot P(b),\qquad C,T,P(b)\in\{0,1\}.
\]

The live observations give \(P(b)=0\) for the inspected branches. Consequently \(G_{\mathrm{merge}}=0\) regardless of the local test result. If the settings query were unavailable or contradictory, policy state would be `UNKNOWN`, which also blocks the decision. A caller-supplied Boolean such as `server_enforced_authorization=true` cannot override a negative provider observation.

## Great Scale mapping

Keep the science state and governance state separate. The Great Scale scalar \(\Psi=\mathrm{CONE}+S\) describes its modeled state; it does not encode whether a test is current or whether the server prevents a failed change from merging. The verification record must remain a vector:

\[
V=(\Psi,\,C,\,T,\,P,\,R),
\]

where \(R\) identifies the applicable rule/ruleset and its required status checks. Accept only when \(C=T=P=1\) and \(R\) is authenticated and applies to the exact target ref. For the inspected repositories, \(P=0\); the appropriate classification is `NOT_ENFORCED`, not “verified.”

## Test and verification

The existing `test_great_scale_clix_server_policy_gate.py` already checks the core implication: `NOT_ENFORCED` or `UNKNOWN` blocks promotion even if CI passes. That regression is included in the canonical `npm run all` command. This descent adds the missing live API observation rather than duplicating that decision test.

The live branch-protection and ruleset queries are the verification of configuration state. They do not change settings. No build script exists in Great Scale. Enabling branch protections or rulesets would be a separate repository-administration action; it is intentionally not performed here because the required check names and bypass/review settings must be selected deliberately. In particular, several current hosted workflows failed before test steps or did not run on the current candidate, so enabling those checks immediately could block all merges without proving the intended checks are healthy.

## Next boundary

Before claiming merge-policy enforcement, choose an active ruleset for each intended integration target, require the actual CI check after verifying that it executes on the correct candidate, and decide whether stale bases, direct pushes, and bypasses are allowed. Then query the live configuration again and verify with a real PR that a missing required check is rejected by GitHub itself. No setting should be marked `ENFORCED` merely because the local Great Scale regression passes.

## References

[1]: https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches "About protected branches"
[2]: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets "Available rules for rulesets"
[3]: https://api.github.com/repos/doitupsolutions810-crow/great-scale/branches/research%2Fdescent-civ-effect-evidence-boundary/protection "Great Scale PR target branch protection endpoint"
[4]: https://api.github.com/repos/doitupsolutions810-crow/great-scale/rulesets?includes_parents=true "Great Scale repository rulesets"
[5]: https://api.github.com/repos/doitupsolutions810-crow/living-intermediate-control-plane/branches/main/protection "Living Intermediate Control Plane main branch protection endpoint"
[6]: https://api.github.com/repos/doitupsolutions810-crow/living-intermediate-control-plane/rulesets?includes_parents=true "Living Intermediate Control Plane repository rulesets"
[7]: https://api.github.com/repos/doitupsolutions810-crow/capability-authority/branches/integration%2Fevidence-chain-and-index/protection "Capability Authority integration branch protection endpoint"
[8]: https://api.github.com/repos/doitupsolutions810-crow/capability-authority/rulesets?includes_parents=true "Capability Authority repository rulesets"
[9]: https://api.github.com/repos/doitupsolutions810-crow/CycleKernal/branches/feature%2Fgs-lvi-closed-loop-evidence/protection "CycleKernal feature branch protection endpoint"
[10]: https://api.github.com/repos/doitupsolutions810-crow/CycleKernal/rulesets?includes_parents=true "CycleKernal repository rulesets"
[11]: https://github.com/doitupsolutions810-crow/living-intermediate-control-plane/pull/27 "Living Intermediate Control Plane PR 27"
