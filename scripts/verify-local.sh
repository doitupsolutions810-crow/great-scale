#!/usr/bin/env bash
set -Eeuo pipefail

# Canonical local/hosted verification entry point.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

VERIFY_JS_STATUS=not_run
VERIFY_PY_STATUS=not_run
VERIFY_EXIT_STATUS=running
VERIFY_COMMIT="$(git rev-parse HEAD 2>/dev/null || echo unavailable)"
VERIFY_NODE="$(node --version 2>&1 || echo unavailable)"
VERIFY_NPM="$(npm --version 2>&1 || echo unavailable)"
VERIFY_PYTHON="$(python3 --version 2>&1 || echo unavailable)"
VERIFY_RECEIPT="${RUNNER_TEMP:-${TMPDIR:-/tmp}}/great-scale-verification-receipt.json"
export VERIFY_JS_STATUS VERIFY_PY_STATUS VERIFY_EXIT_STATUS VERIFY_COMMIT VERIFY_NODE VERIFY_NPM VERIFY_PYTHON VERIFY_RECEIPT

write_receipt() {
  local exit_code=$?
  if [ "$exit_code" -eq 0 ]; then VERIFY_EXIT_STATUS=passed; else VERIFY_EXIT_STATUS=failed; fi
  export VERIFY_JS_STATUS VERIFY_PY_STATUS VERIFY_EXIT_STATUS VERIFY_COMMIT VERIFY_NODE VERIFY_NPM VERIFY_PYTHON VERIFY_RECEIPT
  python3 - <<'PY'
import json, os, datetime
record = {
  "schema": "great-scale.verification-receipt/v1",
  "commit": os.environ.get("VERIFY_COMMIT", "unavailable"),
  "node": os.environ.get("VERIFY_NODE", "unavailable"),
  "npm": os.environ.get("VERIFY_NPM", "unavailable"),
  "python": os.environ.get("VERIFY_PYTHON", "unavailable"),
  "javascript_suite": os.environ.get("VERIFY_JS_STATUS", "not_run"),
  "python_descent_suite": os.environ.get("VERIFY_PY_STATUS", "not_run"),
  "overall": os.environ.get("VERIFY_EXIT_STATUS", "unknown"),
  "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "github_run_id": os.environ.get("GITHUB_RUN_ID"),
  "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
  "github_repository": os.environ.get("GITHUB_REPOSITORY"),
  "github_sha": os.environ.get("GITHUB_SHA"),
  "runner_name": os.environ.get("RUNNER_NAME"),
}
with open(os.environ["VERIFY_RECEIPT"], "w", encoding="utf-8") as f:
    json.dump(record, f, indent=2, sort_keys=True)
    f.write("\n")
summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    with open(summary, "a", encoding="utf-8") as f:
        f.write("## Great Scale verification receipt\n\n")
        f.write(f"- Commit: `{record['commit']}`\n")
        f.write(f"- JavaScript suite: **{record['javascript_suite']}**\n")
        f.write(f"- Python descent suite: **{record['python_descent_suite']}**\n")
        f.write(f"- Overall: **{record['overall']}**\n")
        f.write(f"- Receipt: `{os.environ['VERIFY_RECEIPT']}`\n")
PY
  echo "verification_receipt=$VERIFY_RECEIPT"
  echo "verification_status=$VERIFY_EXIT_STATUS"
}
trap write_receipt EXIT

echo "Great Scale verification"
echo "repository_root=$ROOT"
echo "commit=$VERIFY_COMMIT"
echo "node=$VERIFY_NODE"
echo "npm=$VERIFY_NPM"
echo "python=$VERIFY_PYTHON"

node -e 'const major=Number(process.versions.node.split(".")[0]); if(major!==20) { console.error("Expected Node.js 20; got "+process.version); process.exit(2); }'
python3 - <<'PY'
import sys
if sys.version_info[:2] != (3, 11):
    print(f"Expected Python 3.11; got {sys.version.split()[0]}", file=sys.stderr)
    raise SystemExit(2)
PY

echo "::group::JavaScript regression suite"
if npm test; then VERIFY_JS_STATUS=passed; else VERIFY_JS_STATUS=failed; exit 1; fi
export VERIFY_JS_STATUS
echo "::endgroup::"

echo "::group::Python descent suite"
if python3 test_descent.py; then VERIFY_PY_STATUS=passed; else VERIFY_PY_STATUS=failed; exit 1; fi
export VERIFY_PY_STATUS
echo "::endgroup::"

echo "LOCAL_VERIFICATION=PASS"
echo "NOTE=Receipt binds outcomes to the commit/runtime metadata; it does not by itself prove test correctness or hosted execution."
