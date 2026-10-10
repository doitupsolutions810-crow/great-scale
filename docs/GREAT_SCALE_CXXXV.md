# Great Scale CXXXV — Robust Bounds Under Membership Reclassification

## Question
How much inferential precision survives when stratum membership itself is uncertain,
so that admissible classifications change stratum observed sums and missing counts?

## Model
Let \(\mathcal C\) be a finite, explicitly justified set of admissible classification
scenarios. Scenario \(c\) has strata \(h=1,\ldots,H\), observed sum \(S_{ch}\),
missing count \(m_{ch}\), and valid support \([L_{ch},U_{ch}]\). For population size
\(G\), its conditional interval is

\[
L(c)=\frac{1}{G}\sum_h(S_{ch}+m_{ch}L_{ch}),\qquad
U(c)=\frac{1}{G}\sum_h(S_{ch}+m_{ch}U_{ch}).
\]

The robust envelope is

\[
L_{rob}=\min_{c\in\mathcal C}L(c),\qquad
U_{rob}=\max_{c\in\mathcal C}U(c).
\]

This is sharp relative to the enumerated scenarios and their support assumptions, if
each scenario is feasible and every missing value can independently attain its support
endpoint. It is not automatically sharp for a richer classification space or correlated
constraints omitted from the model.

## Synthetic test
Population \(G=100\). Scenario A: observed sums 10 and 20; missing counts 30 and 30;
supports \([0,0.2]\) and \([0.4,1]\). Thus
\(L(A)= (10+20+30(0)+30(0.4))/100=0.42\) and
\(U(A)= (10+20+30(0.2)+30(1))/100=0.66\).

Scenario B: observed sums 12 and 18; missing counts 20 and 40 with the same supports.
Thus \(L(B)=(12+18+20(0)+40(0.4))/100=0.46\) and
\(U(B)=(12+18+20(0.2)+40(1))/100=0.70\).

Therefore the robust envelope is \([0.42,0.70]\), width \(0.28\). Scenario A
sets the lower endpoint and scenario B the upper endpoint. (The test suite independently
checks the arithmetic and rejects invalid inputs.)

## Profound finding
Uncertain classification is not just another margin of error: it changes which support
constraints apply to which units. Robust inference must optimize over classification
scenarios *and* missing-value completions. Precision claims are only as defensible as
the admissible scenario set; narrowing that set requires external classification evidence,
not a tighter numerical solver.

## Great Scale mapping
- CXXXII: justified strata can tighten global support bounds.
- CXXXIII: retain validity when stratum support endpoints are uncertain.
- CXXXIV: retain validity when missing counts by stratum are uncertain.
- CXXXV: retain validity when classification itself is uncertain.
- Next: replace finite scenario lists with a constrained integer optimization model and compare its solution to exhaustive enumeration on small cases.

## Scope and limitations
This is deterministic partial-identification analysis. No sampling uncertainty, causal
interpretation, or empirical validity of the synthetic support assumptions is claimed.
