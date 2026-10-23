# Great Scale CXVII — Evidence Scope Identity

## Finding

A declared count and a Boolean `scope_complete` do not identify the population to which completeness applies. CXVI correctly gates certification on caller-reported completeness, but the certificate does not itself bind that claim to a canonical population manifest. CXVII adds a content-addressed scope manifest and compares observed evidence IDs against that exact declaration.

## Mathematical object

Let the declared evidence set be (M = \{m_1,\ldots,m_N\}), and the observed set be (O = \{o_1,\ldots,o_k\}). The manifest binds:

[
\mathcal{M}=(s,\operatorname{sort}(M),N,p,v,a)
]

where (s) is scope identity, (p) is policy identity, (v) is policy version, and (a) is an authority reference. Its digest is:

[
h_M=\operatorname{SHA256}(\operatorname{CanonicalJSON}(\mathcal{M})).
]

The comparison has three valid outcomes:

- (O=M): `EXACT_MANIFEST_MATCH`
- (M\setminus O\ne\varnothing) and (O\subseteq M): `PARTIAL_SCOPE`
- (O\setminus M\ne\varnothing): `SCOPE_MISMATCH`

Malformed, altered, or digest-inconsistent manifests produce `INVALID_MANIFEST`.

## CXVII invariant: identity before completeness

[
\operatorname{EXACT\_MANIFEST\_MATCH}(O,M)
\Rightarrow O=M
]

This proves equality of the observed ID set and the manifest's declared ID set—not that the manifest lists every record that exists in the world. The manifest authority, evidence-ID semantics, and population enumeration process still require independent trust and validation. A digest detects modification relative to a known digest; it does not authenticate who created the manifest.

## Why this is a deeper result

The evidence state is not a scalar confidence value. It is a structured tuple:

[
E=(\text{state},\text{lineage},\text{authenticity},\text{scope identity},\text{scope match}).
]

Agreement can be certified only after each required dimension is separately checked. An exact set match cannot repair an observed fork; a valid signature cannot prove that the declared manifest is complete; and a complete manifest cannot make an incomparable lineage comparable.

## Repository boundary review

- Great Scale checkpoint comparison verifies Ed25519 signatures against supplied trusted keys and preserves `INCOMPARABLE`; the observer-view layer explicitly scopes its conclusion to supplied checkpoints.
- Partial-observation logic correctly distinguishes missing pair comparisons from agreement and lets observed forks dominate missing comparisons.
- CXVI's `scope_complete` and `authenticity_status` are inputs to a classifier, not independently established facts. Its signer count is also caller-provided; it does not verify signer identities.
- Living Intermediate Control Plane's operational evidence selection is not cryptographic provenance. TrainLLM's proposal/approval/simulation workflow and CycleKernal's audit/monitoring concepts have not yet been shown to share a compatible, trusted evidence-manifest contract.

Therefore CXVII is added as a standalone Great Scale contract. No other repository is changed until an actual producer-to-consumer schema and authority chain can be mapped without conflating availability with trust.

## Test

```bash
PYTHONPATH=. python tests/test_evidence_scope_binding.py -v
```

The ten tests cover exact set equality, missing and extra IDs, canonical ordering, tampering, count integrity, duplicate/empty populations, policy-version binding, and invalid observations.

## Limits

This is an engineering invariant over declared identifiers, not proof of a real-world population's completeness, key custody, trusted time, scientific validity, or production deployment.
