# Great Scale — Levels 7601–7700: phase-domain and runtime parity

## Profound finding

The public phase-time function did not preserve one canonical phase domain across runtimes. JavaScript's remainder operator keeps the sign of a negative dividend, so the ES module/CommonJS implementation used

\[
\theta(t,r)=(tr)\bmod 1
\]

and returned a negative phase for negative time (for example, \(t=-1,r=0.85\) gives phase \(-0.85\)). Python's modulo operator returns a non-negative remainder for the same inputs, giving phase \(0.15\). The derived cosine-based geometry is periodic, but the exposed `phase` field disagreed across runtimes and violated the natural canonical phase domain \([0,1)\).

A second boundary failure was unchecked non-finite input: `stateAt(NaN)`, `stateAt(Infinity)`, or an overflowed product \(tr\) could propagate NaN into phase, heat, and \(\Psi\). A mathematical invariant is not operationally established when the public API emits undefined numerical state.

## Contract repair

Define a finite phase-time input domain and canonical phase:

\[
c=tr,\qquad
\operatorname{phase}(t,r)=\operatorname{mod}_1(c)
= ((c\bmod 1)+1)\bmod 1.
\]

The implementation rejects non-finite \(t\), non-finite \(r\), and a non-finite product \(tr\), then canonicalizes the phase in ES module, CommonJS, and Python reference code.

For every accepted input, \(\operatorname{phase}(t,r)\in[0,1)\). Since \(h=\tfrac12-\tfrac12\cos(2\pi\operatorname{phase})\), we have \(h\in[0,1]\). Therefore

\[
S=h(1-h)=\tfrac14-(h-\tfrac12)^2\in[0,\tfrac14],
\qquad
\Psi=\mathrm{CONE}+S\ge\mathrm{CONE}.
\]

This is a numerical-domain guarantee for the implementation, not evidence for a physical or quantum interpretation of the model.

## Great Scale mapping

**Level 7601 — Canonical phase.** Every accepted phase is represented in \([0,1)\), including negative time inputs.

**Level 7602 — Cross-runtime equivalence.** ES module, CommonJS, and Python use the same modulo-one convention.

**Level 7603 — Finite numerical domain.** Non-finite time/rate and overflowed phase products are rejected before they contaminate derived state.

**Level 7604 — Invariant propagation.** Canonical phase implies \(h\in[0,1]\), which implies \(S\in[0,1/4]\) and \(\Psi\ge\mathrm{CONE}\).

**Level 7605 — Boundary regression.** Tests cover negative phase, periodic equivalence, NaN, infinities, and multiplication overflow.

**Level 7606 — Verification reachability.** Repository CI must run on stacked research pull requests as well as PRs targeting `main`; otherwise changes built atop a draft research branch can miss the repository's own test workflow.

## CI integration finding

The workflow previously restricted `pull_request` events to base branch `main`. This branch is intentionally stacked on `research/descent-step-domain-contract`, so that filter excludes it. The workflow trigger is broadened to all pull requests, while push-triggered CI remains restricted to `main`. This makes the repository's declared tests eligible to run for draft research PRs too.

## Verification boundary

The source and regression tests are committed to the draft branch. Targeted formula checks are not the same as executing the committed `npm run all` suite. Hosted CI and deployment must be reported from their actual run results; absence of a workflow run is not a passing test.
