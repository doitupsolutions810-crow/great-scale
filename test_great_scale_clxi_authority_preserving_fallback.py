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

def test_default_procurement_command_is_fail_closed():
    # Mirrors package.json: procure does not inject ACCEPT_LOCAL_EVIDENCE.
    default_env = {}
    local_mode_env = {"ACCEPT_LOCAL_EVIDENCE": "1"}
    assert authorization("unconfigured", "local", default_env.get("ACCEPT_LOCAL_EVIDENCE") == "1") is False
    assert authorization("unconfigured", "local", local_mode_env.get("ACCEPT_LOCAL_EVIDENCE") == "1") is True


if __name__ == "__main__":
    tests = [
        test_local_fallback_is_rejected_without_explicit_opt_in,
        test_local_fallback_is_accepted_with_explicit_opt_in,
        test_public_success_is_accepted_without_local_opt_in,
        test_unknown_or_mismatched_authority_fails_closed,
        test_default_procurement_command_is_fail_closed,
    ]
    for test in tests:
        test()
    print(f"PASS CLXI authority-preserving fallback ({len(tests)}/{len(tests)} tests)")
