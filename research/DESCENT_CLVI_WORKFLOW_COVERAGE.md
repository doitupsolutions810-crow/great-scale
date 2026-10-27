# Descent CLVI — Repository-wide policy coverage

## Finding

CLV checked only `.github/workflows/ci.yml`. That protects the current CI file but does not constrain a second workflow added later. A release, deployment, security, or scheduled workflow could reintroduce mutable action tags while the single-file policy stayed green.

CLVI scans every top-level `.yml` and `.yaml` file in `.github/workflows` and fails closed if the directory is absent or empty. Its mutation fixture places an unpinned action in a second workflow using the named-step YAML form, demonstrating that coverage is not limited to the original CI file or the `- uses:` shorthand.

## Mathematics

Let (F(W)) be the set of YAML workflow files in `.github/workflows`, and (U(f)) the action references parsed from file (f). Let (SHA_{40}(r)) mean exactly 40 lowercase hexadecimal characters.

```text
PinnedRepo(W) =
    (|F(W)| > 0)
    AND for every f in F(W), every (action, ref) in U(f): SHA40(ref)
```

The nonempty-set requirement prevents an absent directory or empty file set from being interpreted as proof of compliance.

## Integrated change

- Added `test_great_scale_clvi_workflow_coverage.py`.
- Added it to `npm run all`.
- The test enumerates both `.yml` and `.yaml` workflow files, checks for `ci.yml`, tests pinned and mutable references, and scans every discovered workflow.
- The regex detects both `- uses: owner/action@ref` and a `uses:` key on a separately indented named step.

## Limitations

The scanner covers top-level workflow YAML files only. It does not recursively inspect composite action definitions outside `.github/workflows`, external policy settings, generated workflows, or every possible YAML alias/templating pattern. It checks SHA syntax, not whether a SHA is the intended or reviewed upstream action version. Reusable workflows expressed with a normal `uses: owner/repo/.github/workflows/file.yml@ref` key are covered by the same syntax check when they appear as a step/job key matching the scanner pattern; their remote contents are not recursively fetched.

Run:

```sh
python3 test_great_scale_clvi_workflow_coverage.py
npm run all
```

The isolated copied-harness run passed 4/4 assertions. This is not a clean checkout, a full aggregate run, or hosted CI evidence for the PR head.
