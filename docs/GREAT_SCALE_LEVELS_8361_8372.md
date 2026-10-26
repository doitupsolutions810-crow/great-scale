# Great Scale — Levels 8361–8372: Receipt Time Semantics

## Question

Does a parseable timestamp prove that a CI verification receipt is temporally plausible?

## Finding

No. A generic date parser accepts date strings without an explicit timezone, whose meaning depends on the runtime environment. It can also parse a timestamp set in the future. These conditions weaken the interpretation of a receipt's `created_utc` field.

## Integrated policy

- Require an explicit UTC ISO-8601 timestamp ending in `Z`, with seconds and at most millisecond fractional precision.
- Reject receipts dated more than five minutes into the future, allowing a bounded operational clock-skew window.
- Update the valid fixture to use the current UTC time and add regressions for timezone-less and future-dated receipts.

This validates temporal representation and plausibility; it does **not** prove that the receipt was genuinely generated at that time. Trust in creation time still depends on authenticated platform evidence and the runner's clock.

## Great Scale table

| Level | Mathematics | Science / engineering | Status |
|---|---|---|---|
| 8361 | Require (t\in\text{UTC ISO-8601}). | Timestamps must have unambiguous timezone semantics. | Guard integrated. |
| 8362 | Require (t\le t_{now}+\delta), with \(\delta=300\text{ s}\). | Future-dated evidence beyond bounded clock skew is rejected. | Guard integrated. |
| 8363–8366 | Parseability is necessary but not sufficient for temporal plausibility. | A valid string can still describe an impossible or untrusted time. | Regression cases added. |
| 8367–8370 | Authenticity is not implied by timestamp syntax. | The gate must not confuse format validation with trusted time. | Limitation documented. |
| 8371–8372 | Eligibility remains a conjunction of provenance constraints. | Temporal validity complements, but cannot replace, run/commit/runner binding. | Full suites unverified. |

## Verification boundary

Source and test edits were written to the active research branch. The repository test suites and build were not run in this environment; no runtime pass is claimed. The CI runner issue and branch divergence remain open. PR #89 stays draft and unmerged.

## Profound finding

Time is another typed provenance edge. A timestamp is not simply a number or string; it is a claim about when evidence was produced, with timezone, precision, clock-skew and authenticity assumptions. Great Scale should expose each assumption rather than collapsing them into a single “valid” flag.
