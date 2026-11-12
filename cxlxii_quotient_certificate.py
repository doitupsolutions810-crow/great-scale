"""CXLXII: independently checkable certificates for finite behavioral quotients."""
from __future__ import annotations
from collections import defaultdict
from typing import Mapping, Sequence

def _validate(states, observations, properties, transitions):
    domain=set(states)
    if len(domain)!=len(states): raise ValueError("states must be unique")
    if set(observations)!=domain or set(properties)!=domain or set(transitions)!=domain:
        raise ValueError("maps must cover exactly the state domain")
    for state, edges in transitions.items():
        if not isinstance(edges, Mapping): raise ValueError("each transition entry must be a mapping")
        for nxt in edges.values():
            if nxt is not None and nxt not in domain: raise ValueError("successor outside state domain")

def make_certificate(states, observations, properties, transitions, partition):
    """Serialize a proposed partition as a state-to-block certificate."""
    _validate(states, observations, properties, transitions)
    block_of={}
    for i, block in enumerate(partition):
        for state in block:
            if state in block_of: raise ValueError("state appears in multiple blocks")
            block_of[state]=i
    if set(block_of)!=set(states): raise ValueError("partition must cover every state")
    return {"state_to_block": {repr(s): block_of[s] for s in states},
            "block_count": len(partition),
            "state_count": len(states)}

def verify_certificate(states, observations, properties, transitions, partition, certificate):
    """Verify coverage, property/observation uniformity, transition congruence and minimality."""
    _validate(states, observations, properties, transitions)
    domain=set(states)
    block_of={}
    errors=[]
    for i, block in enumerate(partition):
        if not block: errors.append("empty block")
        for s in block:
            if s not in domain: errors.append(f"out-of-domain state: {s!r}")
            if s in block_of: errors.append(f"duplicate state: {s!r}")
            block_of[s]=i
    if set(block_of)!=domain: errors.append("partition does not cover state domain")
    expected={repr(s): block_of[s] for s in states if s in block_of}
    if certificate.get("state_to_block") != expected: errors.append("certificate mapping mismatch")
    if certificate.get("block_count") != len(partition): errors.append("certificate block count mismatch")
    if certificate.get("state_count") != len(states): errors.append("certificate state count mismatch")

    # Soundness/congruence: all members of a block have matching local signatures
    # against the proposed successor blocks.
    for block in partition:
        members=[s for s in block if s in domain]
        if not members: continue
        def local_signature(s):
            return (observations[s], tuple(properties[s]), frozenset(transitions[s].keys()),
                    tuple(sorted(((repr(a), None if nxt is None else block_of.get(nxt))
                                  for a,nxt in transitions[s].items()), key=lambda x:x[0])))
        if any(local_signature(s)!=local_signature(members[0]) for s in members[1:]):
            errors.append(f"block is not behaviorally/property homogeneous: {members!r}")

    # Independent minimality test: repeatedly refine the current partition by signatures.
    # If it splits, the submitted partition was too coarse. If the input partition was
    # already a stable refinement, it may still be over-split; compare with coarsest seed.
    groups=defaultdict(list)
    for s in states: groups[(observations[s],tuple(properties[s]))].append(s)
    refined=[frozenset(g) for g in groups.values()]
    while True:
        idx={s:i for i,b in enumerate(refined) for s in b}
        next_groups=[]
        for b in refined:
            buckets=defaultdict(list)
            for s in b:
                sig=(frozenset(transitions[s].keys()),
                     tuple(sorted(((repr(a),None if nxt is None else idx[nxt])
                                   for a,nxt in transitions[s].items()),key=lambda x:x[0])))
                buckets[sig].append(s)
            next_groups.extend(frozenset(g) for g in buckets.values())
        if frozenset(next_groups)==frozenset(refined): break
        refined=next_groups
    submitted=frozenset(frozenset(b) for b in partition)
    canonical=frozenset(refined)
    if submitted != canonical: errors.append("partition is not the canonical coarsest quotient")
    return {"valid": not errors, "sound": not any(e.startswith(("partition does not cover","duplicate state","out-of-domain state","block is not")) for e in errors),
            "minimal": submitted == canonical, "errors": errors,
            "canonical_block_count": len(canonical), "submitted_block_count": len(partition)}
