# Great Scale CXIV — The Three-Boundary Theorem of Consistency

## Finding

A consistency result has at least three distinct boundaries:

1. **Pairwise observation boundary** — were all required comparisons among the supplied checkpoints actually observed?
2. **Population boundary** — does the supplied checkpoint set include every relevant observer/checkpoint in the claimed scope?
3. **Trust boundary** — do the signatures, signer identities, and fault-domain assertions satisfy the declared trust model?

Passing one boundary does not imply passing the others. In particular, complete pairwise coverage over a supplied set does not establish that the set itself is complete.

## Formal statement

Let $S$ be the finite set of supplied checkpoints, and let $R(a,b)$ be the comparator's relation. Define internal consistency:

$$
C_S \equiv \forall a,b\in S,\ a\ne b:\ R(a,b)\in\{\mathrm{SAME},\mathrm{ORDERED}\}.
$$

Let $U$ denote the full set of checkpoints relevant to a broader claim. A global claim would require:

$$
C_U \equiv \forall a,b\in U,\ a\ne b:\ R(a,b)\in\{\mathrm{SAME},\mathrm{ORDERED}\}.
$$

If $S$ is a strict subset of $U$, then $C_S$ does not entail $C_U$.

### Indistinguishability argument

Take any observed finite set $S$ whose pairwise relations are consistent. Consider two possible worlds:

- $W_1$: the relevant population is exactly $S$.
- $W_2$: the relevant population is $S\cup\{x\}$, where an unobserved checkpoint $x$ conflicts with one member of $S$.

The supplied evidence is identical in both worlds, but global consistency differs. Therefore, without an independently justified population-completeness assumption or a discovery/publication mechanism, global consistency is **not identifiable** from the supplied set alone.

This is a logical result about evidence scope, not a claim about any particular physical system.

## Great Scale map

| Layer | Object | Required gate | Safe conclusion |
|---|---|---|---|
| State | Signed checkpoint | Signature and schema valid | This record is authenticated under the configured key policy |
| Relation | Pair of checkpoints | Directional comparator | This pair has a classified relation |
| Graph | Observed comparison edges $E_{obs}$ | $E_{obs}=\binom{S}{2}$ | Pair coverage is complete within supplied set $S$ |
| Population | Supplied set $S$ versus relevant set $U$ | External completeness evidence | Scope completeness only if separately justified |
| Trust | Signer/key/domain policy | Explicit trust assumptions | Policy threshold met; independence is not implied |
| Conclusion | Certificate with scope | All applicable gates recorded | Bounded consistency claim, not universal truth |

For $n=|S|$, the required number of unordered pair comparisons is

$$
|E_*|=\binom{n}{2}=\frac{n(n-1)}{2}.
$$

Pair coverage is $\gamma_E=|E_{obs}|/|E_*|$ for $n\ge 2$. If $\gamma_E=1$, that proves only complete comparison coverage for $S$, not that $S=U$. For $n<2$, pair coverage is vacuous and must not be mistaken for meaningful multi-observer corroboration.

## Engineering consequence

A machine-readable consistency certificate should explicitly state:
- the exact checkpoint identifiers in scope;
- observed and expected pair counts, including missing pairs;
- the comparator/version and result for every pair;
- trusted signer/key policy and any caller-supplied domain metadata;
- the source and justification for population completeness, or the literal status `UNKNOWN`;
- timestamp/publication assumptions and limitations.

The existing CXII result already reports pair counts and missing pairs and warns that consistency applies only to the supplied set. CXIV formalizes why that scope warning is logically necessary; it does not change the comparator's runtime behavior.

## Tests and verification status

The executable invariant to test is: adding an unobserved conflicting checkpoint to the hypothetical universe must not change the classification of the supplied set, but it must invalidate any unsupported claim that the supplied-set result proves global consistency. This is a model-level counterexample, not a claim that the hidden checkpoint was observed.

Current CI for PR #32 has failed before exposing any job steps (runner ID 0, empty step list); logs are unavailable through the current connector. Therefore, this document is integrated as a specification only. It does not assert that the repository's test suite has passed.

## Scientific limits

This theorem does not establish that a conflict exists, that any signer is malicious, or that the configured keys correspond to independent people or infrastructure. It establishes a narrower epistemic limit: finite observations cannot certify an unobserved population without additional assumptions or evidence.
