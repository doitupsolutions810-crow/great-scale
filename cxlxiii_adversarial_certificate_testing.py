"""CXLXIII: adversarial and metamorphic checks for quotient certificates."""
from __future__ import annotations
from cxlxii_quotient_certificate import make_certificate, verify_certificate

def reference_partition(states, observations, properties, transitions):
    """Small independently structured fixed-point oracle for finite test models."""
    groups={}
    for s in states:
        groups.setdefault((observations[s],tuple(properties[s])),set()).add(s)
    partition=list(groups.values())
    canon=lambda p:frozenset(frozenset(b) for b in p)
    while True:
        idx={s:i for i,b in enumerate(partition) for s in b}
        refined={}
        for s in states:
            edges=tuple(sorted((repr(a),None if nxt is None else idx[nxt]) for a,nxt in transitions[s].items()))
            key=(observations[s],tuple(properties[s]),frozenset(transitions[s]),edges)
            refined.setdefault(key,set()).add(s)
        candidate=list(refined.values())
        if canon(candidate)==canon(partition): return canon(candidate)
        partition=candidate

def audit_model(states, observations, properties, transitions, partition):
    cert=make_certificate(states,observations,properties,transitions,partition)
    result=verify_certificate(states,observations,properties,transitions,partition,cert)
    oracle=reference_partition(states,observations,properties,transitions)
    return {"verifier_valid":result["valid"],"oracle_match":frozenset(frozenset(b) for b in partition)==oracle,
            "canonical_blocks":len(oracle),"reported_blocks":result["submitted_block_count"]}
