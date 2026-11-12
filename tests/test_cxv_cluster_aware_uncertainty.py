import pytest
from cxv_cluster_aware_uncertainty import analyze_cluster_dependence

def make_trials(cluster_pairs):
    return [
        {"cluster_id": cluster, "a_failed": a, "b_failed": b}
        for cluster, pairs in cluster_pairs
        for a, b in pairs
    ]

def test_cluster_bootstrap_is_reproducible():
    sample = make_trials([(f"c{i}", [(True, True), (False, False)]) for i in range(12)])
    assert analyze_cluster_dependence(sample, seed=7) == analyze_cluster_dependence(sample, seed=7)

def test_counts_clusters_separately_from_trials():
    sample = make_trials([(f"c{i}", [(True, True), (False, False)] * 3) for i in range(12)])
    result = analyze_cluster_dependence(sample)
    assert result["n_trials"] == 72
    assert result["n_clusters"] == 12
    assert result["status"] == "EVIDENCE_OF_POSITIVE_EXCESS"
    assert result["excess_joint_failure"] == pytest.approx(0.25)

def test_many_trials_few_clusters_is_flagged():
    sample = make_trials([(f"c{i}", [(True, True), (False, False)] * 50) for i in range(3)])
    result = analyze_cluster_dependence(sample, min_clusters=10)
    assert result["n_trials"] == 300
    assert result["n_clusters"] == 3
    assert result["status"] == "INSUFFICIENT_CLUSTERS"

def test_missing_cluster_id_rejected():
    with pytest.raises(ValueError, match="cluster_id"):
        analyze_cluster_dependence([{"a_failed": True, "b_failed": False}])

def test_bad_outcome_rejected():
    with pytest.raises(ValueError, match="booleans"):
        analyze_cluster_dependence([{"cluster_id": "x", "a_failed": 1, "b_failed": False}])

def test_empty_input_rejected():
    with pytest.raises(ValueError, match="at least one"):
        analyze_cluster_dependence([])

@pytest.mark.parametrize("kwargs", [
    {"bootstrap_replicates": 99}, {"alpha": 0}, {"alpha": 1}, {"min_clusters": 1}
])
def test_invalid_config_rejected(kwargs):
    with pytest.raises(ValueError):
        analyze_cluster_dependence([{"cluster_id": "x", "a_failed": True, "b_failed": True}], **kwargs)
