# Great Scale LXXXV — Diversity of Failure Mechanisms and Robust Replication

## Pinned finding

Replication becomes robust when evidence pathways do not all fail under the same plausible causes. Independence should be supported by dependency design and adversarial testing, not inferred from pathway count or different labels.

## Finite fault model

Let pathways be P_i and candidate failure sources be f_j. Define A_ij=1 when pathway i depends on source j. A pathway is compromised when any of its declared dependencies fails. For failed-source set S, let R(S) count surviving pathways. If a conclusion requires k pathways, it remains supported in this model when R(S) >= k.

A cut set is a set S with R(S) < k. It is minimal if no proper subset of S is also a cut set. Minimal cut sets expose the smallest modeled combinations of failures that defeat the evidence threshold.

## Implementation

The root-level module replication_resilience.py:
- enumerates surviving pathways under a specified fault set;
- evaluates a minimum-surviving-path threshold;
- enumerates minimal cut sets for small finite dependency models.

Enumeration is exponential in the number of candidate sources; use it for compact audits, not unbounded production inventories.

## Worked example

A={A:{calibration,sensor-A}, B:{calibration,lab-B}, C:{independent-reference,sensor-C}}.

If k=2, failure of the shared calibration source compromises A and B, leaving only C. Thus {calibration} is a minimal cut set for the two-path threshold. The example shows why a nominal count of three pathways is insufficient if two share a critical dependency.

## Scientific limits

The model assumes the dependency inventory and the rule “any declared dependency failure compromises its pathway” are adequate. Real systems require fault injection, evidence that supposedly separate sources are genuinely distinct, and monitoring for hidden dependencies. Passing software tests validates implementation behavior only; it does not validate the real-world dependency map.

## Great Scale progression

- LXXXIII: revoke conclusions downstream of invalid certificates.
- LXXXIV: identify shared causes that undermine apparent evidence independence.
- LXXXV: design for diversity of failure mechanisms and calculate minimal modeled cut sets.

Next: quantify the residual risk under empirically justified failure probabilities, including uncertainty in those probabilities and dependencies.
