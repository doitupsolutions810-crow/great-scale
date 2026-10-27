# Great Scale CXLXX — Generated Differential Quotient Testing

## Question
Does the canonical-ID partition refinement agree with an independently structured reference refinement over a finite model space?

## Experiment
The regression test exhaustively enumerates three-state deterministic models. Each state has a binary observation and one of five transition choices: no edge, terminal edge, or an edge to one of the three states. This gives 2^3 * 5^3 = 1,000 models.

## Comparison
For each model, compare the equivalence classes returned by the canonical-ID implementation with a reference refinement that groups by observation/property and iteratively splits blocks using action and successor-block signatures. Compare partitions as sets of canonical-ID sets, not merely by block count.

## Additional invariant
Boolean True and integer 1 must remain distinct primary IDs in the new model representation.

## Limits
The test is authored but has not been independently executed in this workflow. The reference algorithm shares the same formal signature concept, so it is an independent implementation check, not a formal proof. This bounded three-state domain does not establish correctness for all finite models.

## Great Scale finding
Verification quality improves when the model space is enumerated and outputs are compared structurally. A disagreement can be turned into a minimal counterexample; a clean run supports bounded confidence only.