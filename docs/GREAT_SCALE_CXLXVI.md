# Great Scale CXLXVI — Independent Oracle Hardening

## Question
Can a quotient verifier and a seemingly separate oracle share the same defect? Yes, if both are built around the same partition-refinement signature. This rung uses a pairwise relation-elimination oracle as a structurally different check.

## Mathematics
Begin with relation
\[
R_0=\{(s,t): O(s)=O(t),\ P(s)=P(t),\ A(s)=A(t)\},
\]
where \(A(s)\) is the enabled action set. Iteratively remove any pair whose corresponding actions disagree on terminal behavior or whose successors are no longer related:
\[
R_{k+1}=\{(s,t)\in R_k:\forall a\in A(s),\
[\delta(s,a)=\bot\Leftrightarrow\delta(t,a)=\bot]\land
[\delta(s,a),\delta(t,a)\in S\Rightarrow(\delta(s,a),\delta(t,a))\in R_k]\}.
\]
The finite descending sequence stabilizes at a greatest fixed point. Its classes provide an independently structured cross-check against the production partition-refinement implementation.

## Tests
- Exhaustive two-state enumeration across observations, absent edges, terminal edges, and state successors.
- Certificate mapping tamper.
- Over-merged partition rejection.
- Successor mutation and enabled-action mutation.

## Limits
This is a bounded model check, not a universal proof. The oracle assumes deterministic transitions and matching action labels. The pairwise relation's equivalence-class extraction and the production verifier both require further review before high-assurance use.
