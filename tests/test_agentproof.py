"""Tests for AgentProof core checks."""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from agentproof import (check_git_diff, check_protected_files,
                        check_criteria_file, check_tests)


def make_repo():
    d = tempfile.mkdtemp()
    Path(d, "README.md").write_text("# test\n")
    for cmd in ["git init -q", "git config user.email t@t.t",
                "git config user.name t", "git add -A",
                "git commit -qm init"]:
        subprocess.run(cmd, shell=True, cwd=d, capture_output=True)
    return Path(d)


def test_no_changes_is_unknown():
    repo = make_repo()
    r = check_git_diff(str(repo))
    assert r.status == "unknown", r


def test_changes_detected():
    repo = make_repo()
    (repo / "hello.py").write_text("print('hi')\n")
    subprocess.run("git add -A", shell=True, cwd=repo, capture_output=True)
    r = check_git_diff(str(repo))
    assert r.status == "pass", r
    assert "1 file" in r.detail


def test_protected_file_fail():
    repo = make_repo()
    (repo / ".env").write_text("SECRET=1\n")
    subprocess.run("git add -A", shell=True, cwd=repo, capture_output=True)
    r = check_protected_files(str(repo), [".env"])
    assert r.status == "fail", r
    assert ".env" in r.detail


def test_protected_file_pass():
    repo = make_repo()
    (repo / "app.py").write_text("x=1\n")
    subprocess.run("git add -A", shell=True, cwd=repo, capture_output=True)
    r = check_protected_files(str(repo), [".env"])
    assert r.status == "pass", r


def test_criteria_pass_fail():
    repo = make_repo()
    crit = repo / "c.txt"
    crit.write_text("always true :: true\n\nalways false :: false\n")
    results = check_criteria_file(str(crit), str(repo))
    assert len(results) == 2
    assert results[0].status == "pass"
    assert results[1].status == "fail"


def test_criteria_missing_is_unknown():
    repo = make_repo()
    results = check_criteria_file(str(repo / "nope.txt"), str(repo))
    assert results[0].status == "unknown"


def test_tests_pass():
    repo = make_repo()
    r = check_tests("true", str(repo))
    assert r.status == "pass", r


def test_tests_fail():
    repo = make_repo()
    r = check_tests("false", str(repo))
    assert r.status == "fail", r


def test_tests_no_command_is_unknown():
    repo = make_repo()
    r = check_tests("", str(repo))
    assert r.status == "unknown"
