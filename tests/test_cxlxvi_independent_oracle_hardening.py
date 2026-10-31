"""CXLXVI: pairwise-relation oracle and adversarial certificate mutations."""
from itertools import product
from cxlxiv_canonical_typed_encoding import canonical_encode
from cxlxii_quotient_certificate import make_certificate, verify_certificate

def pairwise_equivalence(states, observations, properties, transitions):
    # Independent greatest-fixed-point relation elimination, not block refinement.
    relation={(a,b) for a in states for b in states
              if observations[a]==observations[b] and tuple(properties[a])==tuple(properties[b])
              and set(transitions[a])==set(transitions[b])}
    changed=True
    while changed:
        changed=False
        for a,b in tuple(relation):
            for action in transitions[a]:
                x,y=transitions[a][action],transitions[b][action]
                if (x is None)!=(y is None) or (x is not None and (x,y) not in relation):
                    relation.remove((a,b)); changed=True; break
    # Equivalence classes induced by the final bisimulation-like relation.
    classes=[]; unseen=set(states)
    while unseen:
        s=next(iter(unseen))
        block={t for t in unseen if (s,t) in relation and (t,s) in relation}
        if not block: block={s}
        classes.append(frozenset(block)); unseen-=block
    return frozenset(classes)

def model(states, obs_bits, edges):
    obs=dict(zip(states,obs_bits)); props={s:() for s in states}
    trans={s:({ "go": edges[i]} if edges[i] is not ... else {}) for i,s in enumerate(states)}
    return obs,props,trans

def test_pairwise_oracle_matches_verifier_exhaustive_two_state_space():
    states=(0,1)
    for obits in product((0,1),repeat=2):
      for edges in product((...,None,0,1),repeat=2):
        obs,props,trans=model(states,obits,edges)
        expected=pairwise_equivalence(states,obs,props,trans)
        partition=[set(b) for b in expected]
        cert=make_certificate(states,obs,props,trans,partition)
        result=verify_certificate(states,obs,props,trans,partition,cert)
        assert result["valid"],(obits,edges,result)
        assert result["canonical_block_count"]==len(expected)

def test_mapping_mutation_is_rejected():
    states=[0,1]; obs={0:0,1:1}; props={s:() for s in states}; trans={s:{} for s in states}
    part=[{0},{1}]; cert=make_certificate(states,obs,props,trans,part)
    cert["state_to_block"][canonical_encode(0)]=99
    result=verify_certificate(states,obs,props,trans,part,cert)
    assert not result["valid"] and "certificate mapping mismatch" in result["errors"]

def test_overmerged_partition_rejected():
    states=[0,1]; obs={0:0,1:1}; props={s:() for s in states}; trans={s:{} for s in states}
    part=[{0,1}]; cert=make_certificate(states,obs,props,trans,part)
    result=verify_certificate(states,obs,props,trans,part,cert)
    assert not result["valid"] and not result["minimal"]

def test_successor_mutation_invalidates_old_certificate():
    states=[0,1,2]; obs={s:0 for s in states}; props={s:() for s in states}
    trans={0:{"go":1},1:{"go":1},2:{"go":2}}; part=[{0,1},{2}]
    cert=make_certificate(states,obs,props,trans,part)
    assert verify_certificate(states,obs,props,trans,part,cert)["valid"]
    mutated={0:{"go":2},1:{"go":1},2:{"go":2}}
    result=verify_certificate(states,obs,props,mutated,part,cert)
    assert not result["valid"]

def test_action_set_mutation_invalidates_certificate():
    states=[0,1]; obs={s:0 for s in states}; props={s:() for s in states}
    trans={0:{"a":0},1:{"a":1}}; part=[{0,1}]
    cert=make_certificate(states,obs,props,trans,part)
    mutated={0:{"a":0},1:{"b":1}}
    assert not verify_certificate(states,obs,props,mutated,part,cert)["valid"]
