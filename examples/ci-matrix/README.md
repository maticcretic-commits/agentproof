# AgentProof CI matrix

Deterministic CI fixtures for the agentproof caller workflow
(`.github/workflows/verify.yml`). The workflow does NOT run
`agentproof check` on a clean checkout — with no uncommitted changes the
tool *correctly* reports UNKNOWN (exit 1) and every build would go red.

Instead, `run-case.sh <pass|fail>` scaffolds a temp git repo from the
fixture, commits the baseline, then applies "the agent's change" (an
uncommitted edit to `index.html` — real git-diff evidence) and runs
`agentproof check --format json`:

- `pass/` — the criterion asserts `'login'` is in `index.html` (it is
  after the change): verdict PASS → **exit 0**.
- `fail/` — the criterion asserts `'logout'` is in `index.html` (it is
  not): verdict FAIL → **exit 1**.

Both cases share the same baseline, the same test command, and the same
evidence shape — the only variable is whether the criterion's expectation
holds. The expected exit codes are pinned by
`tests/test_ci_matrix.py`, so the matrix can't silently rot.
