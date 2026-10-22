#!/usr/bin/env bash
set -Eeuo pipefail

# Reproducible local fallback for the repository CI workflow.
# Run from any directory: bash scripts/verify-local.sh
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "Great Scale verification"
echo "repository_root=$ROOT"
echo "git_commit=$(git rev-parse HEAD 2>/dev/null || echo unavailable)"
echo "node_version=$(node --version)"
echo "npm_version=$(npm --version)"
echo "python_version=$(python3 --version 2>&1)"

node -e 'const major=Number(process.versions.node.split(".")[0]); if(major!==20) { console.error("Expected Node.js 20; got "+process.version); process.exit(2); }'
python3 - <<'PY'
import sys
if sys.version_info[:2] != (3, 11):
    print(f"Expected Python 3.11; got {sys.version.split()[0]}", file=sys.stderr)
    raise SystemExit(2)
PY

echo "::group::JavaScript regression suite"
npm test
echo "::endgroup::"

echo "::group::Python descent suite"
python3 test_descent.py
echo "::endgroup::"

echo "LOCAL_VERIFICATION=PASS"
echo "NOTE=Local success is not hosted CI evidence; record the exact commit and environment."
