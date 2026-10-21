#!/usr/bin/env python3
"""
AgentProof — "Your AI agent says it worked. Prove it."

An open-source CLI that verifies agent-generated code changes against
explicit acceptance criteria. Checks the evidence instead of trusting
the completion message.

Usage:
    agentproof check [--criteria FILE] [--tests CMD] [--format json|markdown]
    agentproof init    # scaffold a .agentproof.yml in the current repo
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.0.0"


@dataclass
class CheckResult:
    name: str
    status: str  # "pass" | "fail" | "unknown"
    detail: str = ""
    duration_ms: int = 0


@dataclass
class ProofReport:
    repo: str
    branch: str
    commit: str
    timestamp: str
    checks: list = field(default_factory=list)

    @property
    def passed(self): return sum(1 for c in self.checks if c.status == "pass")
    @property
    def failed(self): return sum(1 for c in self.checks if c.status == "fail")
    @property
    def unknown(self): return sum(1 for c in self.checks if c.status == "unknown")
    @property
    def verdict(self):
        if self.failed: return "FAIL"
        if self.unknown: return "UNKNOWN"
        return "PASS"


def run(cmd, cwd=None, timeout=120):
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True,
                           text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"timed out after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


def git_info(cwd):
    code, branch, _ = run("git rev-parse --abbrev-ref HEAD", cwd)
    code2, commit, _ = run("git rev-parse --short HEAD", cwd)
    code3, repo, _ = run("git config --get remote.origin.url", cwd)
    return {
        "branch": branch if code == 0 else "unknown",
        "commit": commit if code2 == 0 else "unknown",
        "repo": repo if code3 == 0 else Path(cwd).name,
    }


def check_git_diff(cwd):
    """Verify there are actual changes to check."""
    import time
    start = time.time()
    code, out, err = run("git diff HEAD --stat", cwd)
    if code != 0:
        return CheckResult("git-diff", "unknown", f"could not read diff: {err}")
    files = [l for l in out.splitlines() if l.strip() and "file" in l.lower()]
    changed = len(out.strip().splitlines()) - (1 if files else 0)
    ms = int((time.time() - start) * 1000)
    if not out.strip():
        return CheckResult("git-diff", "unknown",
                           "no uncommitted changes vs HEAD — nothing to verify", ms)
    return CheckResult("git-diff", "pass",
                       f"{changed} file(s) changed vs HEAD", ms)


def check_tests(cmd, cwd):
    """Run the project's test command."""
    import time
    start = time.time()
    if not cmd:
        return CheckResult("tests", "unknown", "no test command configured")
    code, out, err = run(cmd, cwd, timeout=300)
    ms = int((time.time() - start) * 1000)
    combined = (out + "\n" + err).strip()
    tail = "\n".join(combined.splitlines()[-8:]) if combined else "(no output)"
    if code == 0:
        return CheckResult("tests", "pass", f"`{cmd}` exited 0\n{tail}", ms)
    return CheckResult("tests", "fail",
                       f"`{cmd}` exited {code}\n{tail}", ms)


def check_protected_files(cwd, patterns):
    """Ensure no protected paths were touched."""
    import time, fnmatch
    start = time.time()
    code, out, _ = run("git diff HEAD --name-only", cwd)
    if code != 0:
        return CheckResult("protected-files", "unknown", "could not list changed files")
    changed = out.splitlines()
    hits = [f for f in changed
            for p in patterns if fnmatch.fnmatch(f, p)]
    ms = int((time.time() - start) * 1000)
    if hits:
        return CheckResult("protected-files", "fail",
                           f"protected paths modified: {', '.join(hits)}", ms)
    return CheckResult("protected-files", "pass",
                       f"{len(changed)} changed file(s), none protected", ms)


def check_criteria_file(path, cwd):
    """Verify each acceptance criterion listed in the criteria file."""
    import time
    start = time.time()
    if not path or not Path(path).exists():
        return [CheckResult("criteria", "unknown",
                            "no criteria file — create one with `agentproof init`")]
    results = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # criterion format: <description> :: <shell check, exit 0 = pass>
        if "::" in line:
            desc, shell = [p.strip() for p in line.split("::", 1)]
            t0 = time.time()
            code, out, err = run(shell, cwd, timeout=60)
            ms = int((time.time() - t0) * 1000)
            status = "pass" if code == 0 else "fail"
            detail = out or err or f"exit {code}"
            results.append(CheckResult(f"criteria: {desc}", status, detail, ms))
        else:
            results.append(CheckResult(f"criteria: {line}", "unknown",
                                       "no check command (:: shell) given"))
    total_ms = int((time.time() - start) * 1000)
    if not results:
        results.append(CheckResult("criteria", "unknown",
                                   "criteria file is empty", total_ms))
    return results


def load_config(cwd):
    cfg = {"test_command": "", "criteria_file": "",
           "protected": [".env", "*.pem", "*.key", "credentials*"]}
    for name in (".agentproof.yml", ".agentproof.yaml", ".agentproof.json"):
        p = Path(cwd) / name
        if p.exists():
            try:
                if p.suffix == ".json":
                    cfg.update(json.loads(p.read_text()))
                else:  # minimal YAML: key: value lines
                    for line in p.read_text().splitlines():
                        if ":" in line and not line.strip().startswith("#"):
                            k, v = line.split(":", 1)
                            v = v.strip()
                            # Strip ONE matched pair of quotes only: a naive
                            # strip("'\"") would also eat a closing single
                            # quote nested inside double quotes (e.g.
                            # test_command: "python3 -c '...'"), corrupting it.
                            if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
                                v = v[1:-1]
                            k = k.strip()
                            if k == "protected":
                                cfg[k] = [x.strip() for x in v.split(",")]
                            else:
                                cfg[k] = v
            except Exception as e:
                print(f"warning: could not parse {name}: {e}", file=sys.stderr)
            break
    return cfg


def cmd_check(args):
    cwd = os.getcwd()
    cfg = load_config(cwd)
    test_cmd = args.tests or cfg.get("test_command", "")
    criteria = args.criteria or cfg.get("criteria_file", "")
    protected = cfg.get("protected", [])

    info = git_info(cwd)
    report = ProofReport(
        repo=info["repo"], branch=info["branch"], commit=info["commit"],
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    report.checks.append(check_git_diff(cwd))
    report.checks.append(check_protected_files(cwd, protected))
    report.checks.extend(check_criteria_file(criteria, cwd))
    report.checks.append(check_tests(test_cmd, cwd))

    if args.format == "json":
        payload = asdict(report)
        payload["tool"] = "agentproof"
        payload["version"] = VERSION
        payload["schema_version"] = 1
        payload["findings_summary"] = {
            "count": report.failed + report.unknown,
            "highest_severity": "HIGH" if report.failed else ("INFO" if report.unknown else "NONE"),
        }
        print(json.dumps(payload, indent=2))
    else:
        print_markdown(report)

    # Family exit-code contract (CONVENTIONS.md): 0 pass / 1 fail-or-unknown / 2 caller error
    sys.exit({"PASS": 0, "FAIL": 1, "UNKNOWN": 1}[report.verdict])


def print_markdown(r: ProofReport):
    icon = {"PASS": "✅", "FAIL": "❌", "UNKNOWN": "❓"}
    print(f"# AgentProof Report — {icon[r.verdict]} {r.verdict}\n")
    print(f"- **Repo:** {r.repo}\n- **Branch:** {r.branch}\n"
          f"- **Commit:** {r.commit}\n- **Time:** {r.timestamp}\n")
    print(f"**{r.passed} passed · {r.failed} failed · {r.unknown} unknown**\n")
    for c in r.checks:
        mark = {"pass": "✅", "fail": "❌", "unknown": "❓"}[c.status]
        print(f"## {mark} {c.name} ({c.status.upper()}, {c.duration_ms}ms)\n")
        if c.detail:
            print("```\n" + c.detail[:1500] + "\n```\n")


INIT_TEMPLATE = """# AgentProof config — "Your AI agent says it worked. Prove it."
# Each criterion: <description> :: <shell command; exit 0 = pass>
test_command: "python3 -m pytest tests/ -q"
criteria_file: ".agentproof.criteria"
protected: ".env,*.pem,*.key,credentials*,secrets*"
"""

CRITERIA_TEMPLATE = """# Acceptance criteria — one per line: <description> :: <check command>
# Example:
# login page renders :: python -c "assert 'login' in open('index.html').read().lower()"
# no TODO left in src :: sh -c "! grep -ri 'TODO' src/ 2>/dev/null"
"""


def cmd_init(args):
    cwd = Path.cwd()
    cfg_path = cwd / ".agentproof.yml"
    crit_path = cwd / ".agentproof.criteria"
    if cfg_path.exists() and not args.force:
        print(f"{cfg_path} exists — use --force to overwrite")
        return
    cfg_path.write_text(INIT_TEMPLATE)
    if not crit_path.exists():
        crit_path.write_text(CRITERIA_TEMPLATE)
    print(f"created {cfg_path} and {crit_path}")
    print("edit them, then run: agentproof check")


def main():
    ap = argparse.ArgumentParser(
        prog="agentproof",
        description="Verify agent-generated code. Your AI agent says it worked. Prove it.")
    ap.add_argument("--version", action="version", version=f"agentproof {VERSION}")
    ap.add_argument("--no-color", action="store_true",
                    help="disable color output (accepted; output is color-free, NO_COLOR is also honored)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", help="verify current changes")
    c.add_argument("--criteria", help="path to criteria file")
    c.add_argument("--tests", help="test command to run")
    c.add_argument("--format", choices=["markdown", "json"], default="markdown")
    c.set_defaults(fn=cmd_check)

    i = sub.add_parser("init", help="scaffold config in current repo")
    i.add_argument("--force", action="store_true")
    i.set_defaults(fn=cmd_init)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
