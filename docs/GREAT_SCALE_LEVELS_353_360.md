# Great Scale Descent XIII — Exactness, verification scope, and boundary honesty (Levels 353–360)

**Status:** Levels 353–356 are mathematical/implementation audit findings about the current scalar certificate. Levels 357–360 are proposed assurance principles. They are not physical laws.

## 353 — Exact arithmetic can be undermined before arithmetic begins

The helper uses Fraction, but its original input validator first converted every input to float to check finiteness. That conversion can overflow for a finite, very large integer or rational before exact arithmetic starts. Thus an exact arithmetic core does not guarantee an exact input path.

**Change in this candidate:** _fraction now checks IEEE finiteness only for actual float inputs and parses integers, strings, and Fraction values directly into rational form. This preserves the stated decimal-string/exact-rational contract without an unnecessary floating-point bottleneck.

## 354 — Domain restriction is part of the theorem

The certified set is not the raw uncertainty rectangle. It is the intersection
\[
B_{\mathrm{adm}}=
([p-\epsilon_p,p+\epsilon_p]\times[v-\epsilon_v,v+\epsilon_v])
\cap([0,1]\times[0,\infty)).
\]
The result means something only relative to this declared admissible set. Changing the domain changes the quantified proposition and can change the certificate.

## 355 — Why the two margins are sound for this constraint

For \(g(p,v)=p(1-p)-v\), concavity of \(p(1-p)\) gives the minimum over a closed interval at an endpoint. Its maximum is \(1/4\) if the interval contains \(1/2\), otherwise it is attained at an endpoint. Therefore
\[
g_{\min}=\min_{p\in[p_-,p_+]}p(1-p)-v_+,
\quad
g_{\max}=\max_{p\in[p_-,p_+]}p(1-p)-v_-.
\]
So \(g_{\min}\geq0\) proves every admissible point feasible, while \(g_{\max}<0\) proves every admissible point infeasible. Equality on the upper margin is not enough to call the entire box infeasible; the correct outcome is unresolved unless the lower-margin condition independently certifies feasibility.

## 356 — Regression target: exactness of the entire path

A regression should not merely check the final classification. It should test the input boundary, clipped domain, extremum location, equality behavior, and arithmetic representation. The candidate adds a case with an exact uncertainty bound \(10^{400}\), which is finite as a rational and clips the probability interval to \([0,1]\); it also asserts that infinite floating-point inputs remain rejected.

The isolated check passed the six existing classification scenarios plus the large-rational and infinity/NaN checks. This was a focused isolated regression, not the full repository suite; hosted execution remains blocked by the runner failure described in the PR.

## 357 — A certificate is a theorem with a scope

A certificate is not simply a label such as “pass.” It is a compact claim:
\[
\mathcal{M},\mathcal{D},\mathcal{A}\vdash P,
\]
where \(\mathcal{M}\) is the mathematical model, \(\mathcal{D}\) the domain, \(\mathcal{A}\) the assumptions, and \(P\) the certified proposition. Removing the model, domain, or assumptions from the receipt weakens the meaning of the result.

## 358 — Soundness and completeness are different obligations

A sound certificate never declares a false proposition under its model. A complete classifier would decide every possible input. The three-way classifier deliberately permits unresolved; this is not a defect. It preserves soundness when the available bounds cannot decide the claim. Do not optimize away “unresolved” merely to obtain more green results.

## 359 — Independent verification must be genuinely independent

Re-running the same code twice checks repeatability, not independence. A stronger audit compares distinct routes: a derivation of extrema, exact-rational edge cases, a separately implemented reference calculation, and regression tests against the production helper. These checks have different failure modes, though none alone proves the whole software system correct.

## 360 — Profound finding: exactness is an end-to-end property

\[
\operatorname{ExactResult}
\Rightarrow
\operatorname{ExactRepresentation}
\land\operatorname{ValidDomain}
\land\operatorname{SoundDerivation}
\land\operatorname{CorrectImplementation}.
\]
Exact arithmetic only at the center of a pipeline is insufficient if parsing, coercion, domain clipping, or claim interpretation changes the problem before or after the calculation.

For Great Scale, this means the certificate must preserve its full chain: input representation → admissible domain → extrema derivation → three-valued result → commit-bound test evidence. The finding is a formal assurance principle, not a physical discovery. The separate existing \(\Psi=\mathrm{CONE}+S\) convention remains unchanged.
