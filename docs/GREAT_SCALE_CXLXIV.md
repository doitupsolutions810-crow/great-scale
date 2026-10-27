# Great Scale CXLXIV — Canonical Typed Encoding

## Descent question
Can a certificate identify states and actions without relying on human-readable representations such as `repr`?

## Typed encoding contract
This rung defines `gs-typed-v1` for `None`, booleans, integers, strings, finite IEEE-754 floats, and recursively encoded tuples. Each value receives an explicit type tag. Integers use decimal strings; floats use `float.hex()` after rejecting NaN and infinities; JSON serialization uses fixed separators and Unicode preservation. Unsupported types fail closed rather than falling back to an address-bearing or ambiguous representation.

Examples:

- `True` → `["bool",true]`
- `1` → `["int","1"]`
- `"1"` → `["str","1"]`

Thus values that compare equal in Python, such as `True` and `1`, remain distinct encoded identities.

## Mathematical property
For supported values, the encoding aims for injectivity by type and value: if `E(x)=E(y)`, then `x` and `y` have the same supported type and recursively identical value. This is an implementation contract that should be tested across versions; it is not a cryptographic commitment.

## Great Scale mapping
Model labels → typed canonical encoding `E` → versioned identity list → quotient certificate. The encoding layer is now explicit, so serialization assumptions can be tested separately from partition-refinement correctness.

## Limitations
This module is a new utility and is not yet wired into the CXLXII certificate producer/verifier. Integration into that path and differential fuzzing are the next steps. No claim of cryptographic security or executed test success is made until CI runs the tests.
