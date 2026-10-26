# Descent CLVI — Repository-wide policy coverage

## Finding

CLV checked only `.github/workflows/ci.yml`. That protects the current CI file but does not constrain a second workflow added later. A new release, deployment, security, or scheduled workflow could reintroduce mutable action tags while the single-file policy stayed green.

CLVI expands the invariant across all top-level `.yml` and `.yaml` workflow files and fails closed if the workflow directory is absent or empty. A synthetic second-workflow fixture confirms the detector recognizes mutable references outside the original CI workflow.

## Mathematics

Let (F(W)) be all YAML workflow files in `.github/workflows`, and (U(f)) the action references parsed from file (f).

[
\operatorname{PinnedRepo}(W)=
(|F(W)|>0)\land
\bigwedge_{f\in F(W)}
\bigwedge_{(a,r)\in U(f)} SHA_{40}(r)
]

The fail-closed term (|F(W)|>0) prevents an absent directory or empty file set from being interpreted as proof of compliance.

## Integrated change

- Added `test_great_scale_clvi_workflow_coverage.py`.
- Added it to `npm run all`.
- The test enumerates both `.yml` and `.yaml` files, checks for the expected CI workflow, tests positive/negative references, and scans every actual workflow.

## Limitations

The scanner covers top-level workflow YAML files and the common single-line `- uses: owner/action@ref` syntax. It does not recursively inspect composite action definitions outside `.github/workflows`, remote reusable workflow references expressed in other syntactic forms, generated workflows, or external policy settings. It also checks SHA syntax, not whether a SHA is the intended or reviewed upstream action version.

Run:

```sh
python3 test_great_scale_clvi_workflow_coverage.py
npm run all
```

No clean-checkout aggregate run or hosted CI success is claimed until observed for the exact candidate SHA.
