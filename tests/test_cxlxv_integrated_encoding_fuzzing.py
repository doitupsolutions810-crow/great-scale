from itertools import product
from cxlxiv_canonical_typed_encoding import canonical_encode, UnsupportedLabel
from cxlxii_quotient_certificate import make_certificate, verify_certificate

def oracle(states,obs,props,trans):
    p=list(dict.fromkeys(frozenset(s for s in states if (obs[s],tuple(props[s]))==(obs[t],tuple(props[t]))) for t in states))
    while True:
        idx={s:i for i,b in enumerate(p) for s in b}; buckets={}
        for s in states:
            edges=tuple(sorted((canonical_encode(a),None if n is None else idx[n]) for a,n in trans[s].items()))
            buckets.setdefault((obs[s],tuple(props[s]),edges),set()).add(s)
        q=[frozenset(v) for v in buckets.values()]
        if frozenset(q)==frozenset(p): return frozenset(q)
        p=q

def test_type_tagging_distinguishes_bool_int_and_string():
    assert len({canonical_encode(True),canonical_encode(1),canonical_encode("1"),canonical_encode((1,))})==4

def test_unsupported_labels_fail_closed():
    try: canonical_encode(object())
    except UnsupportedLabel: return
    assert False,"unsupported label accepted"

def test_v2_certificate_canonical_keys():
    states=[1,"1"]; obs={s:0 for s in states}; props={s:() for s in states}; trans={s:{} for s in states}; part=[{s} for s in states]
    cert=make_certificate(states,obs,props,trans,part)
    assert cert["schema"]=="gs-quotient-cert-v2" and len(cert["state_to_block"])==2
    assert verify_certificate(states,obs,props,trans,part,cert)["valid"]

def test_exhaustive_two_state_differential():
    states=(0,1); props={s:() for s in states}
    for bits in product((0,1),repeat=2):
      obs=dict(zip(states,bits))
      for e0,e1 in product((None,0,1),repeat=2):
        trans={0:({ "go":e0} if e0 is not None else {}),1:({"go":e1} if e1 is not None else {})}
        expected=oracle(states,obs,props,trans); part=[set(b) for b in expected]
        cert=make_certificate(states,obs,props,trans,part); result=verify_certificate(states,obs,props,trans,part,cert)
        assert result["valid"],(obs,trans,result)
        assert result["canonical_block_count"]==len(expected)

def test_order_metamorphism_and_version_tamper():
    states=[0,1]; obs={0:0,1:0}; props={s:() for s in states}; trans={0:{"b":1,"a":None},1:{"a":None,"b":0}}; part=[{0,1}]
    cert=make_certificate(states,obs,props,trans,part)
    rev={s:dict(reversed(list(trans[s].items()))) for s in states[::-1]}
    cert2=make_certificate(states[::-1],obs,props,rev,part)
    assert cert["state_to_block"]==cert2["state_to_block"]
    cert["encoding_version"]="legacy"
    assert not verify_certificate(states,obs,props,trans,part,cert)["valid"]
