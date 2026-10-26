#!/usr/bin/env python3
"""CLXI: local fallback must not silently become procurement authorization."""


def authorization(status, authority, explicit_opt_in=False, config_opt_in=False):
    """Model the corrected LICP helper, not the former implicit-fallback predicate."""
    return explicit_opt_in or config_opt_in or (
        status == "ok" and authority == "public"
    )


def test_local_fallback_is_rejected_without_explicit_opt_in():
    for status in ("not_found", "unreachable", "unconfigured", "invalid"):
        assert authorization(status, "local", False, False) is False


def test_local_fallback_is_accepted_with_explicit_opt_in():
    for status in ("not_found", "unreachable", "unconfigured", "invalid"):
        assert authorization(status, "local", True, False) is True
        assert authorization(status, "local", False, True) is True


def test_public_success_is_accepted_without_local_opt_in():
    assert authorization("ok", "public", False, False) is True


def test_unknown_or_mismatched_authority_fails_closed():
    assert authorization("ok", "unknown", False, False) is False
    assert authorization("unreachable", "public", False, False) is False
    assert authorization("ok", "local", False, False) is False


if __name__ == "__main__":
    tests = [
        test_local_fallback_is_rejected_without_explicit_opt_in,
        test_local_fallback_is_accepted_with_explicit_opt_in,
        test_public_success_is_accepted_without_local_opt_in,
        test_unknown_or_mismatched_authority_fails_closed,
    ]
    for test in tests:
        test()
    print(f"PASS CLXI authority-preserving fallback ({len(tests)}/{len(tests)} tests)")
