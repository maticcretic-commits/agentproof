# AgentProof ✅❌❓

**Your AI agent says it worked. Prove it.**

AI coding agents can write code, run commands, and confidently report that a task is complete. But did the tests pass? Did it touch files it shouldn't have? Did it actually do what you asked?

AgentProof checks the evidence instead of trusting the completion message.

```bash
npx agentproof check
# or
python src/agentproof.py check
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

Exit codes: `0` = PASS, `1` = FAIL, `2` = UNKNOWN. Drop it in GitHub Actions.

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

## Part of AgentForge

AgentProof is the first tool in the [AgentForge](https://github.com/maticcretic-commits) trust layer for AI agents:
- **AgentProof** — verify agent work (this repo)
- **[PromptRE](https://github.com/maticcretic-commits/promptre)** — reverse-engineer agent prompts
- **[AgentCI](https://github.com/maticcretic-commits/agentci)** — regression harness for agents
- **[SecretScan](https://github.com/maticcretic-commits/secretscan)** — scan agent outputs for leaked secrets
- **[CostLedger](https://github.com/maticcretic-commits/costledger)** — cost accounting for agent runs
- **[SchemaGuard](https://github.com/maticcretic-commits/schemaguard)** — validate agent outputs against their contracts
- **[SkillAudit](https://github.com/maticcretic-commits/skillaudit)** — audit agent skills for hidden instructions and quality
- **[PromptDiff](https://github.com/maticcretic-commits/promptdiff)** — diff prompt versions
- **[TraceTape](https://github.com/maticcretic-commits/tracetape)** — the canonical run tape

AgentProof checks what an agent *did*; PromptRE checks what it was *told*; AgentCI checks it still *works* after you change it; SecretScan checks that nothing *leaked*; CostLedger checks what it *cost*; SchemaGuard checks the output still *fits the contract*; SkillAudit checks the skill was *safe to install*; PromptDiff checks what the prompt change *changed*; TraceTape keeps the whole run on *tape*.

## License

MIT
