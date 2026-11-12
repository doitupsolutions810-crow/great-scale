# Great Scale CXLVIII — Property-Guided Quotient Refinement

## Question

Can a quotient be repaired when a required state property varies inside one of
its blocks, without merging any states that the earlier model kept separate?

## Algorithm

Given a partition \(\Pi\) and required Boolean properties
\(P_1,\ldots,P_m\), define each state's property signature

\[
\sigma(s)=(P_1(s),\ldots,P_m(s)).
\]

Replace each block \(B\in\Pi\) with its nonempty intersections by signature:
\(B_v=\{s\in B:\sigma(s)=v\}\). This only splits blocks; it never merges
states across existing blocks.

## Guarantee and limitation

Every output block has a constant signature for all supplied properties.
The output is the coarsest refinement of the *given partition* that achieves
that property constancy: any partition refining the input and making those
properties constant must keep different signatures apart.

This routine alone does **not** re-establish transition congruence. If the
partition must remain a valid behavioral quotient, transition preservation must
be rechecked after splitting; a complete implementation must iterate the
behavioral and property refinements to a joint fixed point.

## Test plan

Six unit tests cover a safe/unsafe split, joint signatures, no unnecessary
splitting, empty property sets, empty-block rejection, and duplicate-state
rejection. These tests are authored; they must be executed before claiming a
passing test run.

## Great Scale conclusion

A failed preservation audit is not merely a warning: it gives a constructive
refinement signal. Required knowledge can be made explicit as a partition
constraint. The next challenge is the joint fixed point between properties and
transitions, not property splitting in isolation.
