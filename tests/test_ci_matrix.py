"""Pins the CI-matrix fixtures' expected exit codes (examples/ci-matrix/).

The agentproof caller workflow (.github/workflows/verify.yml) runs
run-case.sh for both cases and asserts these exact codes — if a fixture
rots, both CI and this suite catch it.
"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "examples" / "ci-matrix" / "run-case.sh"


def _run_case(case):
    env = dict(os.environ)
    env["AGENTPROOF_CMD"] = (
        f"{sys.executable} {ROOT / 'src' / 'agentproof.py'}")
    return subprocess.run(["bash", str(SCRIPT), case],
                          capture_output=True, text=True, env=env)


def test_ci_matrix_pass_case_exits_0():
    p = _run_case("pass")
    assert p.returncode == 0, p.stderr + p.stdout


def test_ci_matrix_fail_case_exits_1():
    p = _run_case("fail")
    assert p.returncode == 1, p.stderr + p.stdout
