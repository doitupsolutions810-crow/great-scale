from cxlxxiv_counterexample_minimization import minimize_counterexample


def test_minimizer_preserves_failure_and_removes_irrelevant_elements():
    case = ("noise-a", "left", "noise-b", "right", "noise-c")
    result = minimize_counterexample(
        case,
        lambda xs: "left" in xs and "right" in xs,
    )
    assert result == ("left", "right")


def test_minimizer_rejects_case_that_does_not_fail():
    try:
        minimize_counterexample((1, 2, 3), lambda xs: False)
    except ValueError as exc:
        assert "does not reproduce" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_minimizer_result_is_1_minimal():
    case = (1, 2, 3, 4, 5, 6)
    predicate = lambda xs: 2 in xs and 5 in xs
    result = minimize_counterexample(case, predicate)
    assert predicate(result)
    for i in range(len(result)):
        assert not predicate(result[:i] + result[i + 1 :])
