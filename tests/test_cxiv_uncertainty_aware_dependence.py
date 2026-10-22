import pytest
from cxiv_uncertainty_aware_dependence import analyze_dependence

def rows(pairs):
    return [{"a_failed": a, "b_failed": b} for a, b in pairs]

def test_reproducible():
    sample = rows([(True, True)] * 10 + [(False, False)] * 10)
    assert analyze_dependence(sample, seed=19) == analyze_dependence(sample, seed=19)

def test_perfect_cofailure_positive_excess():
    result = analyze_dependence(rows([(True, True)] * 10 + [(False, False)] * 10), seed=3)
    assert result["excess_joint_failure"] == pytest.approx(0.25)
    assert result["interval_lower"] > 0
    assert result["status"] == "EVIDENCE_OF_POSITIVE_EXCESS"

def test_factorial_pattern_inconclusive():
    sample = rows([(True, True)] * 25 + [(True, False)] * 25 + [(False, True)] * 25 + [(False, False)] * 25)
    result = analyze_dependence(sample, seed=5)
    assert result["excess_joint_failure"] == pytest.approx(0)
    assert result["interval_lower"] <= 0 <= result["interval_upper"]
    assert result["status"] == "INCONCLUSIVE"

def test_small_sample_flagged():
    result = analyze_dependence(rows([(True, True), (False, False)] * 4), min_trials=20)
    assert result["status"] == "INSUFFICIENT_DATA"

@pytest.mark.parametrize("bad", [1, "true", None])
def test_non_boolean_rejected(bad):
    with pytest.raises(ValueError, match="booleans"):
        analyze_dependence([{"a_failed": bad, "b_failed": False}])

def test_missing_field_rejected():
    with pytest.raises(ValueError, match="contain a_failed and b_failed"):
        analyze_dependence([{"a_failed": True}])

@pytest.mark.parametrize("kwargs", [{"bootstrap_replicates": 99}, {"alpha": 0}, {"alpha": 1}, {"min_trials": 1}])
def test_bad_config_rejected(kwargs):
    with pytest.raises(ValueError):
        analyze_dependence([{"a_failed": True, "b_failed": False}], **kwargs)

def test_empty_rejected():
    with pytest.raises(ValueError, match="at least one"):
        analyze_dependence([])
