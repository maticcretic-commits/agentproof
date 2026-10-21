#!/usr/bin/env bash
# Run one AgentProof CI-matrix case in a temp git repo.
# Usage: run-case.sh <pass|fail>
# Exit code = agentproof's own exit code (contract-pinned).
# The caller (CI or tests) asserts the expected code.
#
# AGENTPROOF_CMD may point at the tool invocation (e.g. a full
# "python3 /path/src/agentproof.py" string). Default: the installed
# `agentproof` console script, falling back to this repo's src/.
set -u

CASE="${1:?usage: run-case.sh <pass|fail>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ -n "${AGENTPROOF_CMD:-}" ]; then
    AP=($AGENTPROOF_CMD)
elif command -v agentproof >/dev/null 2>&1; then
    AP=(agentproof)
else
    AP=(python3 "$REPO_ROOT/src/agentproof.py")
fi

if [ "$CASE" != "pass" ] && [ "$CASE" != "fail" ]; then
    echo "unknown case: $CASE (want pass|fail)" >&2
    exit 2
fi

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
cp -r "$SCRIPT_DIR/$CASE/." "$WORK/"
cd "$WORK" || exit 2
git init -q .
git config user.email "ci-matrix@example.org"
git config user.name "AgentForge CI matrix"
git add -A
git commit -qm "scaffold"
# The "agent change": ship a login page. Uncommitted = real git-diff evidence.
printf '<html><body>Login page v2</body></html>\n' > index.html
"${AP[@]}" check --format json
