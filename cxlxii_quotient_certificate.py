from __future__ import annotations
from collections import defaultdict
from typing import Mapping
from cxlxiv_canonical_typed_encoding import canonical_encode

def _validate(states, observations, properties, transitions):
    # Check before constructing a set/dict: Python considers True == 1 and gives
    # them equal hashes, even though the typed encoder intentionally distinguishes them.
    ids=[canonical_encode(s) for s in states]
    if len(set(ids))!=len(ids): raise ValueError("canonical state identities must be unique")
    for i, left in enumerate(states):
        for j in range(i + 1, len(states)):
            right = states[j]
            if left == right and ids[i] != ids[j]:
                raise ValueError(
                    "Python equality/hash collision between distinct canonical state labels; "
                    "use distinct external canonical IDs as model states"
                )
    domain=set(states)
    if len(domain)!=len(states): raise ValueError("states must be unique")
    if set(observations)!=domain or set(properties)!=domain or set(transitions)!=domain: raise ValueError("maps must cover exactly the state domain")
    for state,edges in transitions.items():
        if not isinstance(edges,Mapping): raise ValueError("each transition entry must be a mapping")
        keys=[canonical_encode(a) for a in edges]
        if len(set(keys))!=len(keys): raise ValueError("canonical action identities must be unique within a state")
        for nxt in edges.values():
            if nxt is not None and nxt not in domain: raise ValueError("successor outside state domain")

def _edge_sig(edges, block_of):
    return (tuple(sorted(canonical_encode(a) for a in edges)),
            tuple(sorted(((canonical_encode(a),None if nxt is None else block_of.get(nxt)) for a,nxt in edges.items()),key=lambda x:x[0])))

def make_certificate(states,observations,properties,transitions,partition):
    _validate(states,observations,properties,transitions)
    block_of={}
    for i,block in enumerate(partition):
        for state in block:
            if state in block_of: raise ValueError("state appears in multiple blocks")
            block_of[state]=i
    if set(block_of)!=set(states): raise ValueError("partition must cover every state")
    return {"schema":"gs-quotient-cert-v2","encoding_version":"gs-typed-v1","state_to_block":{canonical_encode(s):block_of[s] for s in states},"block_count":len(partition),"state_count":len(states)}

def verify_certificate(states,observations,properties,transitions,partition,certificate):
    _validate(states,observations,properties,transitions)
    domain=set(states); block_of={}; errors=[]
    if certificate.get("schema")!="gs-quotient-cert-v2": errors.append("certificate schema mismatch")
    if certificate.get("encoding_version")!="gs-typed-v1": errors.append("encoding version mismatch")
    for i,block in enumerate(partition):
        if not block: errors.append("empty block")
        for s in block:
            if s not in domain: errors.append(f"out-of-domain state: {s!r}")
            if s in block_of: errors.append(f"duplicate state: {s!r}")
            block_of[s]=i
    if set(block_of)!=domain: errors.append("partition does not cover state domain")
    expected={canonical_encode(s):block_of[s] for s in states if s in block_of}
    if certificate.get("state_to_block")!=expected: errors.append("certificate mapping mismatch")
    if certificate.get("block_count")!=len(partition): errors.append("certificate block count mismatch")
    if certificate.get("state_count")!=len(states): errors.append("certificate state count mismatch")
    for block in partition:
        members=[s for s in block if s in domain]
        if members and any((observations[s],tuple(properties[s]),_edge_sig(transitions[s],block_of))!=(observations[members[0]],tuple(properties[members[0]]),_edge_sig(transitions[members[0]],block_of)) for s in members[1:]):
            errors.append(f"block is not behaviorally/property homogeneous: {members!r}")
    groups=defaultdict(list)
    for s in states: groups[(observations[s],tuple(properties[s]))].append(s)
    refined=[frozenset(g) for g in groups.values()]
    while True:
        idx={s:i for i,b in enumerate(refined) for s in b}; nxt_groups=[]
        for b in refined:
            buckets=defaultdict(list)
            for s in b: buckets[_edge_sig(transitions[s],idx)].append(s)
            nxt_groups.extend(frozenset(g) for g in buckets.values())
        if frozenset(nxt_groups)==frozenset(refined): break
        refined=nxt_groups
    submitted=frozenset(frozenset(b) for b in partition); canonical=frozenset(refined)
    if submitted!=canonical: errors.append("partition is not the canonical coarsest quotient")
    return {"valid":not errors,"sound":not any(e.startswith(("partition does not cover","duplicate state","out-of-domain state","block is not")) for e in errors),"minimal":submitted==canonical,"errors":errors,"canonical_block_count":len(canonical),"submitted_block_count":len(partition)}
