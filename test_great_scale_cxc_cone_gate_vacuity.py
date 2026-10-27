#!/usr/bin/env python3
"""CXC: prove whether the residual cone gate has discriminating power on its accepted domain.

This is a model-level audit of the currently published equations:
    Psi(S) = CONE + S
    cone_ok = Psi(S) >= CONE - 1e-12
with parser domain S in [0, 0.25].
"""
import math

PHI = (1 + math.sqrt(5)) / 2
CONE = (PHI - 1) ** 2
MIN_S = 0.0
MAX_S = 0.25
TOL = 1e-12


def psi(s):
    return CONE + s


def cone_compliant(s):
    return psi(s) >= CONE - TOL


def main():
    # Domain endpoints and representative values accepted by the parser.
    domain = [MIN_S, 1e-15, 0.01, 0.125, 0.25, MAX_S]
    assert all(MIN_S <= s <= MAX_S for s in domain)
    assert all(cone_compliant(s) for s in domain)

    # Algebraic proof of vacuity on the accepted domain:
    # Psi(S) >= CONE iff S >= 0; every accepted S already satisfies that.
    for s in domain:
        assert math.isclose(psi(s) - CONE, s, rel_tol=0.0, abs_tol=1e-15)
        assert (s >= 0.0) == (psi(s) >= CONE)

    # The function does discriminate outside the accepted domain, so the issue
    # is not the formula itself; it is the overlap of gate and domain constraints.
    assert not cone_compliant(-1e-6)
    assert cone_compliant(0.0)

    print("CXC cone-gate vacuity audit: PASS")
    print(f"accepted domain: [{MIN_S}, {MAX_S}]")
    print(f"Psi(S)=CONE+S; all accepted values pass cone floor: {len(domain)}/{len(domain)}")
    print("finding: cone gate is redundant on this domain; range validation carries the restriction")
    print("scope: equation/model audit only; no claim that production authorization is exploitable")


if __name__ == "__main__":
    main()
