# Great Scale CXLII — Coarsest Outcome-Preserving Partition

## Question

Can we quantify whether a sufficient state is also minimal for the outcomes we care about?

## Finite-domain theorem

Fix a finite assignment domain \(\mathcal A\) and a declared complete outcome signature \(O\). Define
\[
a\sim_O b \iff O(a)=O(b).
\]
Equality of signatures is an equivalence relation. Its equivalence classes form the coarsest partition that preserves \(O\): any key \(K\) satisfying
\[
K(a)=K(b)\Rightarrow O(a)=O(b)
\]
must keep distinct outcome classes separate. It may, however, split one outcome class into several states and thus retain unnecessary detail.

The audit reports:
- **collision:** same key, different outcome (unsound compression);
- **split:** different keys, same outcome (potentially redundant detail);
- **coarsest for signature:** no collisions or splits, and candidate state count equals the number of distinct outcomes.

This minimality is relative to the chosen finite domain and outcome signature. If the signature omits relevant constraints, transitions, or objectives, the computed partition is not sufficient for those omitted concerns.

## Example

For heterogeneous unit effects:
\[
O(AB)=(0.8,1.0),\quad O(BA)=(0.6,0.8).
\]
The count key merges AB and BA, producing one candidate state for two distinct outcome classes: it is insufficient.

For homogeneous additive effects on three binary units, the count key gives four count states and four distinct outcome signatures. On that finite example it is both sufficient and coarsest for the supplied lower/upper sums.

An over-refined key that retains assignment order may be sufficient but split assignments with equal outcomes. The audit identifies such splits and counts excess states.

## Complexity

The transparent reference implementation compares all pairs, requiring \(O(n^2)\) pair checks for \(n\) assignments. This is appropriate as a small-instance oracle, not a scalable solver for exponentially large assignment spaces.

## Great Scale mapping

- **Invariant:** key equality must imply outcome equality.
- **Compression loss:** collision witnesses.
- **Unnecessary state detail:** split witnesses.
- **Minimality target:** candidate partition equals the outcome-equivalence partition.
- **Scientific scope:** finite exhaustive audit relative to a declared signature, not a universal claim about real-world model adequacy.

## Test status

Four tests are authored for homogeneous count compression, heterogeneous collision detection, over-refinement, and the oracle key. They have not been executed as part of this integration action.
