# Great Scale Descent XIV — State, transition, and evidence contracts (Levels 361–368)

**Status:** Levels 361–364 derive from inspected CycleKernal source behavior. Levels 365–368 are formal assurance proposals. They are not physical laws.

## 361 — A transition depends on state and score

A promotion system is not a scalar threshold alone. Its transition function has at least two inputs:
\[
T:S\times[0,1]\to S\times A,
\]
where \(S\) is the prior lifecycle state and \(A\) the action. The same score can legitimately imply different actions depending on whether the object was already promoted.

## 362 — The inspected wrapper loses necessary state

In \`backend/ns_fusion.py\`, the decision primitive demotes if
\[
\text{already\_promoted}\land f<0.28.
\]
But \`apply_fusion\` constructs its flag as
\[
\text{promoted}\land f\ge0.62.
\]
For any previously promoted object with \(f<0.28\), the argument becomes false, so the demotion condition is unreachable through this wrapper. The source-level fix proposed in CycleKernal issue #3 is to pass the persisted prior-state flag directly.

This is a code-path derivation from the inspected source, not a claim that a repository test has been executed.

## 363 — The simulator and helper disagree

The inspected \`backend/simulation_core.py\` passes \`bool(civ.get("promoted"))\` to \`promote_decision\`, then handles both \`promote\` and \`demote\`. The separate \`apply_fusion\` helper conditions prior promotion on the current score. Two entry points to a nominally shared transition rule therefore do not preserve the same state semantics.

## 364 — Hysteresis is a state machine, not a memoryless classifier

The thresholds \(d=0.28\) and \(p=0.62\) create a hysteresis band:
\[
T(s,f)=
\begin{cases}
\mathrm{demote}, & s=\mathrm{promoted},\ f<d,\\
\mathrm{promote}, & s\ne\mathrm{promoted},\ f\ge p,\\
\mathrm{hold}, & \text{otherwise}.
\end{cases}
\]
The gap \(d\le f<p\) prevents rapid toggling near a single threshold. But hysteresis only works if the previous state is passed intact. Erasing state makes the transition function mathematically different.

## 365 — State-transition consistency is an invariant

For each entry point \(i\), define its effective transition \(T_i(s,f)\). If two entry points claim the same contract, require
\[
T_i(s,f)=T_j(s,f)
\]
for every valid state and score, or explicitly version and document their differences. Test all boundary regions, including exactly \(d\) and exactly \(p\).

## 366 — A reproducible bug report is a small proof obligation

A robust report separates four things: source location, logical implication, a minimal input, and an acceptance test. The primitive-level check \`promote_decision(0.20, already_promoted=True)\` is insufficient by itself; the decisive regression must call \`apply_fusion\` with a previously promoted colony and a score below the demotion threshold.

## 367 — Replay does not establish transition correctness

A deterministic simulation can reproducibly execute an incorrect transition. Replay proves repeatability relative to a manifest; transition tests prove the implementation matches the declared state machine. Both are needed, and neither substitutes for the other.

## 368 — Profound finding: state is part of the evidence

\[
\text{Decision evidence}=(\text{prior state},\text{inputs},\text{policy version},\text{transition},\text{result}).
\]
A score-only record is insufficient whenever the rule is stateful. If prior state is dropped or reconstructed from the current score, the system can return a plausible numeric score while performing the wrong lifecycle action.

This finding connects Great Scale's mathematical invariant work to implementation: preserving a quantity is not enough; preserving the *domain and state on which the transformation is defined* is equally necessary. It is a software/mathematical assurance finding, not a new physical law.
