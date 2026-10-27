# Descent CXC — A gate can be correct and still add no protection

## Finding

The current residual equations are:

\[
\Psi(S)=C+S,\qquad \operatorname{ConeOK}(S)=[\Psi(S)\ge C-10^{-12}]
\]

where \(C=(\varphi-1)^2\), and the residual parser accepts only \(S\in[0,0.25]\).

Substitution gives:

\[
\operatorname{ConeOK}(S)=[C+S\ge C-10^{-12}]
=[S\ge -10^{-12}]
\]

Every input in the accepted domain already satisfies that inequality. Therefore the cone gate has no discriminating power on the parser's valid domain: it is mathematically redundant with the domain restriction. This is not evidence of an exploit; it is an assurance-design issue because the gate may be counted as an independent safeguard when the accepted input domain makes it always pass.

## Great Scale mapping

Let \(D\) be domain validation and \(G\) be the cone gate. On \(S\in[0,0.25]\):

\[
D(S)=1\Rightarrow G(S)=1
\]

so:

\[
D(S)\land G(S)=D(S)
\]

The second predicate contributes no additional rejection power. A defense-in-depth claim should only count a gate as independent if there exists an in-domain adversarial state rejected by that gate while passing the other checks.

## Regression added

- `test_great_scale_cxc_cone_gate_vacuity.py` checks the equation at domain endpoints and representative values, and checks that the formula does reject a negative out-of-domain value.
- The test is appended to the `npm run all` aggregate in `package.json`.
- The canonical CI workflow invokes `npm run all`.

## Recommended next correction

Choose and document one of two contracts:

1. **Domain-only contract:** explicitly state that \(S\ge0\) is the actual invariant and treat the cone check as a derived diagnostic, not an independent security gate.
2. **Independent cone contract:** define a meaningful upstream residual domain that includes candidate values capable of violating the floor, then verify that parsing, normalization, and authorization all reject them before side effects.

Do not weaken the existing nonnegative domain merely to make the test fail. The next step is to execute the new regression and the complete suite in a clean checkout, then bind a successful hosted CI run to the exact resulting commit.

## Verification boundary

The regression and aggregate wiring are committed on the research branch. The isolated test's execution and full aggregate/hosted CI are not claimed here unless a recorded run for the exact commit confirms them. No production behavior was changed by this finding.
