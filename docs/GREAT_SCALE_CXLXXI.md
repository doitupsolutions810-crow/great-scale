# Great Scale CXLXXI — Typed Semantic Signatures

## Analysis of CXLXX
Generated quotient testing exposed a gap in the test design: generated observations used only integers, so they could not reveal Python's equality collision between `True` and `1`. State IDs were canonicalized, but quotient initialization still grouped raw observation/property values using Python tuple hashing and equality.

## Finding
Typed identity must be preserved throughout the semantic pipeline, not only for state and action labels. Otherwise two distinct typed observations or property values can enter the same initial partition before transition refinement begins.

## Correction
The quotient initializer now groups states by canonical encodings of both observation and property tuples. This avoids Python's `True == 1` collision and avoids requiring raw structured observation values to be hashable, provided they are supported by the canonical encoder. Unsupported values fail closed through the encoder.

## Mathematics
Let `enc` be the canonical typed encoder. Initial equivalence is now defined by:

`x ~0 y iff enc(obs(x)) = enc(obs(y)) and enc(props(x)) = enc(props(y))`.

This is a typed semantic equivalence relation, not host-language equality. Refinement then splits these classes by action/successor signatures.

## Regression tests authored
- `True` and `1` observations remain in separate initial blocks.
- `(True,)` and `(1,)` property tuples remain distinct.
- The typed encoder itself gives different encodings to `True` and `1`.

## Validation status
Tests are authored but have not been independently executed in this workflow. The existing Vercel status does not establish Python test success. This is a semantic correction added to the open CXLXX pull request for review; it remains unmerged.