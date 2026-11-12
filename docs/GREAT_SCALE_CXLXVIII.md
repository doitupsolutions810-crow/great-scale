# Great Scale CXLXVIII — Canonical IDs as Primary Keys

## Finding
Rejecting host-language key collisions is safe but restrictive. A more complete design stores state records and transition edges by canonical IDs, while preserving original labels only as metadata. Records and edges arrive as sequences, so the input can express labels such as `True` and `1` without first collapsing them into a Python dictionary.

## Model
For each state label s, define id(s) = E(s). The model stores state data under id(s), and each transition stores an action ID and either a successor ID or a terminal marker:

`state_id --action_id--> successor_id`

The normalized model performs partition refinement over canonical IDs, preserving observation/property classes and deterministic transition signatures.

## Implementation
- `cxlxviii_canonical_id_model.py`: sequence-based input API, canonical-ID state/action keys, successor validation, partition refinement.
- `tests/test_cxlxviii_canonical_id_model.py`: typed label coexistence, successor resolution, unknown successor rejection, duplicate identity rejection, and quotient class preservation.
- `artifacts/cxlxviii_canonical_id_model.json`: machine-readable summary.

## Limits and validation
This is a new model API, not yet a drop-in migration of every older certificate function. The test module is authored; execution must be reported separately. Canonical identity is only as robust as the encoder's supported types and schema/version discipline. Observation/property payload equality semantics also need a documented normalization contract.

## Great Scale conclusion
The previous rung detected an identity boundary. This rung moves identity into the storage architecture itself. The next proof obligation is differential equivalence: for models without host-language collisions, the new quotient must match the existing verifier, while collision-bearing labels remain distinct.
