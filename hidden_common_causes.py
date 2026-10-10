"""Great Scale LXXXVII: auditable candidate hidden-dependency assessment.

Likelihood inputs must be supplied by a defensible statistical model. This module
calculates odds and enforces a separate, predeclared validation gate; it does not
infer causality from correlation by itself.
"""
from dataclasses import dataclass


def posterior_probability(prior_probability: float, likelihood_ratio: float) -> float:
    if not 0 < prior_probability < 1:
        raise ValueError("prior_probability must be strictly between 0 and 1")
    if likelihood_ratio < 0:
        raise ValueError("likelihood_ratio must be non-negative")
    prior_odds = prior_probability / (1.0 - prior_probability)
    posterior_odds = prior_odds * likelihood_ratio
    return posterior_odds / (1.0 + posterior_odds)


@dataclass(frozen=True)
class CandidateAssessment:
    candidate_id: str
    prior_probability: float
    discovery_likelihood_ratio: float
    validation_likelihood_ratio: float
    validation_is_independent: bool
    threshold: float

    @property
    def discovery_posterior(self) -> float:
        return posterior_probability(self.prior_probability, self.discovery_likelihood_ratio)

    @property
    def accepted_for_model_update(self) -> bool:
        """A strict gate: independent validation and predeclared LR threshold."""
        return (self.validation_is_independent
                and self.validation_likelihood_ratio >= self.threshold)

    @property
    def disposition(self) -> str:
        if not self.validation_is_independent:
            return "HOLDOUT_NOT_INDEPENDENT"
        if self.validation_likelihood_ratio < self.threshold:
            return "NOT_VALIDATED"
        return "ELIGIBLE_FOR_REVIEW_NOT_AUTOMATICALLY_CAUSAL"


def assess_candidate(candidate_id: str, prior_probability: float,
                     discovery_likelihood_ratio: float,
                     validation_likelihood_ratio: float,
                     validation_is_independent: bool,
                     threshold: float) -> CandidateAssessment:
    if not candidate_id.strip():
        raise ValueError("candidate_id must be non-empty")
    if validation_likelihood_ratio < 0 or threshold < 0:
        raise ValueError("likelihood ratio and threshold must be non-negative")
    # Validate probability and discovery LR through the shared calculation.
    posterior_probability(prior_probability, discovery_likelihood_ratio)
    return CandidateAssessment(candidate_id, prior_probability,
                               discovery_likelihood_ratio,
                               validation_likelihood_ratio,
                               validation_is_independent, threshold)
