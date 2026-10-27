# Great Scale CXLVII — Quotient Correctness and Property Preservation

## Question

After compressing states into behavioral-equivalence classes, which claims about
the original system remain answerable from the quotient alone?

## Theorem

Let S be a finite state set, K:S→Q map states to quotient classes, and
P:S→{0,1} be a Boolean state property. The property is well-defined on the
quotient exactly when

    K(s) = K(t)  implies  P(s) = P(t), for all s,t in S.

If this holds, define P-hat([s]) = P(s). The implication makes this independent
of the chosen representative. Conversely, if P factors through the quotient,
states in the same class must have equal values.

## Counterexample

If safe and unsafe states occupy one quotient block, the property is_unsafe
takes values 0 and 1 in that block. No single quotient value can answer it
correctly for both states. This is an information-loss witness, not a claim
that every behavioral quotient has this flaw.

## What survives?

- Every state property constant on each quotient class survives.
- A property determined solely by a preserved observation survives when the
  observation is constant inside each class.
- A property depending on hidden distinctions may fail; the audit emits
  conflicting states as a witness.
- This state-property criterion does not prove preservation of arbitrary
  temporal/path properties. Those need a separate trace or temporal-logic
  argument under explicit transition assumptions.

## Great Scale conclusion

Minimality is question-relative. A quotient can be minimal for a declared
behavioral interface yet insufficient for a new safety, fairness, cost, or
scientific property. Before compression is trusted, list the properties that
must remain decidable and test block-constancy for each.

## Test scope

Tests cover invariant properties, mixed-block witnesses, quotient induction,
observation-derived properties, hidden unsafe flags, and empty-block validation.
Tests are authored; execution status must be obtained from CI or a local run.
