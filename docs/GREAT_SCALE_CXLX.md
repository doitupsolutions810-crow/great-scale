# Great Scale CXLX — Robustness Under Model Change

## Question
When the finite transition model changes, does refinement seeded with the prior quotient agree with a fresh computation?

## Mathematical object
Let a finite labeled transition system M=(S,A,→,O,P), with observation map O, Boolean property vector P, and deterministic action-successor map (an absent action is disabled; successor None denotes terminal behavior). A partition Π is admissible when states in each block agree on O, P, enabled actions, terminal behavior, and successor blocks for each enabled action.

For a model update M→M', the incremental algorithm:
1. intersects old blocks with the new state domain;
2. places newly added states in singleton blocks;
3. splits blocks by current observation/property signatures;
4. repeatedly splits by enabled-action and successor-block signatures until stable.

It deliberately retains prior distinctions. Therefore incremental and full recomputation need not produce the same coarsest partition if the prior partition contained distinctions no longer required by the changed model. The correct safety criterion is equivalence of the induced quotient's preserved behavior/properties, not byte-for-byte equality of partitions. The included audit compares partitions as a stricter diagnostic for the test fixtures, not a universal theorem.

## Termination
Every iteration only splits blocks. If |S|=n, there can be at most n−1 strict increases in block count, so the process terminates after finitely many strict refinements.

## Profound finding
A cached quotient is not automatically a canonical quotient after the model changes. Incremental refinement is safe as a conservative cache only when its retained distinctions are acceptable; canonical minimality may require recomputation or a proven merge phase. Thus **soundness and minimality are separate guarantees**.

## Test plan
The unit tests cover transition changes, state addition, property changes, observation changes, retention of old distinctions, and rejection of invalid successors. These tests are authored but must be executed in a configured Python environment before being treated as passing.

## Great Scale placement
CXLVI behavioral quotient → CXLVII property audit → CXLVIII property-guided split → CXLIX joint fixed point → **CXLX model-change robustness**.

This is a finite deterministic model-checking abstraction, not evidence that a physical system follows the model.
