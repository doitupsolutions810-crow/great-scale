# Great Scale CXL — Adaptive State Refinement

## Question
What happens when two assignments have identical stratum counts but different
unit-specific contributions?

## Counterexample
Two units can each be assigned to A or B. Their additive endpoint contributions
are unit-specific:

- Unit 1: A contributes (0.0, 0.1), B contributes (0.4, 0.5).
- Unit 2: A contributes (0.2, 0.3), B contributes (0.6, 0.7).

Assignments AB and BA have the same count vector (one A, one B), but lower sums
are 0.6 and 0.4, respectively. Therefore the count vector is not a sufficient
state for this objective.

## Corrected state
For this finite additive example, preserve the count vector together with the
accumulated lower and upper contributions. More generally, the state must retain
a sufficient statistic for every quantity affecting feasibility or objective.
If interaction constraints exist, sums alone may not suffice; interaction state
must also be represented.

## Scientific finding
Compression is safe only relative to a specified model. A state that is sufficient
for a homogeneous objective may become insufficient after adding unit-specific
effects. State design is therefore a model-dependent proof obligation, not merely
a performance optimization.

## Verification
Authored tests check the counterexample, the homogeneous case, and invalid inputs.
They have not been run in CI/runtime during this turn.
