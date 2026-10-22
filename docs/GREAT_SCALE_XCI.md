# Great Scale XCI — Active Measurement and the Value of Information

## Question
When current observations cannot distinguish relevant states, which additional measurement should be taken, and when is its cost justified?

## Model
Let H be the hidden state, p(h) its prior, and Y the measurement outcome. With likelihoods P(Y=y | H=h), expected information gain is mutual information:
I(H;Y) = H(H) - E_Y[H(H|Y)].
Entropy uses natural logarithms, so information is in nats.

Information gain differs from decision value. For utility U(d,h), expected value of sample information is:
EVSI = E_Y[max_d E[U(d,H)|Y]] - max_d E[U(d,H)].
For measurement cost c in the same utility units, net value is EVSI - c. Under this finite decision model the measurement can be ignored after observation, so EVSI is non-negative up to floating-point error. Measure only when net value is positive under the supplied model.

## Demonstration
Two states have prior probability 0.5 each. A perfect measurement reveals the state. Two decisions earn +1 for the correct state and -1 for the incorrect state. Without measurement, best expected utility is 0. After a perfect measurement, expected utility is 1, so EVSI = 1. At cost 0.2, net value = 0.8 and the model recommends MEASURE. At cost 1.1, net value = -0.1 and it recommends DO_NOT_MEASURE.

If utility is identical across states for every available decision, a perfect measurement still yields ln(2) nats but EVSI is zero: the information cannot improve the decision.

## Implementation
The active_measurement.py module provides entropy, information_gain, and expected_value_of_sample_information. It validates normalization, dimensions, finite values, and non-negative cost. Inputs must be empirically justified by the caller. The computed values follow from the model; they do not prove the inputs match reality.

## Scientific limits and safeguards
- Misspecified priors or likelihoods can misrank measurements.
- Utility scales and measurement cost must be comparable.
- High information gain can be operationally irrelevant.
- Positive modelled net value does not guarantee real-world benefit.
- High-stakes use should include sensitivity analysis over plausible priors, likelihoods, utilities, and costs.
- This is a finite discrete decision model, not a general causal model.

## Pinned finding
**The best next measurement is the one that can improve a consequential decision enough to justify its cost—not necessarily the one that reveals the most.**

## Test scope
tests/test_active_measurement.py covers entropy, perfect and uninformative measurements, decision-changing information, cost thresholds, irrelevant information, and invalid inputs. Passing unit tests verifies implementation examples, not empirical calibration or deployment safety.
