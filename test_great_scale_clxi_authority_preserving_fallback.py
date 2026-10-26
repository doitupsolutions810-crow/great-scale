#!/usr/bin/env python3
"""CLXI: local fallback must not silently become procurement authorization."""


def current_policy(status, authority, explicit_opt_in=False, config_opt_in=False):
    # Mirrors living-intermediate-control-plane/integrate.mjs as inspected 2026-10-26.
    return (
        explicit_opt_in
        or config_opt_in
        or (authority == "local" and status != "ok")
    )


def corrected_policy(status, authority, explicit_opt_in=False, config_opt_in=False):
    # Availability and authorization are independent: local evidence requires opt-in.
    return explicit_opt_in or config_opt_in or (
        status == "ok" and authority == "public"
    )


def test_counterexample_implicit_local_fallback_authorizes():
    assert current_policy("not_found", "local", False, False) is True
    assert corrected_policy("not_found", "local", False, False) is False


def test_all_degraded_local_states_require_explicit_opt_in():
    for status in ("not_found", "unreachable", "unconfigured", "invalid"):
        assert corrected_policy(status, "local", False, False) is False
        assert corrected_policy(status, "local", True, False) is True
        assert corrected_policy(status, "local", False, True) is True


def test_public_success_does_not_require_local_opt_in():
    assert corrected_policy("ok", "public", False, False) is True


def test_unknown_authority_fails_closed():
    assert corrected_policy("ok", "unknown", False, False) is False
    assert corrected_policy("unreachable", "unknown", False, False) is False


if __name__ == "__main__":
    tests = [
        test_counterexample_implicit_local_fallback_authorizes,
        test_all_degraded_local_states_require_explicit_opt_in,
        test_public_success_does_not_require_local_opt_in,
        test_unknown_authority_fails_closed,
    ]
    for test in tests:
        test()
    print(f"PASS CLXI authority-preserving fallback ({len(tests)}/{len(tests)} tests)")
