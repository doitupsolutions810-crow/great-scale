# Great Scale XC — Observability Limits, Indistinguishable Worlds, and the Limits of Detection

## Descent question

LXXXIX asks whether historical evidence transfers to the current environment. XC asks whether the change can be detected at all from the measurements available. A detector cannot reliably distinguish underlying states that induce the same observation distribution.

## Formal model

Let the hidden system state be \(Z\), observations be \(X=h(Z)\), and the pre-change and post-change observation distributions be \(P_0\) and \(P_1\). If \(P_0=P_1\), every detector based only on these observations has the same output distribution in both worlds. A detector with false-positive probability at most \(\alpha\) therefore has power at most \(\alpha\) against this observationally indistinguishable alternative.

More generally, for total variation distance

\[
d_{\mathrm{TV}}(P_0,P_1)=\sup_A|P_0(A)-P_1(A)|,
\]

any detector rejection event \(A\) satisfies

\[
|P_1(A)-P_0(A)|\le d_{\mathrm{TV}}(P_0,P_1).
\]

If false-positive probability is at most \(\alpha\), detector power obeys

\[
\boxed{\operatorname{Power}\le\min\{1,\alpha+d_{\mathrm{TV}}(P_0,P_1)\}.}
\]

This is an upper bound, not a power guarantee. If a defensible upper bound on TV is \(\delta\), then power is at most \(\min(1,\alpha+\delta)\). When that upper bound is below a required power, the requirement cannot be achieved by the stated detector and observation channel under those assumptions.

## Worked example

Suppose a detector's false-positive rate is controlled at \(\alpha=0.05\), and the two observation distributions have TV distance zero. Then

\[
\operatorname{Power}\le0.05.
\]

It has no information to distinguish the changed world from the baseline; its chance of flagging the change is no better than its baseline flagging rate. If TV is bounded above by 0.10, power is at most 0.15. These are theoretical bounds, not measured detector performance.

## Operational consequence

1. List what is observed and what remains latent.
2. For each important failure mode, identify an observable that would change under that failure.
3. If no existing observable separates the relevant states, add measurements: outcome labels, correctness checks, independent sensors, audits, or controlled probes.
4. Record “not observable with current measurements” separately from “no shift detected.”
5. Do not claim high detection power unless supported by a validated detector and representative testing.
6. Revisit the observability map when system architecture, adversary behavior, or operating conditions change.

## Pinned finding

**Absence of a signal is evidence of absence only when the observation channel has enough power to reveal the event.** If relevant worlds are observationally indistinguishable, better thresholds cannot solve the problem; the measurement design must change.

## Scientific limits

The total-variation bound is exact under its definitions, but useful numerical bounds on TV may be difficult to establish in high dimensions. Detector power also depends on the actual test, sample size, data dependence, and alternatives considered. This rung is a mathematical design result, not empirical validation of any deployed monitor.
