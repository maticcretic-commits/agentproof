# AgentProof ✅❌❓

**Your coding agent says “done.” The login page doesn't render, the tests were never run, and it touched a file it shouldn't have.**

AgentProof checks the evidence instead of trusting the completion message: real git changes, untouched protected files, your acceptance criteria, and the project's own test suite — each reported pass, fail, or unknown, never a guess.

*Part of **AgentForge** — verify AI-agent work before you ship it.*
*The family: [AgentProof](https://github.com/maticcretic-commits/agentproof) · [PromptRE](https://github.com/maticcretic-commits/promptre) · [AgentCI](https://github.com/maticcretic-commits/agentci) · [SecretScan](https://github.com/maticcretic-commits/secretscan) · [CostLedger](https://github.com/maticcretic-commits/costledger) · [SchemaGuard](https://github.com/maticcretic-commits/schemaguard) · [SkillAudit](https://github.com/maticcretic-commits/skillaudit) · [PromptDiff](https://github.com/maticcretic-commits/promptdiff) · [TraceTape](https://github.com/maticcretic-commits/tracetape) · [PromptLint](https://github.com/maticcretic-commits/promptlint) · [ClaimCheck](https://github.com/maticcretic-commits/claimcheck) · [TrustBadge](https://github.com/maticcretic-commits/trustbadge)*

```bash
$ agentproof check
```

```
# AgentProof Report — ❌ FAIL

**3 passed · 1 failed · 0 unknown**

## ✅ git-diff (PASS)
1 file(s) changed vs HEAD

## ✅ protected-files (PASS)
1 changed file(s), none protected

## ❌ criteria: login page renders (FAIL)
AssertionError

## ✅ tests (PASS)
`python3 -m pytest tests/ -q` exited 0
1 passed in 0.01s
```

*Exit code 1 — one criterion failed. Real run against a demo repo whose agent claimed the login page was finished (report trimmed). The agent said “done”; the page disagrees.*

## Install

```bash
pipx install git+https://github.com/maticcretic-commits/agentproof
# or, into the current environment:
pip install git+https://github.com/maticcretic-commits/agentproof
```

Then run it as `agentproof …` (Python 3.9+, no dependencies — stdlib only).
PyPI release planned; until then, the git URL above is the install path.

From source — it is a single file, so no install is needed at all:

```bash
git clone https://github.com/maticcretic-commits/agentproof
cd agentproof
python src/agentproof.py …
```

## What it checks

| Check | What it verifies |
|-------|-----------------|
| **git-diff** | Are there actual changes to verify? |
| **protected-files** | Did the agent touch `.env`, keys, credentials? |
| **criteria** | Does each acceptance criterion pass its shell check? |
| **tests** | Does the project's test suite pass? |

Each check returns **pass** ✅, **fail** ❌, or **unknown** ❓ — never a guess.

## Quick start

```bash
# In your repo:
agentproof init          # scaffold .agentproof.yml + .agentproof.criteria

# Edit .agentproof.criteria with your acceptance criteria:
#   login page renders :: python -c "assert 'login' in open('index.html').read().lower()"
#   no TODO left :: sh -c "! grep -ri 'TODO' src/ 2>/dev/null"

agentproof check         # verify the agent's work
agentproof check --format json   # machine-readable for CI
```

Exit codes: `0` = PASS, `1` = FAIL or UNKNOWN (a check that could
not verify counts as not passing, never as a silent pass), `2` = caller
error. Drop it in GitHub Actions.

## Example output

```
# AgentProof Report — ❌ FAIL

- **Repo:** my-app
- **Branch:** feature/agent-task
- **Commit:** a1b2c3d

**2 passed · 1 failed · 0 unknown**

## ✅ git-diff (PASS)
1 file(s) changed vs HEAD

## ✅ protected-files (PASS)
1 changed file(s), none protected

## ❌ criteria: login page renders (FAIL)
AssertionError: 'login' not in page

## ✅ tests (PASS)
`pytest -q` exited 0
```

## Why

The agent said "done." The login page doesn't render. AgentProof caught it in 3 seconds.

## Limitations

- AgentProof verifies evidence, not intent: a green report means the checks
  you wrote passed — it cannot judge whether the change is the *right* change.
- Criteria are shell commands you supply; a weak criterion passes weak work.
- With no git history or an empty criteria file, checks report UNKNOWN —
  and UNKNOWN counts as not passing (exit 1), never as a silent pass.

## Exit codes & JSON output

All AgentForge tools share one contract (full text in
[CONVENTIONS.md](CONVENTIONS.md)):

| Code | Meaning |
|------|---------|
| `0` | Clean / PASS — no findings at or above the tool's fail threshold |
| `1` | Findings / FAIL — the tool ran fine; the answer is “no” |
| `2` | Caller error — bad arguments, missing or unreadable input |
| `3` | Environment error — the tool itself could not run |

On a caller error the tool also prints one JSON line to stderr:
`{"error": {"code": "file_not_found", "message": "no such file: x"}}`.

JSON output (`--format json`) always carries the family envelope —
`{"tool": "agentproof", "version": "1.0.0", "schema_version": 1}` — alongside
the tool's own payload keys, unchanged.

## Part of AgentForge

AgentProof is one of the 12 tools in the [AgentForge](https://github.com/maticcretic-commits) family — offline, stdlib-only tools to **verify AI-agent work before you ship it**:
- **AgentProof** — verify agent work (this repo)
- **[PromptRE](https://github.com/maticcretic-commits/promptre)** — reverse-engineer agent prompts
- **[AgentCI](https://github.com/maticcretic-commits/agentci)** — regression harness for agents
- **[SecretScan](https://github.com/maticcretic-commits/secretscan)** — scan agent outputs for leaked secrets
- **[CostLedger](https://github.com/maticcretic-commits/costledger)** — cost accounting for agent runs
- **[SchemaGuard](https://github.com/maticcretic-commits/schemaguard)** — validate agent outputs against their contracts
- **[SkillAudit](https://github.com/maticcretic-commits/skillaudit)** — audit agent skills for hidden instructions and quality
- **[PromptDiff](https://github.com/maticcretic-commits/promptdiff)** — diff prompt versions
- **[TraceTape](https://github.com/maticcretic-commits/tracetape)** — the canonical run tape
- **[PromptLint](https://github.com/maticcretic-commits/promptlint)** — lint prompts for quality defects
- **[ClaimCheck](https://github.com/maticcretic-commits/claimcheck)** — audit agent reports against their evidence
- **[TrustBadge](https://github.com/maticcretic-commits/trustbadge)** — one trust score and badge for the whole family

AgentProof checks what an agent *did*; PromptRE checks what it was *told*; AgentCI checks it still *works* after you change it; SecretScan checks that nothing *leaked*; CostLedger checks what it *cost*; SchemaGuard checks the output still *fits the contract*; SkillAudit checks the skill was *safe to install*; PromptDiff checks what the prompt change *changed*; TraceTape keeps the whole run on *tape*; PromptLint keeps the prompt itself *linted clean*; ClaimCheck makes sure every claim is *backed*; TrustBadge puts the family's score *on one badge*.

## License

MIT
