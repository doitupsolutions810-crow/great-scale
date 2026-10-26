#!/usr/bin/env python3
"""CLXIII: force flags must not bypass evidence authorization."""
def procurement_authorized(*, core_ready, public_evidence_valid, local_opt_in, force):
    # Safety invariant: force may request an action, but cannot manufacture trust.
    return core_ready and (public_evidence_valid or local_opt_in)

def test_public_evidence_authorizes_ready_core():
    assert procurement_authorized(core_ready=True, public_evidence_valid=True, local_opt_in=False, force=False)

def test_explicit_local_opt_in_authorizes_ready_core():
    assert procurement_authorized(core_ready=True, public_evidence_valid=False, local_opt_in=True, force=False)

def test_force_does_not_bypass_missing_evidence():
    assert not procurement_authorized(core_ready=True, public_evidence_valid=False, local_opt_in=False, force=True)

def test_core_readiness_remains_necessary():
    assert not procurement_authorized(core_ready=False, public_evidence_valid=True, local_opt_in=False, force=True)

if __name__ == "__main__":
    tests = [
        test_public_evidence_authorizes_ready_core,
        test_explicit_local_opt_in_authorizes_ready_core,
        test_force_does_not_bypass_missing_evidence,
        test_core_readiness_remains_necessary,
    ]
    for test in tests:
        test()
    print(f"PASS CLXIII force/evidence separation ({len(tests)}/{len(tests)} tests)")
