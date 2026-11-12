# Great Scale CIV — Auditable Predictability

## Question
Can an execution trace make the order of betting decisions and observations independently checkable?

## Trace protocol
For each step, first emit a bet record containing the step number, previous chain hash, digest of the prior outcomes, q0, and lambda. Hash this record. Then emit an outcome record referencing the bet hash, containing the observed binary outcome and resulting wealth. Hash the outcome record and use it as the prior hash for the next step. The verifier replays the chain and recomputes wealth.

## Statistical invariant
Under H0, E[X_t | F_(t-1)] <= q0. If lambda_t is chosen using only F_(t-1) and lies in [0, 1/q0], then

E[1 + lambda_t(X_t-q0) | F_(t-1)] <= 1.

Consequently M_t=M_(t-1)[1+lambda_t(X_t-q0)] is a nonnegative supermartingale and Ville's inequality bounds the probability of ever crossing 1/alpha by alpha.

## What the audit trace establishes
The SHA-256 chain detects edits, deletions, reordering, and inconsistent recorded wealth relative to the supplied trace. The verifier checks that each bet record precedes its outcome record and binds the bet to the digest of the recorded past.

## What it does not establish
A hash chain alone does not prove a trusted timestamp, prevent someone with control of the entire log from rewriting and rehashing it, prove that a strategy callback did not use hidden state, or prove the statistical null. Stronger assurance requires an external append-only witness or signed timestamp, restricted execution, and independently controlled data capture. This is an audit aid, not a zero-knowledge proof or a cryptographic proof of strategy causality.
