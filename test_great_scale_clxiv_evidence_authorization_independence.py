#!/usr/bin/env python3
"""CLXIV: procurement force flags cannot manufacture evidence authorization."""


def procurement_authorized(*, core_ready, evidence_status, evidence_authority, local_opt_in, force=False):
    public_valid = evidence_status == "ok" and evidence_authority == "public"
    # 'force' is intentionally non-authoritative: it cannot alter evidence trust.
    return core_ready and (public_valid or local_opt_in)


def test_verified_public_evidence_authorizes_ready_core():
    assert procurement_authorized(core_ready=True, evidence_status="ok", evidence_authority="public", local_opt_in=False)


def test_explicit_local_opt_in_authorizes_ready_core():
    assert procurement_authorized(core_ready=True, evidence_status="unreachable", evidence_authority="local", local_opt_in=True)


def test_degraded_local_fallback_denied_by_default_even_with_force():
    assert not procurement_authorized(core_ready=True, evidence_status="unreachable", evidence_authority="local", local_opt_in=False, force=True)


def test_unknown_authority_fails_closed_even_with_force():
    assert not procurement_authorized(core_ready=True, evidence_status="ok", evidence_authority="unknown", local_opt_in=False, force=True)


def test_core_readiness_is_still_required():
    assert not procurement_authorized(core_ready=False, evidence_status="ok", evidence_authority="public", local_opt_in=False, force=True)


if __name__ == "__main__":
    tests = [
        test_verified_public_evidence_authorizes_ready_core,
        test_explicit_local_opt_in_authorizes_ready_core,
        test_degraded_local_fallback_denied_by_default_even_with_force,
        test_unknown_authority_fails_closed_even_with_force,
        test_core_readiness_is_still_required,
    ]
    for test in tests:
        test()
    print(f"PASS CLXIV evidence authorization independence ({len(tests)}/{len(tests)} tests)")
