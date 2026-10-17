# Great Scale CXLXV — Integrated Typed Identity and Differential Fuzzing

## Finding
Identity encoding is part of a certificate's semantics. Producer and verifier must share one explicit, typed encoding; otherwise a structurally plausible certificate can refer to ambiguous identities. This rung wires CXLXIV's `gs-typed-v1` encoder into the CXLXII certificate path and versions certificates as `gs-quotient-cert-v2`.

## Mathematics
For canonical encoder E, state identity is keyed by E(s), and refinement uses
\[
\sigma_i(s)=\big(O(s),P(s),\operatorname{sort}\{(E(a),i(\delta(s,a)))\}\big).
\]
Starting from the observation/property partition, refine until stable at \(\Pi^*\). Accept only if the submitted partition equals \(\Pi^*\), the certificate's canonical mapping matches, and each block is transition-congruent.

## Tests
Deterministic exhaustive differential comparison on two-state models, type-tag separation, unsupported-label rejection, order metamorphism, and schema-version tampering. Run with `python -m pytest tests/test_cxlxv_integrated_encoding_fuzzing.py`.

## Ladder
CXLXII Quotient Certificates → CXLXIII Adversarial Testing → CXLXIV Canonical Typed Encoding → **CXLXV Integrated Encoding + Differential Fuzzing**.

## Limits
Encoder supports None, bool, int, str, finite float, and tuples of supported values. States must be hashable for Python mapping-based models. Legacy v1 certificates are intentionally rejected. Bounded differential tests find counterexamples; they do not prove correctness for all finite models.
