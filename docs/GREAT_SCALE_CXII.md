# Great Scale CXII — Fault-Domain Diversity

## Research question
CXI detects conflicting heads across signed observer reports, but a raw observer count can overstate evidence when identities share an operational failure domain. CXII adds a configurable minimum number of observers and declared fault domains.

## Rule
Let O be the set of unique observers whose receipts and checkpoints validate. Let d(o) be a configured domain label. The declared domain count is D = |{d(o): o in O and d(o) is configured}|. Evidence diversity meets the configured floor only if |O| >= k, D >= q, and every accepted observer has a non-empty domain label. Any detected same-log, same-size head conflict takes precedence and yields FORK_DETECTED.

## Statuses
- FORK_DETECTED: authenticated conflicting heads were observed.
- DIVERSITY_THRESHOLD_MET: observer and declared-domain floors are met and no fork was observed in the supplied evidence.
- INSUFFICIENT_DIVERSITY: required observer/domain coverage is missing.

## Scientific limits
Domain labels are configuration claims. They do not prove independent ownership, administration, networks, software, upstream data, or incentives. This rung improves declared diversity accounting; it does not infer a hidden dependency graph or estimate correlation from evidence. "No fork observed" is not proof of global consistency.

## Tests
Covers sufficient domains, concentrated domains, duplicate identities, missing labels, fork precedence, untrusted receipts, and invalid thresholds. Run:
`python -m unittest tests/test_cxii_fault_domain_diversity.py`

## Great Scale mapping
CX compares signed checkpoints; CXI gathers signed observer reports; CXII requires a minimum count of verified observers across declared fault domains. The next rung should test whether declared domains correspond to empirically independent evidence paths.
