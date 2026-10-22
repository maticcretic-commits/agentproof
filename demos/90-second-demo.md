# AgentProof — 90-second demo script (PREP ONLY — not published)

Status: launch prep for item 19. Record only when the launch is
approved; nothing here is public yet.

**Premise (one line, on camera):** "Your agent says it shipped the
login page. AgentProof checks — against the actual git diff."

**Setup (before recording):** a scratch git repo built from the
bundled CI-matrix pass fixture (exact commands in Beat 1). Terminal
at 120% font, dark theme. Total runtime ≈ 90 s.

---

### Beat 1 — The setup (0:00–0:15)

Narration: "An agent just 'finished' a task in this repo. It says
the login page works. Don't take its word for it."

On screen:

```bash
mkdir demo && cd demo
cp -r /path/to/agentproof/examples/ci-matrix/pass/. .
git init -q . && git add -A && git commit -qm scaffold
printf '<html><body>Login page v2</body></html>\n' > index.html   # the agent's change
```

### Beat 2 — The verdict (0:15–0:45)

Narration: "AgentProof verifies the work against four kinds of
evidence: what actually changed, whether protected files were
touched, the acceptance criteria, and the test suite."

```bash
$ agentproof check
# AgentProof Report — ✅ PASS
#
# **4 passed · 0 failed · 0 unknown**
#
# ## ✅ git-diff (PASS)          1 file(s) changed vs HEAD
# ## ✅ protected-files (PASS)   1 changed file(s), none protected
# ## ✅ criteria: login page renders (PASS)
# ## ✅ tests (PASS)             exited 0
```

(Real captured output, trimmed; full report names repo, branch and
commit. Exit code 0.)

### Beat 3 — The catch (0:45–1:15)

Narration: "Now the agent quietly swaps in a page that doesn't meet
the criteria. Same confidence in its summary. Watch the verdict."

```bash
$ cp ../fail/.agentproof.criteria .   # criteria the work must meet
$ agentproof check ; echo "exit=$?"
# AgentProof Report — ❌ FAIL
#
# **3 passed · 1 failed · 0 unknown**
#
# ## ❌ criteria: logout page renders (FAIL)
# exit=1
```

### Beat 4 — The close (1:15–1:30)

Narration: "Exit 1 fails the CI build — the agent's claim never
reaches a human as 'done'. One command, offline, no model call:
verify agent work before you ship it. AgentProof — part of the
AgentForge family."

On screen: `agentproof check --format json` piped to a CI step;
end card with the repo URL (added at launch, not before).
