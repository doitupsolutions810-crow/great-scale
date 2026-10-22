# Great Scale Levels 4301–4400 — Proof Validity and Checker Soundness

## Research question
Can a claim-bound evidence receipt establish mathematical correctness? No: binding establishes identity of the referenced claim and assumptions, not that the proof object is valid or that the checker implements sound inference rules.

## Minimal proof kernel
This branch adds a small natural-deduction reference checker for propositional formulas with assumptions, conjunction introduction/elimination, implication introduction/elimination, and disjunction introduction. It also includes a finite truth-table oracle to cross-check accepted derivations over the formula's atoms.

A proof object is accepted only if its inference rule's syntactic preconditions hold. The test harness then checks the resulting sequent semantically over every valuation of its finite atom set. This provides a useful cross-check for this small language, not a proof of the checker itself.

## Formal assurance ladder
Let (K(p)=(Gamma,arphi)) mean the checker accepts proof object (p) as deriving conclusion (arphi) from assumptions (Gamma).

- **Binding:** the proof object and checker version are bound to the intended claim and assumptions.
- **Kernel acceptance:** (K) accepts the proof object under its encoded inference rules.
- **Metatheoretic soundness:** for every accepted derivation, (Gamma models arphi).
- **Implementation assurance:** the executed implementation faithfully realizes the specified kernel.
- **Interpretation/scope assurance:** the formal symbols and assumptions correctly represent the intended target domain.

The truth-table oracle checks semantic consequence for finite propositional formulas only. It does not prove general kernel soundness, validate external empirical data, authenticate provenance, or establish physical laws.

## Run
`node test_proof_kernel.js`
`npm test`
`python3 test_descent.py`

## Candidate finding
A certificate's identity is not its validity; validity is not the same as checker soundness; checker soundness is not the same as applicability to the intended scientific domain. Each transition needs its own explicit obligation.

## Limits
The checker is a teaching/reference kernel. It is not independently verified, not cryptographically authenticated, and not suitable as a production proof assistant. No Quantum Geometry Mathematics physical hypothesis is verified by these tests.
