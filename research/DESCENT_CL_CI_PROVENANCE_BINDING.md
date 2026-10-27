# Descent CL — A verification predicate must not trust its own premise

## Finding

CXLIX models pull-request CI evidence as a tuple, but the `candidate_matches` field is a supplied Boolean. The acceptance predicate checks that assertion rather than deriving candidate binding from the candidate's immutable identity and recorded parent commits. Therefore the model can accept a fabricated or mistaken match claim. This is a weakness in the abstract model, not evidence that GitHub Actions itself produced an incorrect run.

## Formal distinction

Let H be the PR head, B the target branch tip, M the tested candidate, W the workflow revision, and R the run identifier.

A weak predicate accepts an assertion:

`Accept_weak = ClaimedMatch(H,B,M) AND RunSuccess(R) AND TestsReachable(W)`

The stronger contract binds the candidate to its immutable inputs:

`Accept = (ObservedHead = H) AND (ObservedBase = B) AND (ObservedCandidate = M)`
`        AND (Parents(M) = (B,H)) AND (ObservedWorkflow = W)`
`        AND (RunId(R) != empty) AND (Conclusion(R) = success)`
`        AND TestsReachable(W)`

The exact candidate/parent convention must match the hosting provider's documented merge-candidate semantics; a head-only workflow may require a different candidate model. Parent metadata and run metadata must be obtained from an authoritative API or verified object, not copied from the claim being checked.

## Regression model

`test_great_scale_cl_provenance_binding.py` rejects:
- a changed base or candidate SHA;
- a candidate whose recorded parents do not match the expected base/head pair;
- a different workflow revision;
- a missing run ID, failed conclusion, or unreachable required tests.

This is a contract/model test. It does not query GitHub Actions, verify a live merge commit object, or establish that hosted CI passed.

## Great Scale mapping

- **State identity:** immutable head, base, candidate, and workflow SHAs.
- **Transition integrity:** candidate-parent relation binds the tested object to the exact inputs.
- **Evidence integrity:** run ID and conclusion are externally observed, not self-asserted.
- **Reachability:** required regression tests are included in the actual workflow command.
- **Freshness:** any head, base, candidate, or workflow change invalidates prior candidate-specific evidence.

## Synthesis

A proof checker must distinguish a proposition from evidence for that proposition. Adding more fields does not improve rigor if the critical fields are merely caller assertions. The next verification layer should obtain the tuple from the provider's authoritative run and commit metadata, verify object ancestry, and bind the conclusion to the exact run and workflow revision.

No full-suite execution, hosted workflow success, merge, deployment, or production verification is claimed here.
